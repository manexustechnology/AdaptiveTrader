# Adaptive Multi-Regime Trading Skill

BNB Hackathon Track 2 submission - Strategy Skills category

## What is this?

A trading strategy that automatically detects what kind of market we're in (bull, bear, sideways, or volatile) and switches its approach accordingly. Most strategies work great in one market condition but fail in others - this one adapts.

The strategy uses CoinMarketCap API to pull real market data and combines multiple indicators:
- Technical: RSI, MACD, Bollinger Bands
- Sentiment: Fear & Greed Index  
- Derivatives: funding rates, open interest
- Social metrics from CMC

Based on current regime, it picks the right strategy:
- Bull market → momentum trading
- Bear market → capital preservation
- Sideways → mean reversion
- High volatility → risk reduction

## Installation

```bash
git clone https://github.com/manexustechnology/AdaptiveTrader.git
cd AdaptiveTrader
pip install -r requirements.txt
```

You'll need a CoinMarketCap API key (free tier works). Get one at https://pro.coinmarketcap.com/signup

Set it in config/config.yaml or as environment variable:
```bash
export CMC_API_KEY="your-key-here"
```

## Quick Start

```python
from src.cmc_skill import AdaptiveMultiRegimeSkill

skill = AdaptiveMultiRegimeSkill()
signal = skill.generate_signal_live('BTC')

print(f"Regime: {signal['regime']}")
print(f"Action: {signal['action']}")  # BUY, SELL, HOLD
print(f"Confidence: {signal['confidence']:.2%}")
print(f"Position Size: {signal['position_size']:.2%}")
print(f"Entry Price: ${signal['entry_price']:,.2f}")
```

### Run Examples
```bash
# Run REAL CMC API integration examples
python examples/real_cmc_integration.py

# Quick API test
python test_cmc_api.py
```

## 📈 Strategy Specification

See [STRATEGY_SPEC.md](STRATEGY_SPEC.md) for detailed:
- Entry rules for each regime
- Exit rules and stop loss logic
- Position sizing methodology
- Risk management parameters
- Backtesting methodology

## 🎬 Demo

See [docs/DEMO.md](docs/DEMO.md) for:
- Live demo instructions
- Video walkthrough
- Example outputs

## 🏆 Why This Strategy Wins

1. **Originality**: Novel combination of regime detection with multi-signal analysis
2. **Technical Excellence**: Production-ready code with proper architecture
3. **Real-world Relevance**: Addresses actual crypto trading challenges
4. **Clear Demo**: Easy to understand and reproduce

## 📋 Submission Checklist

- [x] CMC Skill implementation
- [x] Strategy specification document
- [x] Backtestable code
- [x] Public repository
- [x] Clear documentation
- [x] Demo instructions

## 🔗 Resources

- **CoinMarketCap AI Agent Hub**: https://coinmarketcap.com/api/agent
- **BNB Hack Telegram**: https://t.me/+MhiOLT0YUnlmNWFk
- **Competition Details**: See [../hackatonbnb1.md](../hackatonbnb1.md)

## 📝 License


print(f"Action: {signal['action']}")
print(f"Confidence: {signal['confidence']:.1%}")
```

## Project Structure

```
src/
  cmc_skill.py           - main skill class
  cmc_data_fetcher.py    - CMC API integration
  regime_detector.py     - market regime detection
  signal_generator.py    - signal generation per regime
  risk_manager.py        - risk management

config/config.yaml       - strategy parameters
examples/                - usage examples
test_cmc_api.py         - API integration tests
STRATEGY_SPEC.md        - full strategy documentation
```

## Strategy Details

See STRATEGY_SPEC.md for complete backtestable specification including:
- Regime detection criteria
- Entry/exit rules for each regime
- Risk management formulas
- Position sizing logic

## Testing

Run the test suite:
```bash
python test_cmc_api.py
```

Tests real CMC API integration with live market data.

## License

MIT

## Disclaimer

This is a trading strategy for educational/competition purposes. Not financial advice.
