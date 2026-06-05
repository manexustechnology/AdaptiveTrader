"""
Adaptive Multi-Regime Trading Skill
Main CMC Skill implementation

This module provides the primary interface for the trading skill.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import yaml

from .regime_detector import RegimeDetector
from .signal_generator import SignalGenerator
from .risk_manager import RiskManager
from .cmc_data_fetcher import CMCDataFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdaptiveMultiRegimeSkill:
    """
    Main CMC Skill for adaptive multi-regime trading.
    
    This skill:
    1. Detects current market regime
    2. Generates trading signals based on regime
    3. Manages risk and position sizing
    4. Adapts to changing market conditions
    """
    
    def __init__(self, config_path: str = "config/config.yaml", api_key: Optional[str] = None):
        """
        Initialize the trading skill.
        
        Args:
            config_path: Path to configuration file
            api_key: CoinMarketCap API key (optional, reads from env if not provided)
        """
        logger.info("Initializing Adaptive Multi-Regime Trading Skill")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize CMC Data Fetcher for real API integration
        self.cmc_fetcher = CMCDataFetcher(api_key)
        logger.info("✓ CMC Data Fetcher initialized (REAL API integration)")
        
        # Initialize components
        self.regime_detector = RegimeDetector(self.config)
        self.signal_generator = SignalGenerator(self.config)
        self.risk_manager = RiskManager(self.config)
        
        # State tracking
        self.current_regime = None
        self.portfolio_value = self.config.get('initial_capital', 10000)
        self.positions = {}
        
        logger.info(f"Skill initialized with capital: ${self.portfolio_value}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'initial_capital': 10000,
            'max_position_size': 0.50,
            'max_daily_loss': 0.05,
            'max_drawdown': 0.20,
            'regime_weights': {
                'technical': 0.40,
                'sentiment': 0.30,
                'volatility': 0.30
            },
            'risk_params': {
                'bull': {'max_position': 0.50, 'stop_loss': 0.03},
                'bear': {'max_position': 0.30, 'stop_loss': 0.02},
                'sideways': {'max_position': 0.25, 'stop_loss': 0.015},
                'volatile': {'max_position': 0.15, 'stop_loss': 0.01}
            }
        }
    
    def fetch_live_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch live market data from CoinMarketCap API.
        
        This method uses the REAL CMC API to fetch current market data
        for the specified cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            
        Returns:
            Market data dictionary compatible with analyze_market()
        """
        logger.info(f"Fetching LIVE market data from CMC for {symbol}")
        
        try:
            # Fetch comprehensive market data from CMC
            market_data = self.cmc_fetcher.get_market_data_for_strategy(symbol)
            
            logger.info(f"✓ LIVE data fetched: {symbol} @ ${market_data['price']:,.2f}")
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to fetch live CMC data: {e}")
            logger.warning("Falling back to demo mode. Set CMC_API_KEY to use real data.")
            raise
    
    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze current market conditions and detect regime.
        
        Args:
            market_data: Dictionary containing all market data from CMC
                - price: current price
                - volume: 24h volume
                - ohlcv: OHLCV data
                - fear_greed: Fear & Greed Index
                - social_metrics: social volume, sentiment
                - derivatives: funding rate, open interest
                - on_chain: transaction volume, active addresses
        
        Returns:
            Analysis results including regime and market metrics
        """
        logger.info(f"Analyzing market for {market_data.get('symbol', 'Unknown')}")
        
        # Detect market regime
        regime_analysis = self.regime_detector.detect_regime(market_data)
        self.current_regime = regime_analysis['regime']
        
        # Calculate technical indicators
        technical_analysis = self._analyze_technical(market_data)
        
        # Analyze sentiment
        sentiment_analysis = self._analyze_sentiment(market_data)
        
        # Combine all analyses
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'symbol': market_data.get('symbol', 'Unknown'),
            'current_price': market_data.get('price'),
            'regime': self.current_regime,
            'regime_confidence': regime_analysis['confidence'],
            'technical': technical_analysis,
            'sentiment': sentiment_analysis,
            'risk_level': self._assess_risk(regime_analysis, market_data)
        }
        
        logger.info(f"Market regime detected: {self.current_regime} (confidence: {regime_analysis['confidence']:.2f})")
        
        return analysis
    
    def generate_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading signal based on market analysis.
        
        Args:
            market_data: Market data dictionary
        
        Returns:
            Trading signal with action, confidence, and trade parameters
        """
        # First analyze the market
        analysis = self.analyze_market(market_data)
        
        # Generate signal based on regime
        signal = self.signal_generator.generate(
            regime=self.current_regime,
            market_data=market_data,
            analysis=analysis
        )
        
        # Apply risk management
        signal = self.risk_manager.apply_risk_rules(
            signal=signal,
            portfolio_value=self.portfolio_value,
            current_positions=self.positions,
            regime=self.current_regime
        )
        
        logger.info(f"Signal generated: {signal['action']} with confidence {signal['confidence']:.2f}")
        
        return signal
    
    def generate_signal_live(self, symbol: str) -> Dict[str, Any]:
        """
        Convenience method: Fetch live data and generate signal in one call.
        
        This method fetches real-time data from CMC API and immediately
        generates a trading signal.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            
        Returns:
            Trading signal with action, confidence, and trade parameters
        """
        logger.info(f"Generating LIVE signal for {symbol}")
        
        # Fetch live market data from CMC
        market_data = self.fetch_live_market_data(symbol)
        
        # Generate signal based on live data
        signal = self.generate_signal(market_data)
        
        return signal
    
    def _analyze_technical(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical indicators."""
        return {
            'rsi': market_data.get('rsi', 50),
            'macd': market_data.get('macd', {}),
            'bollinger_bands': market_data.get('bb', {}),
            'moving_averages': {
                'ma_20': market_data.get('ma_20'),
                'ma_50': market_data.get('ma_50')
            },
            'volume_trend': market_data.get('volume_trend', 'neutral')
        }
    
    def _analyze_sentiment(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment indicators."""
        return {
            'fear_greed': market_data.get('fear_greed', 50),
            'social_sentiment': market_data.get('social_sentiment', 0),
            'social_volume': market_data.get('social_volume', 0),
            'funding_rate': market_data.get('funding_rate', 0),
            'on_chain_flow': market_data.get('on_chain_flow', 0)
        }
    
    def _assess_risk(self, regime_analysis: Dict, market_data: Dict) -> str:
        """Assess overall risk level."""
        confidence = regime_analysis['confidence']
        regime = regime_analysis['regime']
        volatility = market_data.get('volatility', 0)
        
        if regime == 'volatile' or volatility > 0.8:
            return 'HIGH'
        elif regime == 'bear' or confidence < 0.5:
            return 'MEDIUM-HIGH'
        elif regime == 'sideways':
            return 'MEDIUM'
        else:
            return 'LOW-MEDIUM'
    
    def update_portfolio(self, position_update: Dict[str, Any]) -> None:
        """
        Update portfolio state after trade execution.
        
        Args:
            position_update: Dictionary with trade execution details
        """
        symbol = position_update['symbol']
        action = position_update['action']
        
        if action == 'BUY':
            self.positions[symbol] = position_update
            self.portfolio_value -= position_update['cost']
            logger.info(f"Position opened: {symbol} at {position_update['price']}")
        elif action == 'SELL':
            if symbol in self.positions:
                self.portfolio_value += position_update['proceeds']
                del self.positions[symbol]
                logger.info(f"Position closed: {symbol} at {position_update['price']}")
    
    def get_portfolio_status(self) -> Dict[str, Any]:
        """Get current portfolio status."""
        return {
            'portfolio_value': self.portfolio_value,
            'positions': self.positions,
            'current_regime': self.current_regime,
            'available_capital': self.portfolio_value - sum(
                pos.get('cost', 0) for pos in self.positions.values()
            )
        }


def create_skill(config_path: str = "config/config.yaml") -> AdaptiveMultiRegimeSkill:
    """
    Factory function to create a skill instance.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Initialized skill instance
    """
    return AdaptiveMultiRegimeSkill(config_path)


# Example usage
if __name__ == "__main__":
    # Create skill
    skill = create_skill()
    
    # Example market data (would come from CMC in production)
    sample_market_data = {
        'symbol': 'BTC',
        'price': 45000,
        'volume': 25000000000,
        'rsi': 62,
        'ma_20': 44000,
        'ma_50': 43000,
        'fear_greed': 65,
        'social_sentiment': 0.35,
        'funding_rate': 0.015,
        'volatility': 0.35
    }
    
    # Analyze market
    analysis = skill.analyze_market(sample_market_data)
    print(f"\nMarket Analysis:")
    print(f"Regime: {analysis['regime']}")
    print(f"Risk Level: {analysis['risk_level']}")
    
    # Generate signal
    signal = skill.generate_signal(sample_market_data)
    print(f"\nTrading Signal:")
    print(f"Action: {signal['action']}")
    print(f"Confidence: {signal['confidence']:.2%}")
    if signal['action'] != 'HOLD':
        print(f"Position Size: {signal['position_size']:.2%}")
        print(f"Stop Loss: {signal['stop_loss']}")
        print(f"Take Profit: {signal['take_profit']}")
