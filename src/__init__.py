"""
Adaptive Multi-Regime Trading Skill
BNB Hackathon Track 2 - Strategy Skills

A CMC Skill that detects market regimes and adapts trading strategies accordingly.
"""

__version__ = "1.0.0"
__author__ = "BNB Hackathon Participant"
__email__ = "your.email@example.com"

from .cmc_skill import AdaptiveMultiRegimeSkill, create_skill
from .regime_detector import RegimeDetector
from .signal_generator import SignalGenerator
from .risk_manager import RiskManager
from .cmc_data_fetcher import CMCDataFetcher

__all__ = [
    'AdaptiveMultiRegimeSkill',
    'create_skill',
    'RegimeDetector',
    'SignalGenerator',
    'RiskManager',
    'CMCDataFetcher',
]
