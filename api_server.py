"""
Simple FastAPI backend to serve CMC data to frontend
Run with: uvicorn api_server:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.cmc_skill import AdaptiveMultiRegimeSkill
import os

app = FastAPI(title="AdaptiveTrader API")

# Enable CORS for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize skill
skill = AdaptiveMultiRegimeSkill()

@app.get("/")
def read_root():
    return {
        "message": "AdaptiveTrader API",
        "version": "1.0.0",
        "endpoints": {
            "/api/signal/{symbol}": "Generate trading signal for symbol",
            "/health": "Health check"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/signal/{symbol}")
def get_signal(symbol: str):
    """
    Generate trading signal for cryptocurrency
    
    Example: /api/signal/BTC
    """
    try:
        # Fetch live market data
        market_data = skill.fetch_live_market_data(symbol.upper())
        
        # Generate signal
        signal = skill.generate_signal(market_data)
        
        # Get regime info
        regime_analysis = skill.regime_detector.detect_regime(market_data)
        
        return {
            "success": True,
            "market_data": {
                "symbol": market_data.get("symbol"),
                "price": market_data.get("price"),
                "volume_24h": market_data.get("volume_24h"),
                "market_cap": market_data.get("market_cap"),
                "percent_change_24h": market_data.get("percent_change_24h"),
                "rsi": market_data.get("rsi"),
                "volatility": market_data.get("volatility"),
                "btc_dominance": market_data.get("btc_dominance"),
                "total_market_cap": market_data.get("total_market_cap")
            },
            "signal": {
                "action": signal.get("action"),
                "confidence": signal.get("confidence"),
                "regime": regime_analysis.get("regime"),
                "regime_confidence": regime_analysis.get("confidence"),
                "position_size": signal.get("position_size"),
                "entry_price": signal.get("entry_price"),
                "stop_loss": signal.get("stop_loss"),
                "take_profit": signal.get("take_profit"),
                "reasoning": signal.get("reasoning")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
