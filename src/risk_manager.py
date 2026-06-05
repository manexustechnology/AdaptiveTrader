"""
Risk Manager
Manages risk and position sizing for trading signals
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Applies risk management rules to trading signals.
    
    Responsibilities:
    - Position sizing based on regime and capital
    - Stop loss and take profit validation
    - Daily loss limits
    - Maximum drawdown protection
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize risk manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.max_daily_loss = config.get('max_daily_loss', 0.05)  # 5%
        self.max_drawdown = config.get('max_drawdown', 0.20)       # 20%
        self.risk_params = config.get('risk_params', {})
        
        # Track daily performance
        self.daily_pnl = 0.0
        self.peak_portfolio_value = 0.0
        self.current_drawdown = 0.0
    
    def apply_risk_rules(self, signal: Dict[str, Any], portfolio_value: float,
                         current_positions: Dict[str, Any], regime: str) -> Dict[str, Any]:
        """
        Apply risk management rules to a trading signal.
        
        Args:
            signal: Trading signal from generator
            portfolio_value: Current portfolio value
            current_positions: Dictionary of current positions
            regime: Current market regime
        
        Returns:
            Modified signal with risk rules applied
        """
        # Update peak value for drawdown calculation
        if portfolio_value > self.peak_portfolio_value:
            self.peak_portfolio_value = portfolio_value
        
        # Calculate current drawdown
        self.current_drawdown = (self.peak_portfolio_value - portfolio_value) / self.peak_portfolio_value
        
        # Check circuit breakers
        if self._check_circuit_breakers(portfolio_value):
            logger.warning("Circuit breaker triggered - forcing HOLD")
            signal['action'] = 'HOLD'
            signal['reasoning'] += '; Circuit breaker: max loss limit reached'
            return signal
        
        # Adjust position size
        signal = self._adjust_position_size(signal, portfolio_value, regime)
        
        # Validate stop loss and take profit
        signal = self._validate_stops(signal, regime)
        
        # Add risk metrics
        signal['risk_metrics'] = {
            'current_drawdown': f"{self.current_drawdown:.2%}",
            'daily_pnl_pct': f"{self.daily_pnl / portfolio_value:.2%}" if portfolio_value > 0 else "0%",
            'position_size_pct': f"{signal['position_size']:.2%}"
        }
        
        return signal
    
    def _check_circuit_breakers(self, portfolio_value: float) -> bool:
        """
        Check if any circuit breakers should halt trading.
        
        Args:
            portfolio_value: Current portfolio value
        
        Returns:
            True if trading should be halted
        """
        # Check daily loss limit
        if portfolio_value > 0:
            daily_loss_pct = abs(self.daily_pnl) / portfolio_value
            if daily_loss_pct >= self.max_daily_loss:
                logger.error(f"Daily loss limit reached: {daily_loss_pct:.2%}")
                return True
        
        # Check maximum drawdown
        if self.current_drawdown >= self.max_drawdown:
            logger.error(f"Maximum drawdown reached: {self.current_drawdown:.2%}")
            return True
        
        return False
    
    def _adjust_position_size(self, signal: Dict[str, Any], 
                              portfolio_value: float, regime: str) -> Dict[str, Any]:
        """
        Adjust position size based on risk parameters and regime.
        
        Args:
            signal: Trading signal
            portfolio_value: Current portfolio value
            regime: Current market regime
        
        Returns:
            Signal with adjusted position size
        """
        if signal['action'] == 'HOLD':
            return signal
        
        # Get regime-specific limits
        regime_params = self.risk_params.get(regime, {
            'max_position': 0.25,
            'stop_loss': 0.02
        })
        
        max_position = regime_params['max_position']
        
        # Start with signal's position size
        position_size = signal.get('position_size', 0)
        
        # Cap at regime maximum
        position_size = min(position_size, max_position)
        
        # Adjust based on confidence
        confidence = signal.get('confidence', 0.5)
        position_size *= confidence
        
        # Adjust based on current drawdown (reduce size in drawdown)
        if self.current_drawdown > 0.10:  # 10% drawdown
            drawdown_factor = 1 - (self.current_drawdown / self.max_drawdown)
            position_size *= max(drawdown_factor, 0.5)  # Reduce by up to 50%
            logger.info(f"Position size reduced due to drawdown: {self.current_drawdown:.2%}")
        
        # Ensure we don't exceed available capital
        position_size = min(position_size, 0.95)  # Never use more than 95%
        
        signal['position_size'] = position_size
        logger.info(f"Adjusted position size: {position_size:.2%} for {regime} regime")
        
        return signal
    
    def _validate_stops(self, signal: Dict[str, Any], regime: str) -> Dict[str, Any]:
        """
        Validate and adjust stop loss and take profit levels.
        
        Args:
            signal: Trading signal
            regime: Current market regime
        
        Returns:
            Signal with validated stops
        """
        if signal['action'] == 'HOLD':
            return signal
        
        entry_price = signal.get('entry_price', 0)
        if entry_price == 0:
            return signal
        
        # Get regime-specific stop loss
        regime_params = self.risk_params.get(regime, {'stop_loss': 0.02})
        max_stop_loss_pct = regime_params['stop_loss']
        
        # Validate stop loss
        stop_loss = signal.get('stop_loss')
        if stop_loss:
            if signal['action'] == 'BUY':
                stop_loss_pct = (entry_price - stop_loss) / entry_price
                if stop_loss_pct > max_stop_loss_pct:
                    # Stop too wide - tighten it
                    signal['stop_loss'] = entry_price * (1 - max_stop_loss_pct)
                    logger.warning(f"Stop loss tightened to {max_stop_loss_pct:.2%}")
            elif signal['action'] == 'SELL':
                stop_loss_pct = (stop_loss - entry_price) / entry_price
                if stop_loss_pct > max_stop_loss_pct:
                    # Stop too wide - tighten it
                    signal['stop_loss'] = entry_price * (1 + max_stop_loss_pct)
                    logger.warning(f"Stop loss tightened to {max_stop_loss_pct:.2%}")
        else:
            # No stop loss set - add one
            if signal['action'] == 'BUY':
                signal['stop_loss'] = entry_price * (1 - max_stop_loss_pct)
            elif signal['action'] == 'SELL':
                signal['stop_loss'] = entry_price * (1 + max_stop_loss_pct)
            logger.info(f"Stop loss added: {max_stop_loss_pct:.2%}")
        
        return signal
