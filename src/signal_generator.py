"""
Signal Generator
Generates trading signals based on market regime and analysis
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Generates trading signals appropriate for each market regime.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize signal generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
    
    def generate(self, regime: str, market_data: Dict[str, Any], 
                 analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading signal based on regime.
        
        Args:
            regime: Current market regime
            market_data: Market data dictionary
            analysis: Market analysis results
        
        Returns:
            Trading signal dictionary
        """
        logger.info(f"Generating signal for {regime} regime")
        
        # Route to regime-specific strategy
        if regime == 'bull':
            signal = self._bull_strategy(market_data, analysis)
        elif regime == 'bear':
            signal = self._bear_strategy(market_data, analysis)
        elif regime == 'sideways':
            signal = self._sideways_strategy(market_data, analysis)
        elif regime == 'volatile':
            signal = self._volatile_strategy(market_data, analysis)
        else:
            logger.warning(f"Unknown regime: {regime}. Generating HOLD signal.")
            signal = self._default_signal(market_data)
        
        # Add metadata
        signal['timestamp'] = datetime.now().isoformat()
        signal['regime'] = regime
        signal['symbol'] = market_data.get('symbol', 'Unknown')
        
        return signal
    
    def _bull_strategy(self, data: Dict[str, Any], 
                       analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bull market strategy: Momentum trading.
        
        Entry: RSI crosses 50, MACD bullish, volume confirming
        Exit: RSI > 70 or price drops below MA20
        """
        rsi = data.get('rsi', 50)
        price = data.get('price', 0)
        ma_20 = data.get('ma_20', price)
        volume_trend = data.get('volume_trend', 'neutral')
        fear_greed = data.get('fear_greed', 50)
        
        action = 'HOLD'
        confidence = 0.0
        reasoning = []
        
        # Entry conditions
        buy_signals = 0
        total_signals = 0
        
        # Signal 1: RSI above 50 but not overbought
        if 50 < rsi < 70:
            buy_signals += 1
            reasoning.append(f"RSI at {rsi:.1f} (bullish range)")
        total_signals += 1
        
        # Signal 2: Price above MA20
        if price > ma_20:
            buy_signals += 1
            reasoning.append(f"Price above 20-day MA (${ma_20:.0f})")
        total_signals += 1
        
        # Signal 3: Volume confirming
        if volume_trend == 'increasing':
            buy_signals += 1
            reasoning.append("Volume increasing (trend confirmation)")
        total_signals += 1
        
        # Signal 4: Positive sentiment
        if fear_greed > 55:
            buy_signals += 1
            reasoning.append(f"Fear & Greed at {fear_greed} (greed)")
        total_signals += 1
        
        # Calculate confidence
        confidence = buy_signals / total_signals
        
        # Decision logic
        if confidence >= 0.75:
            # Strong buy signal
            action = 'BUY'
            take_profit_pct = 0.05  # 5%
            stop_loss_pct = 0.03    # 3%
        elif confidence >= 0.50:
            # Moderate buy signal
            action = 'BUY'
            take_profit_pct = 0.03  # 3%
            stop_loss_pct = 0.02    # 2%
        else:
            # Not enough confirmation
            action = 'HOLD'
            take_profit_pct = 0
            stop_loss_pct = 0
            reasoning.append("Insufficient buy signals")
        
        # Exit conditions (if we're already in a position)
        if rsi > 70:
            reasoning.append("RSI overbought - consider taking profit")
        if price < ma_20:
            reasoning.append("Price dropped below MA20 - exit signal")
        
        return {
            'action': action,
            'confidence': confidence,
            'entry_price': price,
            'take_profit': price * (1 + take_profit_pct) if action == 'BUY' else None,
            'stop_loss': price * (1 - stop_loss_pct) if action == 'BUY' else None,
            'position_size': 0.50 if action == 'BUY' else 0,  # 50% max for bull
            'reasoning': '; '.join(reasoning)
        }
    
    def _bear_strategy(self, data: Dict[str, Any], 
                       analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bear market strategy: Capital preservation or short positions.
        
        Entry (short): RSI crosses below 50, MACD bearish
        Exit: RSI < 30 or price rises above MA20
        """
        rsi = data.get('rsi', 50)
        price = data.get('price', 0)
        ma_20 = data.get('ma_20', price)
        fear_greed = data.get('fear_greed', 50)
        
        action = 'HOLD'
        confidence = 0.0
        reasoning = []
        
        # In bear market, prefer cash preservation
        reasoning.append("Bear market detected - capital preservation priority")
        
        # Short entry conditions (optional)
        short_signals = 0
        total_signals = 0
        
        # Signal 1: RSI below 50 but not oversold
        if 30 < rsi < 50:
            short_signals += 1
            reasoning.append(f"RSI at {rsi:.1f} (bearish range)")
        total_signals += 1
        
        # Signal 2: Price below MA20
        if price < ma_20:
            short_signals += 1
            reasoning.append(f"Price below 20-day MA (${ma_20:.0f})")
        total_signals += 1
        
        # Signal 3: Negative sentiment
        if fear_greed < 45:
            short_signals += 1
            reasoning.append(f"Fear & Greed at {fear_greed} (fear)")
        total_signals += 1
        
        confidence = short_signals / total_signals
        
        # In bear market, we're conservative
        # Only take positions with very high confidence
        if confidence >= 0.80:
            action = 'SELL'  # Short position
            take_profit_pct = 0.03  # 3% gain on short
            stop_loss_pct = 0.02    # 2% loss tolerance
        else:
            action = 'HOLD'  # Stay in cash
            take_profit_pct = 0
            stop_loss_pct = 0
            reasoning.append("Staying in cash - insufficient short signal")
        
        return {
            'action': action,
            'confidence': confidence,
            'entry_price': price,
            'take_profit': price * (1 - take_profit_pct) if action == 'SELL' else None,
            'stop_loss': price * (1 + stop_loss_pct) if action == 'SELL' else None,
            'position_size': 0.30 if action == 'SELL' else 0,  # 30% max for bear
            'reasoning': '; '.join(reasoning)
        }
    
    def _sideways_strategy(self, data: Dict[str, Any], 
                           analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sideways market strategy: Mean reversion.
        
        Entry: Price at support (lower BB) + RSI < 40
        Exit: Price at resistance (upper BB) + RSI > 60
        """
        rsi = data.get('rsi', 50)
        price = data.get('price', 0)
        bb_upper = data.get('bb_upper', price * 1.05)
        bb_lower = data.get('bb_lower', price * 0.95)
        bb_middle = data.get('bb_middle', price)
        
        action = 'HOLD'
        confidence = 0.0
        reasoning = []
        
        reasoning.append("Sideways market - mean reversion strategy")
        
        # Check distance to bands
        dist_to_lower = abs(price - bb_lower) / price
        dist_to_upper = abs(price - bb_upper) / price
        
        # Buy at support
        if dist_to_lower < 0.02 and rsi < 40:
            # Near lower band and oversold
            action = 'BUY'
            confidence = 0.70
            reasoning.append(f"Price near support (${bb_lower:.0f}), RSI oversold ({rsi:.1f})")
            take_profit = bb_middle  # Target: middle band
            stop_loss = bb_lower * 0.985  # Stop: just below support
        
        # Sell at resistance
        elif dist_to_upper < 0.02 and rsi > 60:
            # Near upper band and overbought
            action = 'SELL'
            confidence = 0.70
            reasoning.append(f"Price near resistance (${bb_upper:.0f}), RSI overbought ({rsi:.1f})")
            take_profit = bb_middle  # Target: middle band
            stop_loss = bb_upper * 1.015  # Stop: just above resistance
        
        else:
            reasoning.append("Price not at range extremes - waiting")
            take_profit = None
            stop_loss = None
        
        return {
            'action': action,
            'confidence': confidence,
            'entry_price': price,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'position_size': 0.25 if action in ['BUY', 'SELL'] else 0,  # 25% for sideways
            'reasoning': '; '.join(reasoning)
        }
    
    def _volatile_strategy(self, data: Dict[str, Any], 
                           analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Volatile market strategy: Risk reduction.
        
        Prefer staying in cash. Only trade with very strong signals.
        """
        reasoning = [
            "High volatility detected - risk reduction mode",
            "Prefer cash preservation",
            "Only trading with extremely strong signals"
        ]
        
        # In volatile markets, mostly stay out
        # Only enter if ALL signals align perfectly
        rsi = data.get('rsi', 50)
        fear_greed = data.get('fear_greed', 50)
        price = data.get('price', 0)
        
        # Require extreme conditions for entry
        if rsi < 30 and fear_greed < 25:
            # Extreme oversold - contrarian buy
            action = 'BUY'
            confidence = 0.60
            reasoning.append("Extreme oversold conditions - contrarian opportunity")
            take_profit = price * 1.02  # Quick 2% target
            stop_loss = price * 0.99    # Tight 1% stop
        elif rsi > 70 and fear_greed > 75:
            # Extreme overbought - contrarian sell
            action = 'SELL'
            confidence = 0.60
            reasoning.append("Extreme overbought conditions - contrarian opportunity")
            take_profit = price * 0.98  # Quick 2% target
            stop_loss = price * 1.01    # Tight 1% stop
        else:
            action = 'HOLD'
            confidence = 0.0
            take_profit = None
            stop_loss = None
        
        return {
            'action': action,
            'confidence': confidence,
            'entry_price': price,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'position_size': 0.15 if action in ['BUY', 'SELL'] else 0,  # 15% max volatile
            'reasoning': '; '.join(reasoning)
        }
    
    def _default_signal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Default HOLD signal when regime is unknown."""
        return {
            'action': 'HOLD',
            'confidence': 0.0,
            'entry_price': data.get('price', 0),
            'take_profit': None,
            'stop_loss': None,
            'position_size': 0.0,
            'reasoning': 'Unknown market regime - staying in cash'
        }


# Example usage
if __name__ == "__main__":
    config = {}
    generator = SignalGenerator(config)
    
    # Bull market example
    bull_data = {
        'symbol': 'BTC',
        'price': 45000,
        'ma_20': 44000,
        'rsi': 62,
        'volume_trend': 'increasing',
        'fear_greed': 65
    }
    
    analysis = {'risk_level': 'LOW-MEDIUM'}
    
    signal = generator.generate('bull', bull_data, analysis)
    print(f"Bull Signal: {signal['action']} (confidence: {signal['confidence']:.2%})")
    print(f"Reasoning: {signal['reasoning']}\n")
    
    # Sideways market example
    sideways_data = {
        'symbol': 'ETH',
        'price': 3000,
        'bb_upper': 3150,
        'bb_lower': 2950,
        'bb_middle': 3050,
        'rsi': 38
    }
    
    signal = generator.generate('sideways', sideways_data, analysis)
    print(f"Sideways Signal: {signal['action']} (confidence: {signal['confidence']:.2%})")
    print(f"Reasoning: {signal['reasoning']}")
