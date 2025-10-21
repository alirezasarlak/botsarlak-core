"""
🤖 SarlakBot v3.2.0 - AI Coach Integration
Main integration file for AI Coach system
"""

from telegram.ext import CallbackQueryHandler, CommandHandler

from ...utils.logging import logger
from ..main_menu.handler import main_menu_handler
from .analytics_handler import analytics_handler
from .coach_handler import ai_coach_handler
from .recommendations_handler import recommendations_handler
from .schedule_handler import schedule_handler


class AICoachIntegration:
    """AI Coach system integration"""

    def __init__(self):
        self.coach_handler = ai_coach_handler
        self.analytics_handler = analytics_handler
        self.recommendations_handler = recommendations_handler
        self.schedule_handler = schedule_handler
        self.main_menu_handler = main_menu_handler

    def get_handlers(self):
        """Get all AI Coach handlers"""
        return [
            # AI Coach main command
            CommandHandler("coach", self.coach_handler.coach_command),
            CommandHandler("ai", self.coach_handler.coach_command),
            CommandHandler("coach", self.coach_handler.coach_command),
            # AI Coach callbacks
            CallbackQueryHandler(
                self.coach_handler.coach_personal_callback, pattern="^coach_personal$"
            ),
            CallbackQueryHandler(
                self.coach_handler.coach_analytics_callback, pattern="^coach_analytics$"
            ),
            CallbackQueryHandler(
                self.coach_handler.coach_recommendations_callback, pattern="^coach_recommendations$"
            ),
            CallbackQueryHandler(
                self.coach_handler.coach_schedule_callback, pattern="^coach_schedule$"
            ),
            CallbackQueryHandler(
                self.coach_handler.coach_predictions_callback, pattern="^coach_predictions$"
            ),
            CallbackQueryHandler(self.coach_handler.back_to_coach_main, pattern="^coach_main$"),
            # Analytics callbacks
            CallbackQueryHandler(
                self.analytics_handler.show_detailed_analytics, pattern="^coach_detailed_stats$"
            ),
            CallbackQueryHandler(
                self.analytics_handler.show_progress_charts, pattern="^coach_charts$"
            ),
            CallbackQueryHandler(
                self.analytics_handler.show_subject_comparison, pattern="^coach_subject_comparison$"
            ),
            CallbackQueryHandler(
                self.analytics_handler.show_time_analysis, pattern="^coach_time_analysis$"
            ),
            CallbackQueryHandler(
                self.analytics_handler.show_strengths_analysis, pattern="^coach_strengths$"
            ),
            CallbackQueryHandler(
                self.analytics_handler.show_weaknesses_analysis, pattern="^coach_weaknesses$"
            ),
            # Recommendations callbacks
            CallbackQueryHandler(
                self.recommendations_handler.show_recommendation_detail, pattern="^coach_rec_"
            ),
            CallbackQueryHandler(
                self.recommendations_handler.accept_recommendation, pattern="^coach_accept_"
            ),
            CallbackQueryHandler(
                self.recommendations_handler.reject_recommendation, pattern="^coach_reject_"
            ),
            CallbackQueryHandler(
                self.recommendations_handler.generate_new_recommendations,
                pattern="^coach_generate_new$",
            ),
            CallbackQueryHandler(
                self.recommendations_handler.show_implementation_guide, pattern="^coach_detail_"
            ),
            # Schedule callbacks
            CallbackQueryHandler(
                self.schedule_handler.show_today_schedule, pattern="^coach_today_schedule$"
            ),
            CallbackQueryHandler(
                self.schedule_handler.show_week_schedule, pattern="^coach_week_schedule$"
            ),
            CallbackQueryHandler(
                self.schedule_handler.show_optimal_times, pattern="^coach_optimal_times$"
            ),
            CallbackQueryHandler(
                self.schedule_handler.regenerate_schedule, pattern="^coach_regenerate_schedule$"
            ),
            # Back to main menu
            CallbackQueryHandler(self.main_menu_handler.show_main_menu, pattern="^back_to_main$"),
        ]

    async def setup_ai_coach_system(self):
        """Setup AI Coach system"""
        try:
            logger.info("🤖 Setting up AI Coach system...")

            # Initialize AI Coach service
            from ...services.ai_coach_service import ai_coach_service

            # Test database connection
            test_connection = await ai_coach_service.db_manager.fetch_one("SELECT 1")
            if not test_connection:
                logger.error("❌ AI Coach database connection failed")
                return False

            logger.info("✅ AI Coach system setup complete")
            return True

        except Exception as e:
            logger.error(f"❌ Error setting up AI Coach system: {e}")
            return False

    async def run_ai_coach_analysis(self, user_id: int):
        """Run AI Coach analysis for a user"""
        try:
            from ...services.ai_coach_service import ai_coach_service

            # Get user analytics
            analytics = await ai_coach_service.get_user_analytics(user_id)
            if not analytics:
                logger.info(f"No analytics data for user {user_id}")
                return False

            # Generate recommendations
            recommendations = await ai_coach_service.generate_recommendations(user_id)

            # Save recommendations
            for rec in recommendations:
                await ai_coach_service.save_recommendation(user_id, rec)

            # Log interaction
            await ai_coach_service.log_coach_interaction(
                user_id,
                ai_coach_service.InteractionType.ANALYSIS,
                f"AI Coach analysis completed for user {user_id}",
            )

            logger.info(f"✅ AI Coach analysis completed for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error running AI Coach analysis: {e}")
            return False

    async def get_ai_coach_summary(self, user_id: int) -> dict:
        """Get AI Coach summary for a user"""
        try:
            from ...services.ai_coach_service import ai_coach_service

            summary = await ai_coach_service.get_user_ai_coach_summary(user_id)
            return summary

        except Exception as e:
            logger.error(f"❌ Error getting AI Coach summary: {e}")
            return {"error": "Failed to get AI Coach summary"}


# Global AI Coach Integration instance
ai_coach_integration = AICoachIntegration()
