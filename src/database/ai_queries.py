"""
🤖 SarlakBot v3.2.0 - AI Coach Database Queries
Database operations for AI Coach and Analytics system
"""

import json
from datetime import datetime, timedelta
from typing import Any

from ..utils.logging import logger
from .connection import get_db_manager


class AIQueries:
    """Database queries for AI Coach system"""

    def __init__(self):
        self.db_manager = get_db_manager()

    async def get_user_analytics_summary(
        self, user_id: int, days: int = 30
    ) -> dict[str, Any] | None:
        """Get comprehensive analytics summary for a user"""
        try:
            query = """
            SELECT
                sa.user_id,
                sa.total_study_time,
                sa.effective_study_time,
                sa.study_sessions,
                sa.subjects_studied,
                sa.efficiency_score,
                sa.focus_score,
                sa.consistency_score,
                sa.study_patterns,
                sa.difficulty_levels,
                sa.performance_scores,
                sa.analysis_date,
                COUNT(ar.id) as active_recommendations,
                COUNT(lp.id) as active_learning_paths,
                COUNT(pp.id) as pending_predictions
            FROM study_analytics sa
            LEFT JOIN ai_recommendations ar ON sa.user_id = ar.user_id AND ar.is_active = TRUE
            LEFT JOIN learning_paths lp ON sa.user_id = lp.user_id AND lp.is_active = TRUE
            LEFT JOIN performance_predictions pp ON sa.user_id = pp.user_id AND pp.target_date > CURRENT_DATE
            WHERE sa.user_id = %s
            AND sa.analysis_date >= %s
            GROUP BY sa.user_id, sa.total_study_time, sa.effective_study_time,
                     sa.study_sessions, sa.subjects_studied, sa.efficiency_score,
                     sa.focus_score, sa.consistency_score, sa.study_patterns,
                     sa.difficulty_levels, sa.performance_scores, sa.analysis_date
            ORDER BY sa.analysis_date DESC
            LIMIT 1
            """

            start_date = (datetime.now() - timedelta(days=days)).date()
            result = await self.db_manager.fetch_one(query, (user_id, start_date))

            return dict(result) if result else None

        except Exception as e:
            logger.error(f"Error getting user analytics summary: {e}")
            return None

    async def get_user_recommendations(self, user_id: int, limit: int = 10) -> list[dict[str, Any]]:
        """Get active recommendations for a user"""
        try:
            query = """
            SELECT
                id, recommendation_type, recommendation_data, priority_level,
                is_active, is_accepted, created_at, expires_at
            FROM ai_recommendations
            WHERE user_id = %s AND is_active = TRUE
            ORDER BY priority_level DESC, created_at DESC
            LIMIT %s
            """

            results = await self.db_manager.fetch_all(query, (user_id, limit))
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error getting user recommendations: {e}")
            return []

    async def get_user_learning_paths(self, user_id: int) -> list[dict[str, Any]]:
        """Get active learning paths for a user"""
        try:
            query = """
            SELECT
                id, path_name, path_description, subjects_sequence,
                difficulty_progression, estimated_duration, current_position,
                completion_percentage, created_at
            FROM learning_paths
            WHERE user_id = %s AND is_active = TRUE
            ORDER BY created_at DESC
            """

            results = await self.db_manager.fetch_all(query, (user_id,))
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error getting user learning paths: {e}")
            return []

    async def get_user_predictions(
        self, user_id: int, days_ahead: int = 30
    ) -> list[dict[str, Any]]:
        """Get performance predictions for a user"""
        try:
            query = """
            SELECT
                id, prediction_type, subject, predicted_value, confidence_level,
                prediction_data, target_date, is_achieved, created_at
            FROM performance_predictions
            WHERE user_id = %s
            AND target_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '%s days'
            ORDER BY target_date ASC
            """

            results = await self.db_manager.fetch_all(query, (user_id, days_ahead))
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error getting user predictions: {e}")
            return []

    async def get_user_study_schedules(self, user_id: int, days: int = 7) -> list[dict[str, Any]]:
        """Get study schedules for a user"""
        try:
            query = """
            SELECT
                id, schedule_date, time_slots, total_planned_time,
                total_actual_time, completion_rate, is_optimized,
                optimization_notes, created_at
            FROM study_schedules
            WHERE user_id = %s
            AND schedule_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY schedule_date DESC
            """

            results = await self.db_manager.fetch_all(query, (user_id, days))
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error getting user study schedules: {e}")
            return []

    async def get_user_learning_patterns(self, user_id: int) -> list[dict[str, Any]]:
        """Get user's learning patterns"""
        try:
            query = """
            SELECT
                id, pattern_type, pattern_data, confidence_score,
                is_active, last_updated, created_at
            FROM user_learning_patterns
            WHERE user_id = %s AND is_active = TRUE
            ORDER BY confidence_score DESC, last_updated DESC
            """

            results = await self.db_manager.fetch_all(query, (user_id,))
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error getting user learning patterns: {e}")
            return []

    async def get_coach_interactions(self, user_id: int, days: int = 30) -> list[dict[str, Any]]:
        """Get AI coach interactions for a user"""
        try:
            query = """
            SELECT
                id, interaction_type, message_content, context_data,
                user_response, effectiveness_rating, created_at
            FROM ai_coach_interactions
            WHERE user_id = %s
            AND created_at >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY created_at DESC
            """

            results = await self.db_manager.fetch_all(query, (user_id, days))
            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error getting coach interactions: {e}")
            return []

    async def save_analytics_data(self, user_id: int, analytics_data: dict[str, Any]) -> bool:
        """Save analytics data for a user"""
        try:
            query = """
            INSERT INTO study_analytics
            (user_id, total_study_time, effective_study_time, study_sessions,
             subjects_studied, difficulty_levels, performance_scores, study_patterns,
             efficiency_score, focus_score, consistency_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, analysis_date)
            DO UPDATE SET
                total_study_time = EXCLUDED.total_study_time,
                effective_study_time = EXCLUDED.effective_study_time,
                study_sessions = EXCLUDED.study_sessions,
                subjects_studied = EXCLUDED.subjects_studied,
                difficulty_levels = EXCLUDED.difficulty_levels,
                performance_scores = EXCLUDED.performance_scores,
                study_patterns = EXCLUDED.study_patterns,
                efficiency_score = EXCLUDED.efficiency_score,
                focus_score = EXCLUDED.focus_score,
                consistency_score = EXCLUDED.consistency_score,
                updated_at = NOW()
            """

            await self.db_manager.execute(
                query,
                (
                    user_id,
                    analytics_data.get("total_study_time", 0),
                    analytics_data.get("effective_study_time", 0),
                    analytics_data.get("study_sessions", 0),
                    analytics_data.get("subjects_studied", []),
                    json.dumps(analytics_data.get("difficulty_levels", {})),
                    json.dumps(analytics_data.get("performance_scores", {})),
                    json.dumps(analytics_data.get("study_patterns", {})),
                    analytics_data.get("efficiency_score", 0.0),
                    analytics_data.get("focus_score", 0.0),
                    analytics_data.get("consistency_score", 0.0),
                ),
            )
            return True

        except Exception as e:
            logger.error(f"Error saving analytics data: {e}")
            return False

    async def save_recommendation(self, user_id: int, recommendation_data: dict[str, Any]) -> bool:
        """Save AI recommendation"""
        try:
            query = """
            INSERT INTO ai_recommendations
            (user_id, recommendation_type, recommendation_data, priority_level, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            """

            await self.db_manager.execute(
                query,
                (
                    user_id,
                    recommendation_data.get("recommendation_type"),
                    json.dumps(recommendation_data.get("data", {})),
                    recommendation_data.get("priority_level", 1),
                    recommendation_data.get("expires_at"),
                ),
            )
            return True

        except Exception as e:
            logger.error(f"Error saving recommendation: {e}")
            return False

    async def save_learning_path(self, user_id: int, path_data: dict[str, Any]) -> bool:
        """Save learning path"""
        try:
            query = """
            INSERT INTO learning_paths
            (user_id, path_name, path_description, subjects_sequence,
             difficulty_progression, estimated_duration, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            await self.db_manager.execute(
                query,
                (
                    user_id,
                    path_data.get("path_name"),
                    path_data.get("path_description"),
                    json.dumps(path_data.get("subjects_sequence", [])),
                    json.dumps(path_data.get("difficulty_progression", {})),
                    path_data.get("estimated_duration", 0),
                    path_data.get("is_active", True),
                ),
            )
            return True

        except Exception as e:
            logger.error(f"Error saving learning path: {e}")
            return False

    async def save_prediction(self, user_id: int, prediction_data: dict[str, Any]) -> bool:
        """Save performance prediction"""
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
                    prediction_data.get("prediction_type"),
                    prediction_data.get("subject"),
                    prediction_data.get("predicted_value", 0.0),
                    prediction_data.get("confidence_level", 0.0),
                    json.dumps(prediction_data.get("prediction_data", {})),
                    prediction_data.get("target_date"),
                ),
            )
            return True

        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return False

    async def save_coach_interaction(self, user_id: int, interaction_data: dict[str, Any]) -> bool:
        """Save coach interaction"""
        try:
            query = """
            INSERT INTO ai_coach_interactions
            (user_id, interaction_type, message_content, context_data,
             user_response, effectiveness_rating)
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            await self.db_manager.execute(
                query,
                (
                    user_id,
                    interaction_data.get("interaction_type"),
                    interaction_data.get("message_content"),
                    json.dumps(interaction_data.get("context_data", {})),
                    interaction_data.get("user_response"),
                    interaction_data.get("effectiveness_rating"),
                ),
            )
            return True

        except Exception as e:
            logger.error(f"Error saving coach interaction: {e}")
            return False

    async def update_recommendation_status(self, rec_id: int, user_id: int, status: str) -> bool:
        """Update recommendation status"""
        try:
            query = """
            UPDATE ai_recommendations
            SET is_active = FALSE, is_accepted = %s, acceptance_date = NOW()
            WHERE id = %s AND user_id = %s
            """

            is_accepted = status == "accepted"
            await self.db_manager.execute(query, (is_accepted, rec_id, user_id))
            return True

        except Exception as e:
            logger.error(f"Error updating recommendation status: {e}")
            return False

    async def get_analytics_trends(self, user_id: int, days: int = 30) -> dict[str, Any]:
        """Get analytics trends for a user"""
        try:
            query = """
            SELECT
                analysis_date,
                total_study_time,
                effective_study_time,
                efficiency_score,
                focus_score,
                consistency_score
            FROM study_analytics
            WHERE user_id = %s
            AND analysis_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY analysis_date ASC
            """

            results = await self.db_manager.fetch_all(query, (user_id, days))

            if not results:
                return {}

            trends = {
                "dates": [row["analysis_date"].strftime("%Y-%m-%d") for row in results],
                "study_time": [row["total_study_time"] for row in results],
                "efficiency": [float(row["efficiency_score"]) for row in results],
                "focus": [float(row["focus_score"]) for row in results],
                "consistency": [float(row["consistency_score"]) for row in results],
            }

            return trends

        except Exception as e:
            logger.error(f"Error getting analytics trends: {e}")
            return {}

    async def get_system_analytics(self) -> dict[str, Any]:
        """Get system-wide analytics"""
        try:
            # Total users with AI coach
            total_users_query = """
            SELECT COUNT(DISTINCT user_id) as total_users
            FROM study_analytics
            """
            total_users_result = await self.db_manager.fetch_one(total_users_query)
            total_users = total_users_result["total_users"] if total_users_result else 0

            # Active recommendations
            active_recs_query = """
            SELECT COUNT(*) as active_recommendations
            FROM ai_recommendations
            WHERE is_active = TRUE
            """
            active_recs_result = await self.db_manager.fetch_one(active_recs_query)
            active_recommendations = (
                active_recs_result["active_recommendations"] if active_recs_result else 0
            )

            # Average efficiency
            avg_efficiency_query = """
            SELECT AVG(efficiency_score) as avg_efficiency
            FROM study_analytics
            WHERE analysis_date >= CURRENT_DATE - INTERVAL '7 days'
            """
            avg_efficiency_result = await self.db_manager.fetch_one(avg_efficiency_query)
            avg_efficiency = (
                float(avg_efficiency_result["avg_efficiency"])
                if avg_efficiency_result and avg_efficiency_result["avg_efficiency"]
                else 0.0
            )

            return {
                "total_users": total_users,
                "active_recommendations": active_recommendations,
                "average_efficiency": avg_efficiency,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting system analytics: {e}")
            return {}


# Global AI Queries instance
ai_queries = AIQueries()
