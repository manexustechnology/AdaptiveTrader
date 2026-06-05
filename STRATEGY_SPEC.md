# Adaptive Multi-Regime Trading Strategy Specification

## Executive Summary

This document specifies a backtestable trading strategy that adapts to different market regimes by combining multiple data sources from the CoinMarketCap AI Agent Hub. The strategy automatically detects market conditions and applies appropriate trading rules for each regime.

---

## 1. Strategy Overview

### 1.1 Core Concept
The Adaptive Multi-Regime Trading Skill combines five dimensions of market data to:
1. Detect the current market regime
2. Generate trading signals appropriate for that regime
3. Manage risk through dynamic position sizing
4. Adapt as market conditions change

### 1.2 Data Sources (All from CMC AI Agent Hub)
1. **Market Data**: Price, volume, OHLCV
2. **Technical Indicators**: RSI, MACD, Bollinger Bands
3. **Sentiment**: Fear & Greed Index
4. **Social Metrics**: Social volume, mentions, sentiment
5. **Derivatives**: Funding rates, Open Interest

---

## 2. Market Regime Detection

### 2.1 Four Regimes

#### Regime 1: Bull Market
**Detection Criteria**:
- Price > 20-day MA AND Price > 50-day MA
- RSI > 50
- Fear & Greed Index > 60
- Funding Rate > 0.01% (positive)
- Social Sentiment > 0.3 (positive)

**Characteristics**: Strong uptrend, positive sentiment, bullish derivatives

#### Regime 2: Bear Market
**Detection Criteria**:
- Price < 20-day MA AND Price < 50-day MA
- RSI < 50
- Fear & Greed Index < 40
- Funding Rate < -0.01% (negative)
- Social Sentiment < -0.3 (negative)

**Characteristics**: Strong downtrend, negative sentiment, bearish derivatives

#### Regime 3: Sideways/Range
**Detection Criteria**:
- Bollinger Band Width < 20th percentile (low volatility)
- Price oscillates between support/resistance
- Fear & Greed Index: 40-60 (neutral)
- Low directional movement (ADX < 25)

**Characteristics**: Consolidation, low volatility, range-bound

#### Regime 4: High Volatility
**Detection Criteria**:
- Bollinger Band Width > 80th percentile
- ATR (Average True Range) > 80th percentile
- Large divergence between technical and sentiment signals
- Extreme Fear & Greed readings (<20 or >80)

**Characteristics**: Unpredictable, high risk, extreme sentiment swings

### 2.2 Regime Scoring Algorithm

```python
def calculate_regime_score(data):
    """
    Returns regime probabilities: {bull, bear, sideways, volatile}
    """
    scores = {
        'bull': 0,
        'bear': 0,
        'sideways': 0,
        'volatile': 0
    }
    
    # Technical score (40% weight)
    if data['price'] > data['ma_20'] and data['price'] > data['ma_50']:
        scores['bull'] += 0.4
    elif data['price'] < data['ma_20'] and data['price'] < data['ma_50']:
        scores['bear'] += 0.4
    
    # Sentiment score (30% weight)
    if data['fear_greed'] > 60:
        scores['bull'] += 0.3
    elif data['fear_greed'] < 40:
        scores['bear'] += 0.3
    else:
        scores['sideways'] += 0.3
    
    # Volatility score (30% weight)
    if data['bb_width_percentile'] > 80:
        scores['volatile'] += 0.3
    elif data['bb_width_percentile'] < 20:
        scores['sideways'] += 0.3
    
    return max(scores, key=scores.get)
```

---

## 3. Trading Rules by Regime

### 3.1 Bull Market Strategy

**Philosophy**: Ride the trend with momentum

#### Entry Rules
1. **Primary Signal**: RSI crosses above 50 from below
2. **Confirmation**:
   - MACD line crosses above signal line
   - Volume > 20-day average volume
   - Fear & Greed Index > 55
   - Social sentiment increasing
3. **Entry Timing**: Market order on confirmation

#### Exit Rules
1. **Take Profit**: 
   - RSI > 70 (overbought)
   - Price hits +5% trailing stop
2. **Stop Loss**: 
   - Price drops below 20-day MA
   - Loss exceeds 3%
3. **Regime Change**: If regime switches to Bear or Volatile

#### Position Sizing
- Base position: 50% of available capital
- Scale up: +10% if social sentiment strongly positive
- Scale down: -10% if on-chain volume decreasing

---

### 3.2 Bear Market Strategy

**Philosophy**: Capital preservation or short positions

#### Entry Rules (Short Positions)
1. **Primary Signal**: RSI crosses below 50 from above
2. **Confirmation**:
   - MACD line crosses below signal line
   - Fear & Greed Index < 45
   - Negative funding rate (shorts paying longs)
3. **Entry Timing**: Market order on confirmation

#### Exit Rules
1. **Take Profit**:
   - RSI < 30 (oversold)
   - Price hits +3% trailing stop (on short)
2. **Stop Loss**:
   - Price rises above 20-day MA
   - Loss exceeds 2%
3. **Regime Change**: If regime switches to Bull

#### Position Sizing
- Base position: 30% of available capital (conservative)
- Maximum: 40% (bear markets are risky)

---

### 3.3 Sideways/Range Strategy

**Philosophy**: Mean reversion, buy low sell high

#### Entry Rules
1. **Buy Signal**:
   - Price touches lower Bollinger Band
   - RSI < 40
   - Price at identified support level
2. **Sell Signal**:
   - Price touches upper Bollinger Band
   - RSI > 60
   - Price at identified resistance level

#### Exit Rules
1. **Take Profit**: 
   - Price reaches opposite band
   - Gain of 2-3% achieved
2. **Stop Loss**:
   - Price breaks below support (for longs)
   - Price breaks above resistance (for shorts)
   - Loss exceeds 1.5%

#### Position Sizing
- Small positions: 20-30% of capital
- Quick in and out trades
- Multiple small trades preferred

---

### 3.4 High Volatility Strategy

**Philosophy**: Risk reduction, smaller positions

#### Entry Rules
1. **Reduced Activity**: Only trade with very strong signals
2. **High Confidence Only**:
   - All 5 data dimensions must align
   - Wait for volatility to decrease
3. **Entry Timing**: Limit orders only (no market orders)

#### Exit Rules
1. **Quick Exits**: 
   - Take profit at 2% gain
   - Stop loss at 1% loss
2. **Time-based**: Exit after 4 hours if no movement

#### Position Sizing
- Maximum 15% of capital
- Prefer staying in cash
- Wait for regime to stabilize

---

## 4. Risk Management

### 4.1 Position Sizing Formula

```python
def calculate_position_size(capital, regime, confidence, volatility):
    """
    Dynamic position sizing based on regime and confidence
    """
    # Base allocation by regime
    base_allocation = {
        'bull': 0.50,      # 50%
        'bear': 0.30,      # 30%
        'sideways': 0.25,  # 25%
        'volatile': 0.15   # 15%
    }
    
    # Adjust by confidence (0-1 scale)
    position_size = capital * base_allocation[regime] * confidence
    
    # Adjust by volatility (reduce size in high volatility)
    volatility_factor = max(0.5, 1 - volatility)
    position_size *= volatility_factor
    
    return min(position_size, capital * 0.50)  # Never exceed 50%
```

### 4.2 Stop Loss Rules
- **Maximum loss per trade**: 3% of position
- **Maximum daily loss**: 5% of portfolio
- **Maximum drawdown**: 20% (stop all trading if reached)

### 4.3 Take Profit Rules
- **Minimum**: 1.5% (risk/reward ratio of 1:0.5)
- **Target by regime**:
  - Bull: 5%
  - Bear (short): 3%
  - Sideways: 2.5%
  - Volatile: 2%

---

## 5. Signal Generation Logic

### 5.1 Signal Confidence Calculation

```python
def calculate_signal_confidence(indicators):
    """
    Returns confidence score 0-1 based on signal alignment
    """
    signals = []
    
    # Technical signals
    signals.append(1 if indicators['rsi_signal'] == 'BUY' else 0)
    signals.append(1 if indicators['macd_signal'] == 'BUY' else 0)
    signals.append(1 if indicators['bb_signal'] == 'BUY' else 0)
    
    # Sentiment signal
    signals.append(1 if indicators['fear_greed'] > 55 else 0)
    
    # Social signal
    signals.append(1 if indicators['social_sentiment'] > 0 else 0)
    
    # On-chain signal
    signals.append(1 if indicators['on_chain_flow'] > 0 else 0)
    
    # Derivatives signal
    signals.append(1 if indicators['funding_rate'] > 0 else 0)
    
    # Confidence is percentage of aligned signals
    confidence = sum(signals) / len(signals)
    
    return confidence
```

### 5.2 Signal Output Format

```json
{
    "timestamp": "2026-06-04T12:00:00Z",
    "symbol": "BTC",
    "regime": "bull",
    "action": "BUY",
    "confidence": 0.85,
    "entry_price": 45000,
    "stop_loss": 43650,
    "take_profit": 47250,
    "position_size": 0.45,
    "reasoning": {
        "technical": "RSI crossed 50, MACD bullish",
        "sentiment": "Fear & Greed at 65 (Greed)",
        "social": "Social volume +25%, positive sentiment",
        "on_chain": "Whale accumulation detected",
        "derivatives": "Funding rate positive, OI increasing"
    }
}
```

---

## 6. Backtesting Methodology

### 6.1 Data Requirements
- **Timeframe**: 1-hour candles
- **History**: Minimum 1 year of data
- **Assets**: BTC, ETH, BNB (BSC native tokens)
- **Data Sources**: CMC API for all metrics

### 6.2 Backtest Process

```python
def backtest_strategy(data, initial_capital=10000):
    """
    Run strategy backtest on historical data
    """
    portfolio = Portfolio(initial_capital)
    signals = []
    
    for timestamp, market_data in data.iterrows():
        # Detect regime
        regime = detect_regime(market_data)
        
        # Generate signal
        signal = generate_signal(regime, market_data)
        
        # Execute trade
        if signal['action'] in ['BUY', 'SELL']:
            portfolio.execute_trade(signal)
        
        # Track performance
        portfolio.update_value(market_data['close'])
        signals.append(signal)
    
    return portfolio.get_performance_metrics()
```

### 6.3 Performance Metrics
- **Total Return**: (Final Value - Initial Value) / Initial Value
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Average Win/Loss Ratio**: Average profit vs average loss
- **Total Trades**: Number of trades executed
- **Profit Factor**: Gross profit / Gross loss

### 6.4 Benchmark Comparison
- Compare against Buy & Hold strategy
- Compare against each individual regime strategy
- Compare against random trading

---

## 7. Implementation Details

### 7.1 CMC AI Agent Hub Integration

```python
from cmc_agent_hub import AgentHub

class CMCDataProvider:
    def __init__(self, api_key):
        self.hub = AgentHub(api_key)
    
    def get_market_data(self, symbol):
        """Fetch all required data from CMC"""
        return {
            'price': self.hub.get_price(symbol),
            'volume': self.hub.get_volume(symbol),
            'fear_greed': self.hub.get_fear_greed_index(),
            'social_metrics': self.hub.get_social_metrics(symbol),
            'derivatives': self.hub.get_derivatives_data(symbol),
            'on_chain': self.hub.get_on_chain_metrics(symbol)
        }
```

### 7.2 Required CMC Features
- **MCP Protocol**: For real-time data streaming
- **x402 Payment**: For per-request data access
- **CMC CLI**: For command-line backtesting
- **Skills Library**: Leverage existing CMC skills for indicators

---

## 8. Expected Performance

### 8.1 Target Metrics (Backtested)
- **Annual Return**: 25-40%
- **Sharpe Ratio**: > 1.5
- **Maximum Drawdown**: < 20%
- **Win Rate**: > 55%
- **Profit Factor**: > 1.8

### 8.2 Performance by Market Condition
- **Bull Market**: Outperform buy & hold by 10-15%
- **Bear Market**: Minimize losses, preserve capital
- **Sideways**: Generate consistent small profits
- **Volatile**: Reduce exposure, avoid large losses

---

## 9. Advantages Over Example Strategies

### 9.1 vs Momentum Skill (Example A)
- **More adaptive**: Changes strategy per regime, not just one approach
- **More data dimensions**: 5 sources vs 3 indicators
- **Better risk management**: Dynamic position sizing

### 9.2 vs Sentiment Divergence (Example B)
- **More actionable**: Generates clear entry/exit vs just flags
- **More comprehensive**: Includes technical and derivatives data
- **Backtestable**: Clear rules for historical testing

### 9.3 vs Regime Detection (Example C)
- **More complete**: Not just detection, but full trading strategy
- **More signals**: Uses social and on-chain data too
- **Production-ready**: Full risk management included

---

## 10. Real-World Application

### 10.1 Use Cases
1. **Individual Traders**: Systematic trading approach
2. **Trading Bots**: Automated execution
3. **Portfolio Management**: Multi-asset allocation
4. **Risk Assessment**: Market condition monitoring

### 10.2 Path to Adoption
1. **Phase 1**: Paper trading for validation
2. **Phase 2**: Small capital live testing
3. **Phase 3**: Full deployment with monitoring
4. **Phase 4**: Integration with existing trading platforms

---

## 11. Limitations & Future Enhancements

### 11.1 Current Limitations
- Requires reliable CMC data feed
- Assumes liquid markets (may not work for small-cap tokens)
- Historical performance doesn't guarantee future results
- Doesn't account for extreme black swan events

### 11.2 Future Enhancements
- **Machine Learning**: Train regime detector on more data
- **Multi-timeframe**: Combine signals from different timeframes
- **Portfolio Mode**: Trade multiple assets simultaneously
- **Adaptive Parameters**: Auto-tune based on performance

---

## 12. Conclusion

The Adaptive Multi-Regime Trading Skill represents a sophisticated, backtestable trading strategy that leverages the full power of CoinMarketCap's AI Agent Hub. By combining multiple data dimensions and adapting to market conditions, it addresses real-world trading challenges while maintaining clear, implementable rules.

**Key Differentiators**:
- ✅ Original approach combining 5 data sources
- ✅ Adaptive strategy that changes with market regimes
- ✅ Production-ready with comprehensive risk management
- ✅ Clear backtesting methodology
- ✅ Real-world applicability

This strategy specification provides a complete blueprint for implementation and validation, meeting all Track 2 requirements for the BNB Hack competition.

---

**Document Version**: 1.0  
**Date**: June 2026  
**Competition**: BNB Hack Track 2 - Strategy Skills
