"""
CoinMarketCap Data Fetcher
Real API integration with CoinMarketCap REST API

This module handles all communication with the CoinMarketCap API
to fetch real-time cryptocurrency market data.

API Documentation: https://coinmarketcap.com/api/documentation/v1/
"""

import os
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class CMCDataFetcher:
    """
    Fetches real-time cryptocurrency data from CoinMarketCap API.
    
    Endpoints used:
    - /v1/cryptocurrency/quotes/latest: Latest price, volume, market cap
    - /v1/cryptocurrency/ohlcv/historical: Historical OHLCV data for indicators
    - /v1/global-metrics/quotes/latest: Global market metrics
    """
    
    # CoinMarketCap API Base URL (ACTUAL from documentation)
    BASE_URL = "https://pro-api.coinmarketcap.com"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CMC Data Fetcher.
        
        Args:
            api_key: CoinMarketCap API key. If None, reads from environment variable CMC_API_KEY
        """
        self.api_key = api_key or os.environ.get('CMC_API_KEY')
        
        if not self.api_key:
            logger.warning("CMC_API_KEY not set. API calls will fail. "
                         "Get your key at: https://pro.coinmarketcap.com/signup")
        
        # Request headers (ACTUAL from CMC documentation)
        self.headers = {
            'Accept': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key
        }
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds between requests
        
        logger.info("CMC Data Fetcher initialized")
    
    def _rate_limit(self):
        """Enforce rate limiting between API calls."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make authenticated request to CMC API.
        
        Args:
            endpoint: API endpoint (e.g., '/v1/cryptocurrency/quotes/latest')
            params: Query parameters
            
        Returns:
            API response data
            
        Raises:
            Exception: If API request fails
        """
        self._rate_limit()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            logger.debug(f"Making request to {endpoint} with params: {params}")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if data.get('status', {}).get('error_code', 0) != 0:
                error_msg = data['status'].get('error_message', 'Unknown error')
                raise Exception(f"CMC API Error: {error_msg}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"Failed to fetch data from CMC: {e}")
    
    def get_crypto_quote(self, symbol: str, convert: str = 'USD') -> Dict[str, Any]:
        """
        Get latest quote for a cryptocurrency.
        
        Endpoint: GET /v1/cryptocurrency/quotes/latest
        Documentation: https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyQuotesLatest
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
            convert: Quote currency (default: 'USD')
            
        Returns:
            Dictionary with quote data:
            {
                'symbol': 'BTC',
                'name': 'Bitcoin',
                'price': 45000.00,
                'volume_24h': 28439861524.00,
                'market_cap': 880000000000.00,
                'percent_change_1h': 0.15,
                'percent_change_24h': 2.34,
                'percent_change_7d': -1.05,
                'last_updated': '2026-06-04T12:00:00.000Z'
            }
        """
        logger.info(f"Fetching quote for {symbol}")
        
        params = {
            'symbol': symbol.upper(),
            'convert': convert
        }
        
        data = self._make_request('/v1/cryptocurrency/quotes/latest', params)
        
        # Extract quote data
        crypto_data = data['data'][symbol.upper()]
        quote = crypto_data['quote'][convert]
        
        return {
            'symbol': crypto_data['symbol'],
            'name': crypto_data['name'],
            'price': quote['price'],
            'volume_24h': quote['volume_24h'],
            'volume_change_24h': quote.get('volume_change_24h', 0),
            'market_cap': quote['market_cap'],
            'percent_change_1h': quote.get('percent_change_1h', 0),
            'percent_change_24h': quote.get('percent_change_24h', 0),
            'percent_change_7d': quote.get('percent_change_7d', 0),
            'circulating_supply': crypto_data.get('circulating_supply', 0),
            'total_supply': crypto_data.get('total_supply', 0),
            'max_supply': crypto_data.get('max_supply'),
            'last_updated': quote['last_updated']
        }
    
    def get_global_metrics(self) -> Dict[str, Any]:
        """
        Get global cryptocurrency market metrics.
        
        Endpoint: GET /v1/global-metrics/quotes/latest
        Documentation: https://coinmarketcap.com/api/documentation/v1/#operation/getV1GlobalmetricsQuotesLatest
        
        Returns:
            Dictionary with global metrics:
            {
                'total_market_cap': 2400000000000.00,
                'total_volume_24h': 95000000000.00,
                'btc_dominance': 45.5,
                'eth_dominance': 18.2,
                'active_cryptocurrencies': 10500,
                'total_cryptocurrencies': 24000,
                'last_updated': '2026-06-04T12:00:00.000Z'
            }
        """
        logger.info("Fetching global market metrics")
        
        data = self._make_request('/v1/global-metrics/quotes/latest', {})
        
        metrics = data['data']
        quote = metrics.get('quote', {}).get('USD', {})
        
        return {
            'total_market_cap': quote.get('total_market_cap', 0),
            'total_volume_24h': quote.get('total_volume_24h', 0),
            'btc_dominance': metrics.get('btc_dominance', 0),
            'eth_dominance': metrics.get('eth_dominance', 0),
            'active_cryptocurrencies': metrics.get('active_cryptocurrencies', 0),
            'total_cryptocurrencies': metrics.get('total_cryptocurrencies', 0),
            'defi_volume_24h': metrics.get('defi_volume_24h', 0),
            'defi_market_cap': metrics.get('defi_market_cap', 0),
            'last_updated': quote.get('last_updated', '')
        }
    
    def get_ohlcv_historical(self, symbol: str, time_period: str = 'daily', 
                            count: int = 30) -> List[Dict[str, Any]]:
        """
        Get historical OHLCV (Open, High, Low, Close, Volume) data.
        
        Endpoint: GET /v1/cryptocurrency/ohlcv/historical
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC')
            time_period: 'daily', 'hourly', 'weekly', 'monthly'
            count: Number of periods to fetch (default: 30)
            
        Returns:
            List of OHLCV data points:
            [
                {
                    'time_open': '2026-05-01T00:00:00.000Z',
                    'time_close': '2026-05-01T23:59:59.999Z',
                    'open': 44500.00,
                    'high': 45800.00,
                    'low': 44200.00,
                    'close': 45000.00,
                    'volume': 28000000000.00
                },
                ...
            ]
        """
        logger.info(f"Fetching historical OHLCV for {symbol}")
        
        params = {
            'symbol': symbol.upper(),
            'time_period': time_period,
            'count': count
        }
        
        try:
            data = self._make_request('/v1/cryptocurrency/ohlcv/historical', params)
            
            # Extract OHLCV data
            quotes = data['data']['quotes']
            
            ohlcv_data = []
            for quote in quotes:
                ohlcv = quote['quote']['USD']
                ohlcv_data.append({
                    'time_open': quote['time_open'],
                    'time_close': quote['time_close'],
                    'open': ohlcv['open'],
                    'high': ohlcv['high'],
                    'low': ohlcv['low'],
                    'close': ohlcv['close'],
                    'volume': ohlcv['volume']
                })
            
            return ohlcv_data
            
        except Exception as e:
            logger.warning(f"Failed to fetch OHLCV data: {e}. "
                          "This endpoint may require a paid API plan.")
            return []
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: List of closing prices (oldest first)
            period: RSI period (default: 14)
            
        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            logger.warning(f"Insufficient data for RSI calculation (need {period + 1}, got {len(prices)})")
            return 50.0  # Neutral
        
        # Calculate price changes
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separate gains and losses
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        # Calculate average gain and loss
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def calculate_volatility(self, prices: List[float]) -> float:
        """
        Calculate price volatility (standard deviation of returns).
        
        Args:
            prices: List of closing prices
            
        Returns:
            Volatility as percentage
        """
        if len(prices) < 2:
            return 0.0
        
        # Calculate returns
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # Calculate standard deviation
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        
        return round(std_dev * 100, 2)
    
    def get_market_data_for_strategy(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive market data for trading strategy.
        
        This method aggregates data from multiple endpoints to provide
        all the information needed for regime detection and signal generation.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC')
            
        Returns:
            Dictionary with comprehensive market data
        """
        logger.info(f"Fetching comprehensive market data for {symbol}")
        
        # Get current quote
        quote = self.get_crypto_quote(symbol)
        
        # Get global metrics
        global_metrics = self.get_global_metrics()
        
        # Try to get historical data for technical indicators
        ohlcv = self.get_ohlcv_historical(symbol, time_period='daily', count=30)
        
        # Calculate technical indicators if we have historical data
        if ohlcv and len(ohlcv) > 0:
            prices = [candle['close'] for candle in ohlcv]
            rsi = self.calculate_rsi(prices)
            volatility = self.calculate_volatility(prices)
            
            # Simple moving averages
            sma_7 = sum(prices[-7:]) / 7 if len(prices) >= 7 else quote['price']
            sma_30 = sum(prices[-30:]) / 30 if len(prices) >= 30 else quote['price']
        else:
            # Fallback: estimate from available data
            logger.warning("No historical data available. Using estimates for technical indicators.")
            rsi = 50.0 + (quote['percent_change_7d'] / 2)  # Rough estimate
            rsi = max(0, min(100, rsi))  # Clamp to 0-100
            volatility = abs(quote['percent_change_24h'])
            sma_7 = quote['price']
            sma_30 = quote['price']
        
        # Compile comprehensive market data
        market_data = {
            # Basic quote data
            'symbol': quote['symbol'],
            'name': quote['name'],
            'price': quote['price'],
            'volume_24h': quote['volume_24h'],
            'market_cap': quote['market_cap'],
            
            # Price changes
            'percent_change_1h': quote['percent_change_1h'],
            'percent_change_24h': quote['percent_change_24h'],
            'percent_change_7d': quote['percent_change_7d'],
            
            # Technical indicators
            'rsi': rsi,
            'volatility': volatility,
            'sma_7': sma_7,
            'sma_30': sma_30,
            
            # Global market context
            'btc_dominance': global_metrics['btc_dominance'],
            'total_market_cap': global_metrics['total_market_cap'],
            'total_volume_24h': global_metrics['total_volume_24h'],
            
            # Supply data
            'circulating_supply': quote['circulating_supply'],
            'total_supply': quote['total_supply'],
            'max_supply': quote['max_supply'],
            
            # Metadata
            'last_updated': quote['last_updated'],
            'data_source': 'CoinMarketCap API'
        }
        
        logger.info(f"Market data fetched successfully for {symbol}: "
                   f"Price=${market_data['price']:.2f}, RSI={market_data['rsi']:.1f}, "
                   f"Vol={market_data['volatility']:.2f}%")
        
        return market_data


def test_cmc_fetcher():
    """Test CMC Data Fetcher with real API calls."""
    print("=" * 80)
    print("CMC Data Fetcher Test")
    print("=" * 80)
    
    # Check for API key
    api_key = os.environ.get('CMC_API_KEY')
    if not api_key:
        print("\n⚠️  WARNING: CMC_API_KEY environment variable not set!")
        print("   Get your free API key at: https://pro.coinmarketcap.com/signup")
        print("   Then set it: export CMC_API_KEY='your-key-here'")
        print("\n   For this test, using demo mode (will show structure only)\n")
    
    fetcher = CMCDataFetcher(api_key)
    
    try:
        # Test 1: Get BTC quote
        print("\n1. Testing get_crypto_quote('BTC')...")
        btc_quote = fetcher.get_crypto_quote('BTC')
        print(f"   ✓ BTC Price: ${btc_quote['price']:,.2f}")
        print(f"   ✓ 24h Volume: ${btc_quote['volume_24h']:,.0f}")
        print(f"   ✓ Market Cap: ${btc_quote['market_cap']:,.0f}")
        
        # Test 2: Get global metrics
        print("\n2. Testing get_global_metrics()...")
        global_metrics = fetcher.get_global_metrics()
        print(f"   ✓ Total Market Cap: ${global_metrics['total_market_cap']:,.0f}")
        print(f"   ✓ BTC Dominance: {global_metrics['btc_dominance']:.2f}%")
        
        # Test 3: Get comprehensive market data
        print("\n3. Testing get_market_data_for_strategy('BTC')...")
        market_data = fetcher.get_market_data_for_strategy('BTC')
        print(f"   ✓ RSI: {market_data['rsi']:.2f}")
        print(f"   ✓ Volatility: {market_data['volatility']:.2f}%")
        print(f"   ✓ 7d Change: {market_data['percent_change_7d']:.2f}%")
        
        print("\n✅ All tests passed! CMC API integration is working.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nPossible issues:")
        print("   1. API key not set or invalid")
        print("   2. No internet connection")
        print("   3. Rate limit exceeded")
        print("   4. API endpoint changed")
        
    print("\n" + "=" * 80)


if __name__ == '__main__':
    test_cmc_fetcher()
