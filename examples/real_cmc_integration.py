#!/usr/bin/env python3
"""
Real CMC Integration Example
Demonstrates ACTUAL CoinMarketCap API integration

This example shows how to use the Adaptive Multi-Regime Trading Skill
with REAL data from the CoinMarketCap API (not mock data).

Requirements:
1. Get API key from https://pro.coinmarketcap.com/signup (free plan available)
2. Set environment variable: export CMC_API_KEY='your-key-here'
3. Run this script: python examples/real_cmc_integration.py
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cmc_skill import AdaptiveMultiRegimeSkill
from src.cmc_data_fetcher import CMCDataFetcher


def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def check_api_key():
    """Check if CMC API key is set."""
    api_key = os.environ.get('CMC_API_KEY')
    if not api_key:
        print("⚠️  WARNING: CMC_API_KEY environment variable not set!")
        print("\nTo get real data from CoinMarketCap:")
        print("1. Sign up at: https://pro.coinmarketcap.com/signup")
        print("2. Get your free API key from the dashboard")
        print("3. Set environment variable:")
        print("   export CMC_API_KEY='your-key-here'")
        print("\n❌ Exiting: Cannot run without API key\n")
        return False
    else:
        print(f"✓ CMC API key found: {api_key[:8]}...{api_key[-4:]}")
        return True


def example_1_fetch_live_data():
    """Example 1: Fetch live market data from CMC."""
    print_header("Example 1: Fetch Live Market Data from CMC")
    
    fetcher = CMCDataFetcher()
    
    # Fetch BTC data
    print("Fetching live BTC data from CoinMarketCap API...\n")
    btc_data = fetcher.get_market_data_for_strategy('BTC')
    
    print("✓ Live Data Fetched:")
    print(f"  Symbol: {btc_data['symbol']}")
    print(f"  Name: {btc_data['name']}")
    print(f"  Price: ${btc_data['price']:,.2f}")
    print(f"  24h Volume: ${btc_data['volume_24h']:,.0f}")
    print(f"  Market Cap: ${btc_data['market_cap']:,.0f}")
    print(f"  24h Change: {btc_data['percent_change_24h']:+.2f}%")
    print(f"  7d Change: {btc_data['percent_change_7d']:+.2f}%")
    print(f"  RSI: {btc_data['rsi']:.2f}")
    print(f"  Volatility: {btc_data['volatility']:.2f}%")
    print(f"  BTC Dominance: {btc_data['btc_dominance']:.2f}%")
    print(f"  Data Source: {btc_data['data_source']}")
    print(f"  Last Updated: {btc_data['last_updated']}")
    
    return btc_data


def example_2_generate_signal_with_live_data():
    """Example 2: Generate trading signal using live CMC data."""
    print_header("Example 2: Generate Trading Signal with Live CMC Data")
    
    skill = AdaptiveMultiRegimeSkill()
    
    print("Generating signal for BTC using LIVE CMC data...\n")
    
    # Use the convenience method that fetches and analyzes in one call
    signal = skill.generate_signal_live('BTC')
    
    print("✓ Signal Generated:")
    print(f"  Action: {signal['action']}")
    print(f"  Confidence: {signal['confidence']:.2%}")
    print(f"  Entry Price: ${signal.get('entry_price', 0) or 0:,.2f}")
    
    if signal.get('stop_loss'):
        print(f"  Stop Loss: ${signal['stop_loss']:,.2f}")
    if signal.get('take_profit'):
        print(f"  Take Profit: ${signal['take_profit']:,.2f}")
    if signal.get('position_size'):
        print(f"  Position Size: {signal['position_size']:.2%}")
    
    print(f"  Regime: {signal.get('regime', 'unknown')}")
    print(f"\n  Reasoning: {signal.get('reasoning', 'N/A')}")
    
    return signal


def example_3_compare_multiple_coins():
    """Example 3: Compare multiple cryptocurrencies."""
    print_header("Example 3: Compare Multiple Cryptocurrencies")
    
    skill = AdaptiveMultiRegimeSkill()
    symbols = ['BTC', 'ETH', 'BNB']
    
    print("Fetching live data and generating signals for multiple coins...\n")
    
    results = []
    for symbol in symbols:
        try:
            print(f"Processing {symbol}...")
            signal = skill.generate_signal_live(symbol)
            results.append({
                'symbol': symbol,
                'action': signal['action'],
                'confidence': signal['confidence'],
                'regime': signal.get('regime', 'unknown'),
                'price': signal.get('entry_price', 0)
            })
            print(f"  ✓ {symbol}: {signal['action']} ({signal['confidence']:.1%} confidence)\n")
        except Exception as e:
            print(f"  ✗ Failed to process {symbol}: {e}\n")
    
    # Summary table
    print("\n" + "-" * 80)
    print(f"{'Symbol':<10} {'Price':<15} {'Action':<10} {'Confidence':<12} {'Regime':<12}")
    print("-" * 80)
    for r in results:
        print(f"{r['symbol']:<10} ${r['price']:<14,.2f} {r['action']:<10} {r['confidence']:<11.1%} {r['regime']:<12}")
    print("-" * 80)
    
    return results


def example_4_live_trading_simulation():
    """Example 4: Simulate live trading session."""
    print_header("Example 4: Live Trading Simulation")
    
    skill = AdaptiveMultiRegimeSkill()
    
    print("Simulating a live trading session with real CMC data...\n")
    
    # Generate signal
    signal = skill.generate_signal_live('BTC')
    
    print(f"Signal: {signal['action']} @ ${signal.get('entry_price', 0):,.2f}\n")
    
    if signal['action'] == 'BUY' and signal['confidence'] > 0.5:
        print("Executing BUY order...")
        
        # Simulate trade execution
        trade = {
            'symbol': 'BTC',
            'action': 'BUY',
            'price': signal['entry_price'],
            'quantity': signal['position_size'] * skill.portfolio_value / signal['entry_price'],
            'cost': signal['position_size'] * skill.portfolio_value,
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Update portfolio
        skill.update_portfolio(trade)
        
        print(f"  ✓ Trade executed:")
        print(f"    Quantity: {trade['quantity']:.6f} BTC")
        print(f"    Cost: ${trade['cost']:,.2f}")
        print(f"    Stop Loss: ${trade['stop_loss']:,.2f}")
        print(f"    Take Profit: ${trade['take_profit']:,.2f}")
        
        # Show portfolio status
        portfolio = skill.get_portfolio_status()
        print(f"\n  Portfolio Status:")
        print(f"    Total Value: ${portfolio['portfolio_value']:,.2f}")
        print(f"    Available Capital: ${portfolio['available_capital']:,.2f}")
        print(f"    Open Positions: {len(portfolio['positions'])}")
        print(f"    Current Regime: {portfolio['current_regime']}")
        
    else:
        print(f"No trade: {signal['action']} signal with {signal['confidence']:.1%} confidence")
        print(f"Reasoning: {signal.get('reasoning', 'N/A')}")


def main():
    """Main execution."""
    print("\n" + "=" * 80)
    print("  REAL CMC API INTEGRATION TEST")
    print("  Adaptive Multi-Regime Trading Skill")
    print("=" * 80)
    print(f"\n  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  API: CoinMarketCap REST API")
    print(f"  Base URL: https://pro-api.coinmarketcap.com")
    print("\n" + "=" * 80)
    
    # Check API key
    if not check_api_key():
        return
    
    try:
        # Run examples
        example_1_fetch_live_data()
        example_2_generate_signal_with_live_data()
        example_3_compare_multiple_coins()
        example_4_live_trading_simulation()
        
        print_header("Summary")
        print("✅ All examples completed successfully!")
        print("\nWhat was demonstrated:")
        print("  1. Real-time data fetching from CoinMarketCap API")
        print("  2. Technical indicator calculation (RSI, volatility, etc.)")
        print("  3. Regime detection with live market data")
        print("  4. Signal generation based on real market conditions")
        print("  5. Multi-coin comparison with live data")
        print("  6. Live trading simulation with portfolio tracking")
        print("\n✓ This is NOT mock data - all data comes from CMC API!")
        print("✓ API endpoints used:")
        print("    - /v1/cryptocurrency/quotes/latest")
        print("    - /v1/global-metrics/quotes/latest")
        print("    - /v1/cryptocurrency/ohlcv/historical (if available)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible issues:")
        print("  1. Invalid or expired API key")
        print("  2. Rate limit exceeded (free plan: 30 calls/min)")
        print("  3. Network connection issue")
        print("  4. API plan doesn't support all endpoints")
        
    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    main()
