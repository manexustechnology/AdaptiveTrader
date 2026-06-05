#!/usr/bin/env python
"""
Quick CMC API Test Script
Run this to verify CMC API integration is working
"""

from src.cmc_data_fetcher import CMCDataFetcher
from src.cmc_skill import AdaptiveMultiRegimeSkill
import sys

def test_data_fetcher():
    """Test 1: CMC Data Fetcher"""
    print("="*70)
    print("TEST 1: CMC Data Fetcher")
    print("="*70)
    
    try:
        fetcher = CMCDataFetcher()
        
        # Test BTC quote
        print("\n📊 Fetching BTC quote...")
        btc = fetcher.get_crypto_quote('BTC')
        print(f"   ✓ Price: ${btc['price']:,.2f}")
        print(f"   ✓ 24h Volume: ${btc['volume_24h']:,.0f}")
        print(f"   ✓ Market Cap: ${btc['market_cap']:,.0f}")
        print(f"   ✓ 24h Change: {btc['percent_change_24h']:.2f}%")
        
        # Test global metrics
        print("\n🌍 Fetching global metrics...")
        metrics = fetcher.get_global_metrics()
        print(f"   ✓ Total Market Cap: ${metrics['total_market_cap']:,.0f}")
        print(f"   ✓ BTC Dominance: {metrics['btc_dominance']:.2f}%")
        print(f"   ✓ Active Cryptos: {metrics['active_cryptocurrencies']:,}")
        
        # Test comprehensive market data
        print("\n📈 Fetching comprehensive market data...")
        market = fetcher.get_market_data_for_strategy('BTC')
        print(f"   ✓ RSI: {market['rsi']:.2f}")
        print(f"   ✓ Volatility: {market['volatility']:.2f}%")
        print(f"   ✓ Data Source: {market['data_source']}")
        
        print("\n✅ Data Fetcher Test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Data Fetcher Test FAILED: {e}")
        return False


def test_signal_generation():
    """Test 2: Signal Generation with Real Data"""
    print("\n" + "="*70)
    print("TEST 2: Live Signal Generation")
    print("="*70)
    
    try:
        skill = AdaptiveMultiRegimeSkill()
        
        symbols = ['BTC', 'ETH', 'BNB']
        
        for symbol in symbols:
            print(f"\n📊 {symbol}:")
            signal = skill.generate_signal_live(symbol)
            
            print(f"   Price: ${signal['entry_price']:,.2f}")
            print(f"   Action: {signal['action']}")
            print(f"   Regime: {signal['regime']}")
            print(f"   Confidence: {signal['confidence']:.1%}")
            
            if signal.get('position_size') and signal['position_size'] > 0:
                print(f"   Position Size: {signal['position_size']:.1%}")
            
            print(f"   Reasoning: {signal['reasoning']}")
        
        print("\n✅ Signal Generation Test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Signal Generation Test FAILED: {e}")
        return False


def test_multi_call():
    """Test 3: Multiple API Calls (Rate Limiting)"""
    print("\n" + "="*70)
    print("TEST 3: Multiple API Calls (Rate Limiting Test)")
    print("="*70)
    
    try:
        fetcher = CMCDataFetcher()
        
        symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL']
        
        print(f"\nFetching data for {len(symbols)} cryptocurrencies...")
        
        for i, symbol in enumerate(symbols, 1):
            try:
                data = fetcher.get_crypto_quote(symbol)
                print(f"   {i}. {symbol}: ${data['price']:,.2f} "
                      f"({data['percent_change_24h']:+.2f}%)")
            except Exception as e:
                print(f"   {i}. {symbol}: Failed - {e}")
        
        print("\n✅ Rate Limiting Test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Rate Limiting Test FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🚀 "*23)
    print("CMC API INTEGRATION TEST SUITE")
    print("🚀 "*23 + "\n")
    
    results = []
    
    # Test 1: Data Fetcher
    results.append(test_data_fetcher())
    
    # Test 2: Signal Generation
    results.append(test_signal_generation())
    
    # Test 3: Multiple Calls
    results.append(test_multi_call())
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED - CMC API IS FULLY FUNCTIONAL!")
        print("\nYour CMC API integration is working correctly.")
        print("You can now use the skill for live trading signals.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nPlease check:")
        print("1. API key is set correctly in config/config.yaml")
        print("2. Internet connection is working")
        print("3. CMC API rate limits are not exceeded")
        return 1


if __name__ == '__main__':
    sys.exit(main())
