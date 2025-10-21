"""
🤖 SarlakBot v3.2.0 - AI Coach Service
Advanced AI-powered study coaching and analytics
"""

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Optional

from ..database.connection import get_db_manager
from ..utils.logging import logger


class RecommendationType(Enum):
    STUDY_PLAN = "study_plan"
    SUBJECT_PRIORITY = "subject_priority"
    BREAK_SCHEDULE = "break_schedule"
    GOAL_TASK = "goal_task"
    ENCOURAGEMENT = "encouragement"
    WARNING = "warning"


class InteractionType(Enum):
    RECOMMENDATION = "recommendation"
    ENCOURAGEMENT = "encouragement"
    WARNING = "warning"
    CELEBRATION = "celebration"
    ANALYSIS = "analysis"


@dataclass
class StudyAnalytics:
    """Study analytics data structure"""

    user_id: int
    total_study_time: int
    effective_study_time: int
    study_sessions: int
    subjects_studied: list[str]
    efficiency_score: float
    focus_score: float
    consistency_score: float
    study_patterns: dict[str, Any]
    difficulty_levels: dict[str, float]
    performance_scores: dict[str, float]


@dataclass
class AIRecommendation:
    """AI recommendation data structure"""

    recommendation_type: RecommendationType
    title: str
    description: str
    priority_level: int
    data: dict[str, Any]
    estimated_effectiveness: float
    expires_at: Optional[datetime] = None


@dataclass
class LearningPath:
    """Learning path data structure"""

    path_name: str
    description: str
    subjects_sequence: list[str]
    difficulty_progression: dict[str, float]
    estimated_duration: int
    current_position: int
    completion_percentage: float


@dataclass
class PerformancePrediction:
    """Performance prediction data structure"""

    prediction_type: str
    subject: Optional[str]
    predicted_value: float
    confidence_level: float
    prediction_data: dict[str, Any]
    target_date: date


class AICoachService:
    """AI Coach Service for personalized study coaching"""

    def __init__(self):
        self.db_manager = get_db_manager()
        self.persian_encouragements = [
            "آفرین! پیشرفت عالی داری 🌟",
            "تو واقعاً عالی هستی! ادامه بده 💪",
            "این روند فوق‌العاده‌ست! 🚀",
            "من بهت افتخار می‌کنم! 🏆",
            "تو یک ستاره‌ای! ⭐",
        ]

        self.persian_warnings = [
            "نگران نباش، همه‌چیز درست میشه 🤗",
            "یادت باشه، استراحت هم مهمه 😌",
            "کم کم پیش برو، عجله نکن 🐌",
            "من اینجا هستم تا کمکت کنم 💙",
            "همه‌چیز رو قدم به قدم حل می‌کنیم 🚶‍♂️",
        ]

    async def get_user_analytics(self, user_id: int, days: int = 30) -> Optional[StudyAnalytics]:
        """Get comprehensive study analytics for a user"""
        try:
            query = """
            SELECT
                user_id, total_study_time, effective_study_time, study_sessions,
                subjects_studied, difficulty_levels, performance_scores,
                study_patterns, efficiency_score, focus_score, consistency_score,
                analysis_date
            FROM study_analytics
            WHERE user_id = %s
            AND analysis_date >= %s
            ORDER BY analysis_date DESC
            LIMIT 1
            """

            start_date = (datetime.now() - timedelta(days=days)).date()
            result = await self.db_manager.fetch_one(query, (user_id, start_date))

            if not result:
                return None

            return StudyAnalytics(
                user_id=result["user_id"],
                total_study_time=result["total_study_time"],
                effective_study_time=result["effective_study_time"],
                study_sessions=result["study_sessions"],
                subjects_studied=result["subjects_studied"] or [],
                efficiency_score=float(result["efficiency_score"]),
                focus_score=float(result["focus_score"]),
                consistency_score=float(result["consistency_score"]),
                study_patterns=result["study_patterns"] or {},
                difficulty_levels=result["difficulty_levels"] or {},
                performance_scores=result["performance_scores"] or {},
            )

        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            return None

    async def generate_recommendations(self, user_id: int) -> list[AIRecommendation]:
        """Generate personalized AI recommendations for a user"""
        try:
            analytics = await self.get_user_analytics(user_id)
            if not analytics:
                return []

            recommendations = []

            # Study plan recommendation
            if analytics.efficiency_score < 70:
                recommendations.append(
                    AIRecommendation(
                        recommendation_type=RecommendationType.STUDY_PLAN,
                        title="بهبود برنامه مطالعه",
                        description="برنامه مطالعه‌ات رو بهینه‌تر کن تا کارایی بیشتری داشته باشی",
                        priority_level=3,
                        data={
                            "suggested_duration": 120,
                            "break_frequency": 25,
                            "subjects": analytics.subjects_studied[:2],
                        },
                        estimated_effectiveness=0.8,
                    )
                )

            # Subject priority recommendation
            if analytics.performance_scores:
                weak_subjects = [
                    subject for subject, score in analytics.performance_scores.items() if score < 60
                ]
                if weak_subjects:
                    recommendations.append(
                        AIRecommendation(
                            recommendation_type=RecommendationType.SUBJECT_PRIORITY,
                            title="اولویت‌بندی موضوعات",
                            description=f"روی {', '.join(weak_subjects)} بیشتر تمرکز کن",
                            priority_level=4,
                            data={"priority_subjects": weak_subjects},
                            estimated_effectiveness=0.9,
                        )
                    )

            # Break schedule recommendation
            if analytics.focus_score < 75:
                recommendations.append(
                    AIRecommendation(
                        recommendation_type=RecommendationType.BREAK_SCHEDULE,
                        title="برنامه استراحت",
                        description="استراحت‌های منظم داشته باش تا تمرکزت بهتر بشه",
                        priority_level=2,
                        data={
                            "break_duration": 15,
                            "break_frequency": 45,
                            "activities": ["نفس عمیق", "کشش", "نگاه به دور"],
                        },
                        estimated_effectiveness=0.7,
                    )
                )

            # Encouragement recommendation
            if analytics.efficiency_score > 80:
                recommendations.append(
                    AIRecommendation(
                        recommendation_type=RecommendationType.ENCOURAGEMENT,
                        title="تشویق",
                        description="آفرین! عملکرد عالی داری، ادامه بده",
                        priority_level=1,
                        data={"encouragement_type": "high_performance"},
                        estimated_effectiveness=1.0,
                    )
                )

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    async def save_recommendation(self, user_id: int, recommendation: AIRecommendation) -> bool:
        """Save AI recommendation to database"""
        try:
            query = """
            INSERT INTO ai_recommendations
            (user_id, recommendation_type, recommendation_data, priority_level, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            """

            expires_at = None
            if recommendation.expires_at:
                expires_at = recommendation.expires_at

            await self.db_manager.execute(
                query,
                (
                    user_id,
                    recommendation.recommendation_type.value,
                    json.dumps(recommendation.data),
                    recommendation.priority_level,
                    expires_at,
                ),
            )
            return True

        except Exception as e:
            logger.error(f"Error saving recommendation: {e}")
            return False

    async def get_active_recommendations(self, user_id: int) -> list[dict[str, Any]]:
        """Get active recommendations for a user"""
        try:
            query = """
            SELECT id, recommendation_type, recommendation_data, priority_level,
                   created_at, expires_at
            FROM ai_recommendations
            WHERE user_id = %s AND is_active = TRUE
            ORDER BY priority_level DESC, created_at DESC
            """

            results = await self.db_manager.fetch_all(query, (user_id,))
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error getting active recommendations: {e}")
            return []

    async def create_learning_path(
        self, user_id: int, subjects: list[str], difficulty_progression: dict[str, float]
    ) -> Optional[LearningPath]:
        """Create a personalized learning path for a user"""
        try:
            path_name = f"مسیر یادگیری {', '.join(subjects[:2])}"
            description = f"برنامه شخصی‌سازی شده برای {', '.join(subjects)}"

            query = """
            INSERT INTO learning_paths
            (user_id, path_name, path_description, subjects_sequence,
             difficulty_progression, estimated_duration, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """

            estimated_duration = len(subjects) * 7  # 7 days per subject

            result = await self.db_manager.fetch_one(
                query,
                (
                    user_id,
                    path_name,
                    description,
                    json.dumps(subjects),
                    json.dumps(difficulty_progression),
                    estimated_duration,
                    True,
                ),
            )

            if result:
                return LearningPath(
                    path_name=path_name,
                    description=description,
                    subjects_sequence=subjects,
                    difficulty_progression=difficulty_progression,
                    estimated_duration=estimated_duration,
                    current_position=0,
                    completion_percentage=0.0,
                )

            return None

        except Exception as e:
            logger.error(f"Error creating learning path: {e}")
            return None

    async def predict_performance(
        self, user_id: int, subject: str, target_date: date
    ) -> Optional[PerformancePrediction]:
        """Predict user performance for a specific subject and date"""
        try:
            analytics = await self.get_user_analytics(user_id)
            if not analytics:
                return None

            # Simple prediction algorithm (can be enhanced with ML)
            base_score = analytics.performance_scores.get(subject, 50)
            time_factor = min(analytics.total_study_time / 100, 1.0)  # Normalize to 0-1
            consistency_factor = analytics.consistency_score / 100

            predicted_score = base_score + (time_factor * 20) + (consistency_factor * 10)
            predicted_score = min(predicted_score, 100)  # Cap at 100

            confidence = min(analytics.consistency_score, 90)  # Max 90% confidence

            prediction_data = {
                "base_score": base_score,
                "time_factor": time_factor,
                "consistency_factor": consistency_factor,
                "study_time": analytics.total_study_time,
                "efficiency": analytics.efficiency_score,
            }

            return PerformancePrediction(
                prediction_type="exam_score",
                subject=subject,
                predicted_value=predicted_score,
                confidence_level=confidence,
                prediction_data=prediction_data,
                target_date=target_date,
            )

        except Exception as e:
            logger.error(f"Error predicting performance: {e}")
            return None

    async def save_prediction(self, user_id: int, prediction: PerformancePrediction) -> bool:
        """Save performance prediction to database"""
        try:
            query = """
            INSERT INTO performance_predictions
            (user_id, prediction_type, subject, predicted_value, confidence_level,
             prediction_data, target_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            await self.db_manager.execute(
                query,
                (
                    user_id,
                    prediction.prediction_type,
                    prediction.subject,
                    prediction.predicted_value,
                    prediction.confidence_level,
                    json.dumps(prediction.prediction_data),
                    prediction.target_date,
                ),
            )
            return True

        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return False

    async def log_coach_interaction(
        self,
        user_id: int,
        interaction_type: InteractionType,
        message: str,
        context: dict[str, Any] = None,
    ) -> bool:
        """Log AI coach interaction"""
        try:
            query = """
            INSERT INTO ai_coach_interactions
            (user_id, interaction_type, message_content, context_data)
            VALUES (%s, %s, %s, %s)
            """

            await self.db_manager.execute(
                query, (user_id, interaction_type.value, message, json.dumps(context or {}))
            )
            return True

        except Exception as e:
            logger.error(f"Error logging coach interaction: {e}")
            return False

    async def get_coach_personality_message(
        self, user_id: int, interaction_type: InteractionType
    ) -> str:
        """Get personalized coach message based on user and interaction type"""
        try:
            analytics = await self.get_user_analytics(user_id)

            if interaction_type == InteractionType.ENCOURAGEMENT:
                if analytics and analytics.efficiency_score > 80:
                    return "🌟 تو واقعاً عالی هستی! این روند فوق‌العاده‌ست!"
                else:
                    return "💪 تو می‌تونی! من بهت ایمان دارم!"

            elif interaction_type == InteractionType.WARNING:
                if analytics and analytics.consistency_score < 60:
                    return "🤗 نگران نباش، همه‌چیز درست میشه. قدم به قدم پیش برویم"
                else:
                    return "😌 یادت باشه، استراحت هم مهمه"

            elif interaction_type == InteractionType.CELEBRATION:
                return "🎉 آفرین! این دستاورد واقعاً ارزشمند بود!"

            else:
                return "🤖 من اینجا هستم تا کمکت کنم. چطور می‌تونم کمکت کنم؟"

        except Exception as e:
            logger.error(f"Error getting coach message: {e}")
            return "🤖 من اینجا هستم تا کمکت کنم!"

    async def analyze_study_patterns(self, user_id: int) -> dict[str, Any]:
        """Analyze user's study patterns and return insights"""
        try:
            analytics = await self.get_user_analytics(user_id, days=14)
            if not analytics:
                return {}

            patterns = {
                "efficiency_trend": "stable",
                "focus_level": "good" if analytics.focus_score > 70 else "needs_improvement",
                "consistency": "excellent" if analytics.consistency_score > 80 else "good",
                "preferred_subjects": analytics.subjects_studied[:2],
                "study_intensity": "high" if analytics.efficiency_score > 80 else "medium",
                "recommendations": [],
            }

            # Generate pattern-based recommendations
            if analytics.efficiency_score < 70:
                patterns["recommendations"].append("زمان مطالعه‌ات رو بهینه‌تر کن")

            if analytics.focus_score < 75:
                patterns["recommendations"].append("استراحت‌های منظم داشته باش")

            if analytics.consistency_score < 60:
                patterns["recommendations"].append("برنامه مطالعه‌ات رو منظم‌تر کن")

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing study patterns: {e}")
            return {}

    async def get_user_ai_coach_summary(self, user_id: int) -> dict[str, Any]:
        """Get comprehensive AI coach summary for a user"""
        try:
            analytics = await self.get_user_analytics(user_id)
            recommendations = await self.get_active_recommendations(user_id)
            patterns = await self.analyze_study_patterns(user_id)

            summary = {
                "user_id": user_id,
                "analytics": {
                    "total_study_time": analytics.total_study_time if analytics else 0,
                    "efficiency_score": analytics.efficiency_score if analytics else 0,
                    "focus_score": analytics.focus_score if analytics else 0,
                    "consistency_score": analytics.consistency_score if analytics else 0,
                },
                "recommendations_count": len(recommendations),
                "patterns": patterns,
                "coach_message": await self.get_coach_personality_message(
                    user_id, InteractionType.ENCOURAGEMENT
                ),
                "last_updated": datetime.now().isoformat(),
            }

            return summary

        except Exception as e:
            logger.error(f"Error getting AI coach summary: {e}")
            return {"error": "Failed to get AI coach summary"}


# Global AI Coach Service instance
ai_coach_service = AICoachService()
