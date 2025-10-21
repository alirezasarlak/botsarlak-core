"""
🤖 SarlakBot v3.2.0 - AI Coach Module
AI-powered study coaching and personalized recommendations
"""

from .analytics_handler import analytics_handler
from .coach_handler import ai_coach_handler
from .recommendations_handler import recommendations_handler
from .schedule_handler import schedule_handler

__all__ = ["ai_coach_handler", "analytics_handler", "recommendations_handler", "schedule_handler"]
