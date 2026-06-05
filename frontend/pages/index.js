import { useState } from 'react'

export default function Home() {
  const [symbol, setSymbol] = useState('BTC')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const testCMC = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`/api/test-cmc?symbol=${symbol}`)
      const data = await res.json()
      
      if (!res.ok) {
        throw new Error(data.error || 'Failed to fetch data')
      }
      
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="header">
        <h1>🚀 AdaptiveTrader Dashboard</h1>
        <p>Real-time CMC data testing with multi-regime detection</p>
        <p style={{ fontSize: '0.9rem', marginTop: '10px', opacity: 0.8 }}>
          BNB Hackathon Track 2 - Strategy Skills
        </p>
      </div>

      <div className="test-section">
        <h2 style={{ marginBottom: '20px' }}>Test CMC API & Generate Signal</h2>
        
        <div className="input-group">
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Enter crypto symbol (BTC, ETH, BNB...)"
          />
          <button onClick={testCMC} disabled={loading}>
            {loading ? 'Testing...' : 'Test Now'}
          </button>
        </div>

        <p style={{ fontSize: '0.9rem', color: '#8892b0' }}>
          Try: BTC, ETH, BNB, ADA, SOL, DOGE, XRP, DOT, UNI, LINK
        </p>
      </div>

      {loading && (
        <div className="loading">
          <div>⏳ Fetching live data from CoinMarketCap...</div>
        </div>
      )}

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="results">
          <div className="card">
            <h3>💰 Market Data</h3>
            <div className="data-grid">
              <div className="data-item">
                <div className="data-label">Symbol</div>
                <div className="data-value">{result.market_data.symbol}</div>
              </div>
              <div className="data-item">
                <div className="data-label">Price</div>
                <div className="data-value">
                  ${result.market_data.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
              </div>
              <div className="data-item">
                <div className="data-label">24h Change</div>
                <div className="data-value" style={{ 
                  color: result.market_data.percent_change_24h >= 0 ? '#10b981' : '#ef4444' 
                }}>
                  {result.market_data.percent_change_24h >= 0 ? '+' : ''}
                  {result.market_data.percent_change_24h.toFixed(2)}%
                </div>
              </div>
              <div className="data-item">
                <div className="data-label">24h Volume</div>
                <div className="data-value">
                  ${(result.market_data.volume_24h / 1e9).toFixed(2)}B
                </div>
              </div>
              <div className="data-item">
                <div className="data-label">Market Cap</div>
                <div className="data-value">
                  ${(result.market_data.market_cap / 1e9).toFixed(2)}B
                </div>
              </div>
              <div className="data-item">
                <div className="data-label">RSI</div>
                <div className="data-value">{result.market_data.rsi.toFixed(1)}</div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3>🎯 Market Regime</h3>
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <span className={`regime regime-${result.signal.regime || 'sideways'}`}>
                {(result.signal.regime || 'sideways').toUpperCase()}
              </span>
              <p style={{ marginTop: '15px', color: '#8892b0' }}>
                Confidence: {(result.signal.regime_confidence * 100).toFixed(1)}%
              </p>
            </div>
          </div>

          <div className="card">
            <h3>📊 Trading Signal</h3>
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <div className={`signal signal-${result.signal.action.toLowerCase()}`}>
                {result.signal.action}
              </div>
              <div style={{ marginTop: '20px' }}>
                <p style={{ fontSize: '1.1rem', marginBottom: '10px' }}>
                  <strong>Confidence:</strong> {(result.signal.confidence * 100).toFixed(1)}%
                </p>
                {result.signal.action !== 'HOLD' && (
                  <>
                    <p style={{ color: '#8892b0', marginBottom: '5px' }}>
                      Position Size: {(result.signal.position_size * 100).toFixed(1)}%
                    </p>
                    <p style={{ color: '#8892b0', marginBottom: '5px' }}>
                      Entry: ${result.signal.entry_price?.toLocaleString()}
                    </p>
                    <p style={{ color: '#8892b0', marginBottom: '5px' }}>
                      Stop Loss: ${result.signal.stop_loss?.toLocaleString()}
                    </p>
                    <p style={{ color: '#8892b0' }}>
                      Take Profit: ${result.signal.take_profit?.toLocaleString()}
                    </p>
                  </>
                )}
              </div>
              <div style={{ 
                marginTop: '20px', 
                padding: '15px', 
                background: '#1a1f3a', 
                borderRadius: '8px',
                textAlign: 'left'
              }}>
                <strong>Reasoning:</strong>
                <p style={{ marginTop: '10px', color: '#8892b0', lineHeight: '1.6' }}>
                  {result.signal.reasoning}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <h3>⚙️ Technical Data</h3>
            <div className="data-grid">
              <div className="data-item">
                <div className="data-label">Volatility</div>
                <div className="data-value">
                  {(result.market_data.volatility * 100).toFixed(2)}%
                </div>
              </div>
              <div className="data-item">
                <div className="data-label">BTC Dominance</div>
                <div className="data-value">
                  {result.market_data.btc_dominance.toFixed(2)}%
                </div>
              </div>
              <div className="data-item">
                <div className="data-label">Total Market Cap</div>
                <div className="data-value">
                  ${(result.market_data.total_market_cap / 1e12).toFixed(2)}T
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="footer">
        <p>
          <strong>AdaptiveTrader</strong> - Multi-Regime Trading Skill
        </p>
        <p style={{ marginTop: '10px' }}>
          <a href="https://github.com/manexustechnology/AdaptiveTrader" target="_blank" rel="noopener noreferrer">
            GitHub Repository
          </a>
          {' | '}
          Powered by CoinMarketCap API
        </p>
      </div>
    </div>
  )
}
