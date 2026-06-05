"""
Market Regime Detector
Detects which market regime (bull, bear, sideways, volatile) is currently active
"""

import logging
from typing import Dict, Any
import numpy as np

logger = logging.getLogger(__name__)


class RegimeDetector:
    """
    Detects market regime using multiple data dimensions.
    
    Regimes:
    - Bull: Strong uptrend with positive sentiment
    - Bear: Strong downtrend with negative sentiment
    - Sideways: Range-bound, low volatility
    - Volatile: High volatility, unpredictable
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize regime detector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.weights = config.get('regime_weights', {
            'technical': 0.40,
            'sentiment': 0.30,
            'volatility': 0.30
        })
    
    def detect_regime(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect current market regime.
        
        Args:
            market_data: Market data including price, indicators, sentiment
        
        Returns:
            Dictionary with regime and confidence score
        """
        # Calculate scores for each regime
        scores = {
            'bull': 0.0,
            'bear': 0.0,
            'sideways': 0.0,
            'volatile': 0.0
        }
        
        # Technical analysis component
        technical_scores = self._analyze_technical(market_data)
        for regime, score in technical_scores.items():
            scores[regime] += score * self.weights['technical']
        
        # Sentiment analysis component
        sentiment_scores = self._analyze_sentiment(market_data)
        for regime, score in sentiment_scores.items():
            scores[regime] += score * self.weights['sentiment']
        
        # Volatility analysis component
        volatility_scores = self._analyze_volatility(market_data)
        for regime, score in volatility_scores.items():
            scores[regime] += score * self.weights['volatility']
        
        # Determine regime with highest score
        regime = max(scores, key=scores.get)
        confidence = scores[regime]
        
        logger.debug(f"Regime scores: {scores}")
        logger.info(f"Detected regime: {regime} (confidence: {confidence:.2f})")
        
        return {
            'regime': regime,
            'confidence': confidence,
            'scores': scores
        }
    
    def _analyze_technical(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze technical indicators for regime detection.
        
        Args:
            data: Market data
        
        Returns:
            Scores for each regime
        """
        scores = {'bull': 0.0, 'bear': 0.0, 'sideways': 0.0, 'volatile': 0.0}
        
        price = data.get('price', 0)
        ma_20 = data.get('ma_20', price)
        ma_50 = data.get('ma_50', price)
        rsi = data.get('rsi', 50)
        
        # Price vs Moving Averages
        if price > ma_20 and price > ma_50:
            # Price above both MAs = bullish
            scores['bull'] += 0.4
            if ma_20 > ma_50:
                # Golden cross = very bullish
                scores['bull'] += 0.3
        elif price < ma_20 and price < ma_50:
            # Price below both MAs = bearish
            scores['bear'] += 0.4
            if ma_20 < ma_50:
                # Death cross = very bearish
                scores['bear'] += 0.3
        else:
            # Mixed signals = sideways
            scores['sideways'] += 0.3
        
        # RSI Analysis
        if rsi > 60:
            scores['bull'] += 0.2
        elif rsi < 40:
            scores['bear'] += 0.2
        else:
            scores['sideways'] += 0.2
        
        # Volume trend
        volume_trend = data.get('volume_trend', 'neutral')
        if volume_trend == 'increasing':
            # Increasing volume confirms trend
            if scores['bull'] > scores['bear']:
                scores['bull'] += 0.1
            elif scores['bear'] > scores['bull']:
                scores['bear'] += 0.1
        
        return scores
    
    def _analyze_sentiment(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze sentiment indicators for regime detection.
        
        Args:
            data: Market data with sentiment metrics
        
        Returns:
            Scores for each regime
        """
        scores = {'bull': 0.0, 'bear': 0.0, 'sideways': 0.0, 'volatile': 0.0}
        
        # Fear & Greed Index (0-100)
        fear_greed = data.get('fear_greed', 50)
        
        if fear_greed > 60:
            # Greed = bullish
            scores['bull'] += 0.4
            if fear_greed > 80:
                # Extreme greed = volatile
                scores['volatile'] += 0.2
        elif fear_greed < 40:
            # Fear = bearish
            scores['bear'] += 0.4
            if fear_greed < 20:
                # Extreme fear = volatile
                scores['volatile'] += 0.2
        else:
            # Neutral = sideways
            scores['sideways'] += 0.4
        
        # Social Sentiment (-1 to 1)
        social_sentiment = data.get('social_sentiment', 0)
        
        if social_sentiment > 0.3:
            scores['bull'] += 0.3
        elif social_sentiment < -0.3:
            scores['bear'] += 0.3
        else:
            scores['sideways'] += 0.2
        
        # Funding Rate (derivatives)
        funding_rate = data.get('funding_rate', 0)
        
        if funding_rate > 0.01:
            # Positive funding = longs paying shorts = bullish
            scores['bull'] += 0.3
        elif funding_rate < -0.01:
            # Negative funding = shorts paying longs = bearish
            scores['bear'] += 0.3
        
        return scores
    
    def _analyze_volatility(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze volatility for regime detection.
        
        Args:
            data: Market data with volatility metrics
        
        Returns:
            Scores for each regime
        """
        scores = {'bull': 0.0, 'bear': 0.0, 'sideways': 0.0, 'volatile': 0.0}
        
        # Volatility (0-1 normalized)
        volatility = data.get('volatility', 0.3)
        
        if volatility > 0.6:
            # High volatility
            scores['volatile'] += 0.7
        elif volatility < 0.2:
            # Low volatility
            scores['sideways'] += 0.7
        else:
            # Medium volatility - doesn't strongly indicate regime
            pass
        
        # Bollinger Band Width
        bb_width_percentile = data.get('bb_width_percentile', 50)
        
        if bb_width_percentile > 80:
            # Very wide bands = high volatility
            scores['volatile'] += 0.3
        elif bb_width_percentile < 20:
            # Very narrow bands = low volatility / consolidation
            scores['sideways'] += 0.3
        
        return scores
    
    def get_regime_characteristics(self, regime: str) -> Dict[str, Any]:
        """
        Get characteristics of a specific regime.
        
        Args:
            regime: Regime name
        
        Returns:
            Dictionary with regime characteristics
        """
        characteristics = {
            'bull': {
                'description': 'Strong uptrend with positive sentiment',
                'typical_duration': '2-6 months',
                'risk_level': 'LOW-MEDIUM',
                'strategy': 'Momentum trading with trailing stops',
                'position_size': 'Large (40-50%)'
            },
            'bear': {
                'description': 'Strong downtrend with negative sentiment',
                'typical_duration': '1-4 months',
                'risk_level': 'MEDIUM-HIGH',
                'strategy': 'Short positions or cash preservation',
                'position_size': 'Medium (20-30%)'
            },
            'sideways': {
                'description': 'Range-bound consolidation with low volatility',
                'typical_duration': '1-3 months',
                'risk_level': 'MEDIUM',
                'strategy': 'Mean reversion, buy support sell resistance',
                'position_size': 'Small (15-25%)'
            },
            'volatile': {
                'description': 'High volatility with unpredictable movements',
                'typical_duration': '1-4 weeks',
                'risk_level': 'HIGH',
                'strategy': 'Risk reduction, smaller positions, quick exits',
                'position_size': 'Very small (10-15%)'
            }
        }
        
        return characteristics.get(regime, {})


# Example usage
if __name__ == "__main__":
    config = {
        'regime_weights': {
            'technical': 0.40,
            'sentiment': 0.30,
            'volatility': 0.30
        }
    }
    
    detector = RegimeDetector(config)
    
    # Example: Bull market data
    bull_data = {
        'price': 45000,
        'ma_20': 44000,
        'ma_50': 43000,
        'rsi': 65,
        'fear_greed': 70,
        'social_sentiment': 0.4,
        'funding_rate': 0.02,
        'volatility': 0.3,
        'bb_width_percentile': 45
    }
    
    result = detector.detect_regime(bull_data)
    print(f"Detected: {result['regime']} (confidence: {result['confidence']:.2f})")
    print(f"All scores: {result['scores']}")
    
    # Example: Volatile market data
    volatile_data = {
        'price': 45000,
        'ma_20': 45000,
        'ma_50': 45000,
        'rsi': 50,
        'fear_greed': 85,
        'social_sentiment': 0.0,
        'funding_rate': 0.0,
        'volatility': 0.8,
        'bb_width_percentile': 90
    }
    
    result = detector.detect_regime(volatile_data)
    print(f"\nDetected: {result['regime']} (confidence: {result['confidence']:.2f})")
    print(f"All scores: {result['scores']}")
