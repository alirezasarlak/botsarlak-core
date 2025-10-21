"""
🤖 SarlakBot v3.2.0 - AI Coach Handler
AI-powered study coaching and personalized recommendations
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ...services.ai_coach_service import InteractionType, ai_coach_service
from ...utils.logging import logger
from ...utils.navigation import create_back_button

# Conversation states
COACH_MAIN = "coach_main"
COACH_ANALYTICS = "coach_analytics"
COACH_RECOMMENDATIONS = "coach_recommendations"
COACH_SCHEDULE = "coach_schedule"
COACH_PREDICTIONS = "coach_predictions"


class AICoachHandler:
    """AI Coach Handler for personalized study coaching"""

    def __init__(self):
        self.service = ai_coach_service

    async def coach_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /coach command - AI Coach main menu"""
        try:
            user_id = update.effective_user.id

            # Get AI coach summary
            summary = await self.service.get_user_ai_coach_summary(user_id)

            if "error" in summary:
                await update.message.reply_text(
                    "❌ متأسفانه در حال حاضر نمی‌تونم بهت کمک کنم. لطفاً بعداً تلاش کن.",
                    reply_markup=create_back_button(),
                )
                return COACH_MAIN

            # Create AI Coach main menu
            keyboard = [
                [InlineKeyboardButton("🤖 مربی شخصی", callback_data="coach_personal")],
                [InlineKeyboardButton("📊 آمار پیشرفته", callback_data="coach_analytics")],
                [InlineKeyboardButton("💡 توصیه‌های هوشمند", callback_data="coach_recommendations")],
                [InlineKeyboardButton("📅 برنامه‌ریزی", callback_data="coach_schedule")],
                [InlineKeyboardButton("🔮 پیش‌بینی عملکرد", callback_data="coach_predictions")],
                [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_to_main")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Create coach message
            coach_message = f"""
🤖 **مربی هوشمند SarlakBot**

سلام! من مربی شخصی‌ت هستم و اینجا هستم تا کمکت کنم بهترین عملکرد رو داشته باشی.

📊 **وضعیت فعلی:**
• ⏱️ زمان مطالعه: {summary['analytics']['total_study_time']} دقیقه
• ⭐ امتیاز کارایی: {summary['analytics']['efficiency_score']:.1f}/100
• 🎯 امتیاز تمرکز: {summary['analytics']['focus_score']:.1f}/100
• 🔄 امتیاز ثبات: {summary['analytics']['consistency_score']:.1f}/100

💡 **توصیه‌های فعال:** {summary['recommendations_count']} عدد

{summary['coach_message']}

چطور می‌تونم کمکت کنم؟
            """

            await update.message.reply_text(
                coach_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

            # Log interaction
            await self.service.log_coach_interaction(
                user_id, InteractionType.RECOMMENDATION, "User accessed AI Coach"
            )

            return COACH_MAIN

        except Exception as e:
            logger.error(f"Error in coach_command: {e}")
            await update.message.reply_text(
                "❌ خطا در دسترسی به مربی هوشمند. لطفاً دوباره تلاش کن.",
                reply_markup=create_back_button(),
            )
            return COACH_MAIN

    async def coach_personal_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle personal coach callback"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            # Get personalized coach message
            coach_message = await self.service.get_coach_personality_message(
                user_id, InteractionType.ENCOURAGEMENT
            )

            # Get study patterns
            patterns = await self.service.analyze_study_patterns(user_id)

            keyboard = [
                [InlineKeyboardButton("💬 گفتگو با مربی", callback_data="coach_chat")],
                [InlineKeyboardButton("📈 تحلیل شخصی", callback_data="coach_analysis")],
                [InlineKeyboardButton("🎯 اهداف شخصی", callback_data="coach_goals")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_main")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            personal_message = f"""
🤖 **مربی شخصی شما**

{coach_message}

📊 **تحلیل شخصی:**
• روند کارایی: {patterns.get('efficiency_trend', 'در حال بررسی')}
• سطح تمرکز: {patterns.get('focus_level', 'در حال بررسی')}
• ثبات مطالعه: {patterns.get('consistency', 'در حال بررسی')}

🎯 **موضوعات مورد علاقه:**
{', '.join(patterns.get('preferred_subjects', ['در حال بررسی']))}

💡 **توصیه‌های شخصی:**
{chr(10).join(f"• {rec}" for rec in patterns.get('recommendations', ['در حال تحلیل']))}
            """

            await query.edit_message_text(
                personal_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in coach_personal_callback: {e}")
            await query.edit_message_text("❌ خطا در دسترسی به مربی شخصی. لطفاً دوباره تلاش کن.")

    async def coach_analytics_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle analytics callback"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            # Get detailed analytics
            analytics = await self.service.get_user_analytics(user_id)

            if not analytics:
                await query.edit_message_text(
                    "📊 هنوز داده‌ای برای تحلیل وجود نداره. بعد از چند جلسه مطالعه دوباره مراجعه کن.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔙 بازگشت", callback_data="coach_main")]]
                    ),
                )
                return

            keyboard = [
                [InlineKeyboardButton("📈 نمودار پیشرفت", callback_data="coach_charts")],
                [InlineKeyboardButton("📊 آمار تفصیلی", callback_data="coach_detailed_stats")],
                [InlineKeyboardButton("🔍 تحلیل الگوها", callback_data="coach_patterns")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_main")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            analytics_message = f"""
📊 **آمار پیشرفته مطالعه**

⏱️ **زمان‌بندی:**
• زمان کل: {analytics.total_study_time} دقیقه
• زمان مؤثر: {analytics.effective_study_time} دقیقه
• جلسات: {analytics.study_sessions} جلسه

📈 **امتیازات:**
• کارایی: {analytics.efficiency_score:.1f}/100
• تمرکز: {analytics.focus_score:.1f}/100
• ثبات: {analytics.consistency_score:.1f}/100

📚 **موضوعات:**
{', '.join(analytics.subjects_studied) if analytics.subjects_studied else 'هنوز موضوعی مطالعه نشده'}

🎯 **تحلیل عملکرد:**
• بهترین موضوع: {max(analytics.performance_scores.items(), key=lambda x: x[1])[0] if analytics.performance_scores else 'نامشخص'}
• نیاز به بهبود: {min(analytics.performance_scores.items(), key=lambda x: x[1])[0] if analytics.performance_scores else 'نامشخص'}
            """

            await query.edit_message_text(
                analytics_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in coach_analytics_callback: {e}")
            await query.edit_message_text("❌ خطا در دسترسی به آمار. لطفاً دوباره تلاش کن.")

    async def coach_recommendations_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle recommendations callback"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            # Get active recommendations
            recommendations = await self.service.get_active_recommendations(user_id)

            if not recommendations:
                # Generate new recommendations
                new_recommendations = await self.service.generate_recommendations(user_id)
                for rec in new_recommendations:
                    await self.service.save_recommendation(user_id, rec)

                recommendations = await self.service.get_active_recommendations(user_id)

            keyboard = []
            for i, rec in enumerate(recommendations[:5]):  # Show max 5 recommendations
                priority_emoji = (
                    "🔴"
                    if rec["priority_level"] >= 4
                    else "🟡" if rec["priority_level"] >= 3 else "🟢"
                )
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"{priority_emoji} {rec['recommendation_type']}",
                            callback_data=f"coach_rec_{rec['id']}",
                        )
                    ]
                )

            keyboard.append(
                [InlineKeyboardButton("🔄 تولید توصیه جدید", callback_data="coach_generate_new")]
            )
            keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="coach_main")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            recommendations_message = f"""
💡 **توصیه‌های هوشمند**

تعداد توصیه‌های فعال: {len(recommendations)}

🎯 **اولویت‌بندی:**
🔴 اولویت بالا (فوری)
🟡 اولویت متوسط (مهم)
🟢 اولویت پایین (اختیاری)

برای مشاهده جزئیات هر توصیه، روی آن کلیک کن.
            """

            await query.edit_message_text(
                recommendations_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in coach_recommendations_callback: {e}")
            await query.edit_message_text("❌ خطا در دسترسی به توصیه‌ها. لطفاً دوباره تلاش کن.")

    async def coach_schedule_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle schedule callback"""
        try:
            query = update.callback_query
            await query.answer()

            keyboard = [
                [InlineKeyboardButton("📅 برنامه امروز", callback_data="coach_today_schedule")],
                [InlineKeyboardButton("📆 برنامه هفته", callback_data="coach_week_schedule")],
                [InlineKeyboardButton("⏰ زمان‌بندی بهینه", callback_data="coach_optimal_times")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_main")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            schedule_message = """
📅 **برنامه‌ریزی هوشمند**

من می‌تونم بهت کمک کنم:
• برنامه روزانه مطالعه
• برنامه هفتگی
• بهترین زمان‌ها
• استراحت‌های بهینه

چه نوع برنامه‌ای می‌خوای؟
            """

            await query.edit_message_text(schedule_message, reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Error in coach_schedule_callback: {e}")
            await query.edit_message_text("❌ خطا در دسترسی به برنامه‌ریزی. لطفاً دوباره تلاش کن.")

    async def coach_predictions_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle predictions callback"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            # Get performance predictions
            subjects = ["ریاضی", "فیزیک", "شیمی", "زیست"]
            predictions = []

            for subject in subjects:
                prediction = await self.service.predict_performance(
                    user_id, subject, date.today() + timedelta(days=30)
                )
                if prediction:
                    predictions.append(prediction)
                    await self.service.save_prediction(user_id, prediction)

            keyboard = []
            for pred in predictions:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"🔮 {pred.subject}: {pred.predicted_value:.1f}%",
                            callback_data=f"coach_pred_{pred.subject}",
                        )
                    ]
                )

            keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="coach_main")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            predictions_message = f"""
🔮 **پیش‌بینی عملکرد**

پیش‌بینی‌های 30 روز آینده:

{chr(10).join(f"• {pred.subject}: {pred.predicted_value:.1f}% (اطمینان: {pred.confidence_level:.1f}%)" for pred in predictions)}

💡 این پیش‌بینی‌ها بر اساس الگوهای مطالعه‌ات محاسبه شده‌اند.
            """

            await query.edit_message_text(
                predictions_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in coach_predictions_callback: {e}")
            await query.edit_message_text("❌ خطا در دسترسی به پیش‌بینی‌ها. لطفاً دوباره تلاش کن.")

    async def back_to_coach_main(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Return to AI Coach main menu"""
        try:
            query = update.callback_query
            await query.answer()

            # Reset to coach main menu
            await self.coach_command(update, context)

        except Exception as e:
            logger.error(f"Error in back_to_coach_main: {e}")


# Create AI Coach handler instance
ai_coach_handler = AICoachHandler()
