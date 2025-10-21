"""
💡 SarlakBot v3.2.0 - Recommendations Handler
AI-powered study recommendations and personalized suggestions
"""

import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ...services.ai_coach_service import InteractionType, ai_coach_service
from ...utils.logging import logger


class RecommendationsHandler:
    """Recommendations Handler for AI-powered study suggestions"""

    def __init__(self):
        self.service = ai_coach_service

    async def show_recommendation_detail(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed recommendation information"""
        try:
            query = update.callback_query
            await query.answer()

            # Extract recommendation ID from callback data
            callback_data = query.data
            if not callback_data.startswith("coach_rec_"):
                await query.edit_message_text("❌ خطا در دریافت توصیه.")
                return

            rec_id = int(callback_data.split("_")[2])
            user_id = update.effective_user.id

            # Get recommendation details
            recommendations = await self.service.get_active_recommendations(user_id)
            recommendation = next((rec for rec in recommendations if rec["id"] == rec_id), None)

            if not recommendation:
                await query.edit_message_text(
                    "❌ توصیه مورد نظر یافت نشد.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔙 بازگشت", callback_data="coach_recommendations")]]
                    ),
                )
                return

            # Parse recommendation data
            rec_data = json.loads(recommendation["recommendation_data"])

            keyboard = [
                [InlineKeyboardButton("✅ قبول", callback_data=f"coach_accept_{rec_id}")],
                [InlineKeyboardButton("❌ رد", callback_data=f"coach_reject_{rec_id}")],
                [InlineKeyboardButton("💡 جزئیات بیشتر", callback_data=f"coach_detail_{rec_id}")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_recommendations")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Create detailed message based on recommendation type
            detail_message = self._create_recommendation_detail_message(recommendation, rec_data)

            await query.edit_message_text(
                detail_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in show_recommendation_detail: {e}")
            await query.edit_message_text("❌ خطا در نمایش جزئیات توصیه. لطفاً دوباره تلاش کن.")

    def _create_recommendation_detail_message(self, recommendation: dict, rec_data: dict) -> str:
        """Create detailed message for recommendation"""
        rec_type = recommendation["recommendation_type"]
        priority = recommendation["priority_level"]

        priority_emoji = "🔴" if priority >= 4 else "🟡" if priority >= 3 else "🟢"
        priority_text = "فوری" if priority >= 4 else "مهم" if priority >= 3 else "اختیاری"

        if rec_type == "study_plan":
            return f"""
📚 **توصیه: برنامه مطالعه**

{priority_emoji} **اولویت:** {priority_text}

📋 **جزئیات:**
• مدت زمان پیشنهادی: {rec_data.get('suggested_duration', 'نامشخص')} دقیقه
• فرکانس استراحت: هر {rec_data.get('break_frequency', 'نامشخص')} دقیقه
• موضوعات: {', '.join(rec_data.get('subjects', []))}

💡 **چرا این توصیه؟**
بر اساس تحلیل الگوهای مطالعه‌ات، این برنامه می‌تونه کاراییت رو بهبود بده.

🎯 **نحوه اجرا:**
1. زمان‌بندی مشخص کن
2. عوامل حواس‌پرتی رو حذف کن
3. استراحت‌های منظم داشته باش
4. پیشرفت‌ت رو پیگیری کن
            """

        elif rec_type == "subject_priority":
            subjects = rec_data.get("priority_subjects", [])
            return f"""
🎯 **توصیه: اولویت‌بندی موضوعات**

{priority_emoji} **اولویت:** {priority_text}

📋 **جزئیات:**
• موضوعات اولویت: {', '.join(subjects)}
• دلیل: عملکرد ضعیف‌تر در این موضوعات
• هدف: بهبود نمرات و درک بهتر

💡 **چرا این توصیه؟**
تحلیل عملکردت نشون می‌ده که این موضوعات نیاز به توجه بیشتری دارند.

🎯 **نحوه اجرا:**
1. زمان بیشتری برای این موضوعات اختصاص بده
2. از منابع مختلف استفاده کن
3. تمرین‌های اضافی انجام بده
4. پیشرفت‌ت رو هفتگی بررسی کن
            """

        elif rec_type == "break_schedule":
            return f"""
⏰ **توصیه: برنامه استراحت**

{priority_emoji} **اولویت:** {priority_text}

📋 **جزئیات:**
• مدت استراحت: {rec_data.get('break_duration', 'نامشخص')} دقیقه
• فرکانس: هر {rec_data.get('break_frequency', 'نامشخص')} دقیقه
• فعالیت‌های استراحت: {', '.join(rec_data.get('activities', []))}

💡 **چرا این توصیه؟**
استراحت‌های منظم باعث بهبود تمرکز و کارایی می‌شه.

🎯 **نحوه اجرا:**
1. تایمر تنظیم کن
2. در زمان استراحت از مطالعه دور باش
3. فعالیت‌های سبک انجام بده
4. به چشمانت استراحت بده
            """

        else:
            return f"""
💡 **توصیه شخصی‌سازی شده**

{priority_emoji} **اولویت:** {priority_text}

📋 **جزئیات:**
• نوع: {rec_type}
• داده‌ها: {json.dumps(rec_data, ensure_ascii=False, indent=2)}

💡 **این توصیه بر اساس تحلیل الگوهای مطالعه‌ات تولید شده.**
            """

    async def accept_recommendation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Accept a recommendation"""
        try:
            query = update.callback_query
            await query.answer()

            # Extract recommendation ID
            callback_data = query.data
            rec_id = int(callback_data.split("_")[2])
            user_id = update.effective_user.id

            # Update recommendation status
            await self._update_recommendation_status(rec_id, user_id, "accepted")

            # Log interaction
            await self.service.log_coach_interaction(
                user_id, InteractionType.RECOMMENDATION, f"User accepted recommendation {rec_id}"
            )

            keyboard = [
                [InlineKeyboardButton("💡 توصیه بعدی", callback_data="coach_recommendations")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_main")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "✅ **توصیه قبول شد!**\n\n"
                "عالی! حالا می‌تونی این توصیه رو اجرا کنی. "
                "من پیشرفت‌ت رو پیگیری می‌کنم و در صورت نیاز راهنمایی‌های بیشتری می‌دم.\n\n"
                "💪 موفق باشی!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
            )

        except Exception as e:
            logger.error(f"Error in accept_recommendation: {e}")
            await query.edit_message_text("❌ خطا در قبول توصیه. لطفاً دوباره تلاش کن.")

    async def reject_recommendation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reject a recommendation"""
        try:
            query = update.callback_query
            await query.answer()

            # Extract recommendation ID
            callback_data = query.data
            rec_id = int(callback_data.split("_")[2])
            user_id = update.effective_user.id

            # Update recommendation status
            await self._update_recommendation_status(rec_id, user_id, "rejected")

            # Log interaction
            await self.service.log_coach_interaction(
                user_id, InteractionType.RECOMMENDATION, f"User rejected recommendation {rec_id}"
            )

            keyboard = [
                [InlineKeyboardButton("💡 توصیه جدید", callback_data="coach_generate_new")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_recommendations")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "❌ **توصیه رد شد**\n\n"
                "متوجه شدم! این توصیه مناسبت نبوده. "
                "می‌تونم توصیه‌های جدیدی بر اساس نیازهایت تولید کنم.\n\n"
                "چه نوع توصیه‌ای می‌خوای؟",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
            )

        except Exception as e:
            logger.error(f"Error in reject_recommendation: {e}")
            await query.edit_message_text("❌ خطا در رد توصیه. لطفاً دوباره تلاش کن.")

    async def generate_new_recommendations(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Generate new recommendations for user"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            # Generate new recommendations
            new_recommendations = await self.service.generate_recommendations(user_id)

            if not new_recommendations:
                await query.edit_message_text(
                    "💡 در حال حاضر توصیه جدیدی ندارم. " "بعد از چند جلسه مطالعه دوباره مراجعه کن.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔙 بازگشت", callback_data="coach_recommendations")]]
                    ),
                )
                return

            # Save new recommendations
            saved_count = 0
            for rec in new_recommendations:
                if await self.service.save_recommendation(user_id, rec):
                    saved_count += 1

            keyboard = [
                [InlineKeyboardButton("💡 مشاهده توصیه‌ها", callback_data="coach_recommendations")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_main")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"🎉 **توصیه‌های جدید تولید شد!**\n\n"
                f"✅ {saved_count} توصیه جدید بر اساس آخرین تحلیل‌ها تولید شد.\n\n"
                f"این توصیه‌ها شخصی‌سازی شده‌اند و بر اساس الگوهای مطالعه‌ات طراحی شده‌اند.\n\n"
                f"💡 برای مشاهده توصیه‌ها روی دکمه زیر کلیک کن.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
            )

        except Exception as e:
            logger.error(f"Error in generate_new_recommendations: {e}")
            await query.edit_message_text("❌ خطا در تولید توصیه‌های جدید. لطفاً دوباره تلاش کن.")

    async def show_implementation_guide(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show implementation guide for recommendations"""
        try:
            query = update.callback_query
            await query.answer()

            keyboard = [
                [
                    InlineKeyboardButton(
                        "📚 راهنمای برنامه مطالعه", callback_data="guide_study_plan"
                    )
                ],
                [InlineKeyboardButton("🎯 راهنمای اولویت‌بندی", callback_data="guide_priorities")],
                [InlineKeyboardButton("⏰ راهنمای استراحت", callback_data="guide_breaks")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_recommendations")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            guide_message = """
📖 **راهنمای اجرای توصیه‌ها**

من اینجا هستم تا کمکت کنم توصیه‌ها رو به بهترین شکل اجرا کنی.

🎯 **نکات مهم:**
• هر توصیه رو قدم به قدم اجرا کن
• عجله نکن و صبور باش
• پیشرفت‌ت رو پیگیری کن
• در صورت مشکل، کمک بخواه

💡 **راهنماهای موجود:**
• برنامه مطالعه مؤثر
• اولویت‌بندی موضوعات
• استراحت‌های بهینه

کدوم راهنما رو می‌خوای؟
            """

            await query.edit_message_text(guide_message, reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Error in show_implementation_guide: {e}")
            await query.edit_message_text("❌ خطا در نمایش راهنما. لطفاً دوباره تلاش کن.")

    async def _update_recommendation_status(self, rec_id: int, user_id: int, status: str):
        """Update recommendation status in database"""
        try:
            query = """
            UPDATE ai_recommendations
            SET is_active = FALSE, is_accepted = %s, acceptance_date = NOW()
            WHERE id = %s AND user_id = %s
            """

            is_accepted = status == "accepted"
            await self.service.db_manager.execute(query, (is_accepted, rec_id, user_id))

        except Exception as e:
            logger.error(f"Error updating recommendation status: {e}")


# Create Recommendations handler instance
recommendations_handler = RecommendationsHandler()
