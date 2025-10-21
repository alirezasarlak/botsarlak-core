"""
📊 SarlakBot v3.2.0 - Analytics Handler
Advanced study analytics and performance tracking
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ...services.ai_coach_service import ai_coach_service
from ...utils.logging import logger


class AnalyticsHandler:
    """Analytics Handler for advanced study analytics"""

    def __init__(self):
        self.service = ai_coach_service

    async def show_detailed_analytics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed analytics dashboard"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            # Get comprehensive analytics
            analytics = await self.service.get_user_analytics(user_id, days=30)

            if not analytics:
                await query.edit_message_text(
                    "📊 هنوز داده‌ای برای تحلیل وجود نداره. بعد از چند جلسه مطالعه دوباره مراجعه کن.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔙 بازگشت", callback_data="coach_analytics")]]
                    ),
                )
                return

            # Calculate additional metrics
            daily_average = analytics.total_study_time / 30 if analytics.total_study_time > 0 else 0
            efficiency_percentage = (
                (analytics.effective_study_time / analytics.total_study_time * 100)
                if analytics.total_study_time > 0
                else 0
            )

            keyboard = [
                [InlineKeyboardButton("📈 نمودار پیشرفت", callback_data="coach_charts")],
                [
                    InlineKeyboardButton(
                        "📊 مقایسه موضوعات", callback_data="coach_subject_comparison"
                    )
                ],
                [InlineKeyboardButton("⏰ تحلیل زمان‌بندی", callback_data="coach_time_analysis")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_analytics")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            detailed_message = f"""
📊 **آمار تفصیلی مطالعه**

⏱️ **زمان‌بندی:**
• زمان کل: {analytics.total_study_time:,} دقیقه ({analytics.total_study_time//60:.1f} ساعت)
• زمان مؤثر: {analytics.effective_study_time:,} دقیقه ({analytics.effective_study_time//60:.1f} ساعت)
• کارایی: {efficiency_percentage:.1f}%
• میانگین روزانه: {daily_average:.1f} دقیقه

📈 **امتیازات عملکرد:**
• کارایی: {analytics.efficiency_score:.1f}/100
• تمرکز: {analytics.focus_score:.1f}/100
• ثبات: {analytics.consistency_score:.1f}/100

📚 **موضوعات مطالعه:**
{chr(10).join(f"• {subject}" for subject in analytics.subjects_studied) if analytics.subjects_studied else "• هنوز موضوعی مطالعه نشده"}

🎯 **عملکرد موضوعات:**
{chr(10).join(f"• {subject}: {score:.1f}%" for subject, score in analytics.performance_scores.items()) if analytics.performance_scores else "• داده‌ای موجود نیست"}

📊 **الگوهای مطالعه:**
• جلسات: {analytics.study_sessions} جلسه
• میانگین جلسه: {analytics.total_study_time/analytics.study_sessions:.1f} دقیقه
• موضوعات مختلف: {len(analytics.subjects_studied)} موضوع
            """

            await query.edit_message_text(
                detailed_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in show_detailed_analytics: {e}")
            await query.edit_message_text("❌ خطا در نمایش آمار تفصیلی. لطفاً دوباره تلاش کن.")

    async def show_progress_charts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show progress charts and visualizations"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            # Get analytics for chart generation
            analytics = await self.service.get_user_analytics(user_id, days=7)

            if not analytics:
                await query.edit_message_text(
                    "📈 داده‌ای برای نمایش نمودار وجود نداره.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔙 بازگشت", callback_data="coach_analytics")]]
                    ),
                )
                return

            # Create simple text-based charts
            efficiency_bar = self._create_progress_bar(analytics.efficiency_score)
            focus_bar = self._create_progress_bar(analytics.focus_score)
            consistency_bar = self._create_progress_bar(analytics.consistency_score)

            keyboard = [
                [InlineKeyboardButton("📊 نمودار هفتگی", callback_data="coach_weekly_chart")],
                [InlineKeyboardButton("📈 نمودار ماهانه", callback_data="coach_monthly_chart")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_analytics")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            charts_message = f"""
📈 **نمودارهای پیشرفت**

🎯 **امتیاز کارایی:**
{efficiency_bar} {analytics.efficiency_score:.1f}%

🎯 **امتیاز تمرکز:**
{focus_bar} {analytics.focus_score:.1f}%

🎯 **امتیاز ثبات:**
{consistency_bar} {analytics.consistency_score:.1f}%

📊 **تحلیل کلی:**
• وضعیت: {'عالی' if analytics.efficiency_score > 80 else 'خوب' if analytics.efficiency_score > 60 else 'نیاز به بهبود'}
• روند: {'صعودی' if analytics.consistency_score > 80 else 'ثابت' if analytics.consistency_score > 60 else 'نزولی'}
• توصیه: {'ادامه بده!' if analytics.efficiency_score > 80 else 'کمی بیشتر تلاش کن' if analytics.efficiency_score > 60 else 'برنامه‌ات رو بهبود بده'}
            """

            await query.edit_message_text(
                charts_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in show_progress_charts: {e}")
            await query.edit_message_text("❌ خطا در نمایش نمودارها. لطفاً دوباره تلاش کن.")

    async def show_subject_comparison(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show subject performance comparison"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            analytics = await self.service.get_user_analytics(user_id)

            if not analytics or not analytics.performance_scores:
                await query.edit_message_text(
                    "📊 داده‌ای برای مقایسه موضوعات وجود نداره.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔙 بازگشت", callback_data="coach_analytics")]]
                    ),
                )
                return

            # Sort subjects by performance
            sorted_subjects = sorted(
                analytics.performance_scores.items(), key=lambda x: x[1], reverse=True
            )

            keyboard = [
                [InlineKeyboardButton("🎯 تحلیل نقاط قوت", callback_data="coach_strengths")],
                [InlineKeyboardButton("⚠️ تحلیل نقاط ضعف", callback_data="coach_weaknesses")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_analytics")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            comparison_message = f"""
📊 **مقایسه موضوعات**

🏆 **رتبه‌بندی عملکرد:**
{chr(10).join(f"{i+1}. {subject}: {self._create_progress_bar(score)} {score:.1f}%" for i, (subject, score) in enumerate(sorted_subjects))}

📈 **تحلیل:**
• بهترین موضوع: {sorted_subjects[0][0]} ({sorted_subjects[0][1]:.1f}%)
• ضعیف‌ترین موضوع: {sorted_subjects[-1][0]} ({sorted_subjects[-1][1]:.1f}%)
• تفاوت عملکرد: {sorted_subjects[0][1] - sorted_subjects[-1][1]:.1f}%

💡 **توصیه:**
• روی {sorted_subjects[-1][0]} بیشتر تمرکز کن
• {sorted_subjects[0][0]} رو به عنوان نقطه قوت حفظ کن
• تعادل بین موضوعات رو حفظ کن
            """

            await query.edit_message_text(
                comparison_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in show_subject_comparison: {e}")
            await query.edit_message_text("❌ خطا در مقایسه موضوعات. لطفاً دوباره تلاش کن.")

    async def show_time_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show time analysis and optimization suggestions"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            analytics = await self.service.get_user_analytics(user_id)

            if not analytics:
                await query.edit_message_text(
                    "⏰ داده‌ای برای تحلیل زمان‌بندی وجود نداره.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔙 بازگشت", callback_data="coach_analytics")]]
                    ),
                )
                return

            # Calculate time metrics
            total_hours = analytics.total_study_time / 60
            effective_hours = analytics.effective_study_time / 60
            efficiency_rate = (
                (analytics.effective_study_time / analytics.total_study_time * 100)
                if analytics.total_study_time > 0
                else 0
            )
            avg_session = (
                analytics.total_study_time / analytics.study_sessions
                if analytics.study_sessions > 0
                else 0
            )

            keyboard = [
                [InlineKeyboardButton("⏰ زمان‌بندی بهینه", callback_data="coach_optimal_timing")],
                [InlineKeyboardButton("🔄 بهبود کارایی", callback_data="coach_efficiency_tips")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_analytics")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            time_analysis_message = f"""
⏰ **تحلیل زمان‌بندی**

📊 **آمار زمان:**
• زمان کل: {total_hours:.1f} ساعت
• زمان مؤثر: {effective_hours:.1f} ساعت
• کارایی: {efficiency_rate:.1f}%
• میانگین جلسه: {avg_session:.1f} دقیقه

🎯 **تحلیل کارایی:**
• وضعیت: {'عالی' if efficiency_rate > 80 else 'خوب' if efficiency_rate > 60 else 'نیاز به بهبود'}
• توصیه: {'ادامه بده!' if efficiency_rate > 80 else 'زمان‌بندی‌ت رو بهبود بده' if efficiency_rate > 60 else 'برنامه‌ریزی جدید کن'}

💡 **نکات بهینه‌سازی:**
• جلسات کوتاه‌تر و متمرکزتر داشته باش
• استراحت‌های منظم بین جلسات
• زمان‌های اوج انرژی‌ت رو شناسایی کن
• عوامل حواس‌پرتی رو حذف کن
            """

            await query.edit_message_text(
                time_analysis_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in show_time_analysis: {e}")
            await query.edit_message_text("❌ خطا در تحلیل زمان‌بندی. لطفاً دوباره تلاش کن.")

    def _create_progress_bar(self, value: float, length: int = 10) -> str:
        """Create a text-based progress bar"""
        filled = int((value / 100) * length)
        empty = length - filled
        return "█" * filled + "░" * empty

    async def show_strengths_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show strengths analysis"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            analytics = await self.service.get_user_analytics(user_id)

            if not analytics or not analytics.performance_scores:
                await query.edit_message_text(
                    "🎯 داده‌ای برای تحلیل نقاط قوت وجود نداره.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🔙 بازگشت", callback_data="coach_subject_comparison"
                                )
                            ]
                        ]
                    ),
                )
                return

            # Find strengths (subjects with score > 70)
            strengths = [
                (subject, score)
                for subject, score in analytics.performance_scores.items()
                if score > 70
            ]

            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_subject_comparison")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            strengths_message = f"""
🎯 **تحلیل نقاط قوت**

🏆 **موضوعات قوی:**
{chr(10).join(f"• {subject}: {self._create_progress_bar(score)} {score:.1f}%" for subject, score in strengths) if strengths else "• هنوز نقطه قوت مشخصی نداره"}

💪 **توصیه‌ها:**
• نقاط قوتت رو حفظ کن
• از این موضوعات به عنوان پایه استفاده کن
• اعتماد به نفس‌ت رو بالا نگه دار
• این موفقیت‌ها رو جشن بگیر
            """

            await query.edit_message_text(
                strengths_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in show_strengths_analysis: {e}")
            await query.edit_message_text("❌ خطا در تحلیل نقاط قوت. لطفاً دوباره تلاش کن.")

    async def show_weaknesses_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show weaknesses analysis"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            analytics = await self.service.get_user_analytics(user_id)

            if not analytics or not analytics.performance_scores:
                await query.edit_message_text(
                    "⚠️ داده‌ای برای تحلیل نقاط ضعف وجود نداره.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🔙 بازگشت", callback_data="coach_subject_comparison"
                                )
                            ]
                        ]
                    ),
                )
                return

            # Find weaknesses (subjects with score < 60)
            weaknesses = [
                (subject, score)
                for subject, score in analytics.performance_scores.items()
                if score < 60
            ]

            keyboard = [
                [InlineKeyboardButton("💡 برنامه بهبود", callback_data="coach_improvement_plan")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_subject_comparison")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            weaknesses_message = f"""
⚠️ **تحلیل نقاط ضعف**

🔍 **موضوعات نیازمند بهبود:**
{chr(10).join(f"• {subject}: {self._create_progress_bar(score)} {score:.1f}%" for subject, score in weaknesses) if weaknesses else "• همه موضوعات در سطح خوبی هستند"}

💡 **برنامه بهبود:**
• زمان بیشتری برای این موضوعات اختصاص بده
• از منابع مختلف استفاده کن
• کمک بگیر (معلم، دوستان، منابع آنلاین)
• صبور باش و قدم به قدم پیش برو
• هر پیشرفت کوچکی رو جشن بگیر
            """

            await query.edit_message_text(
                weaknesses_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in show_weaknesses_analysis: {e}")
            await query.edit_message_text("❌ خطا در تحلیل نقاط ضعف. لطفاً دوباره تلاش کن.")


# Create Analytics handler instance
analytics_handler = AnalyticsHandler()
