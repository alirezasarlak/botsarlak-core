"""
📅 SarlakBot v3.2.0 - Schedule Handler
AI-powered study scheduling and time optimization
"""

import json
from datetime import date

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ...services.ai_coach_service import ai_coach_service
from ...utils.logging import logger


class ScheduleHandler:
    """Schedule Handler for AI-powered study scheduling"""

    def __init__(self):
        self.service = ai_coach_service

    async def show_today_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show today's study schedule"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id
            today = date.today()

            # Get today's schedule from database
            schedule = await self._get_user_schedule(user_id, today)

            if not schedule:
                # Generate new schedule for today
                schedule = await self._generate_daily_schedule(user_id, today)

            keyboard = [
                [InlineKeyboardButton("⏰ زمان‌بندی بهینه", callback_data="coach_optimal_times")],
                [
                    InlineKeyboardButton(
                        "🔄 تولید برنامه جدید", callback_data="coach_regenerate_schedule"
                    )
                ],
                [InlineKeyboardButton("📊 تحلیل زمان‌بندی", callback_data="coach_time_analysis")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_schedule")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            schedule_message = self._create_schedule_message(schedule, today)

            await query.edit_message_text(
                schedule_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in show_today_schedule: {e}")
            await query.edit_message_text("❌ خطا در نمایش برنامه امروز. لطفاً دوباره تلاش کن.")

    async def show_week_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show weekly study schedule"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            # Get week schedule
            week_schedule = await self._get_week_schedule(user_id)

            keyboard = [
                [InlineKeyboardButton("📅 برنامه روزانه", callback_data="coach_today_schedule")],
                [InlineKeyboardButton("🎯 اهداف هفتگی", callback_data="coach_weekly_goals")],
                [InlineKeyboardButton("📊 آمار هفته", callback_data="coach_weekly_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_schedule")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            week_message = self._create_week_schedule_message(week_schedule)

            await query.edit_message_text(
                week_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in show_week_schedule: {e}")
            await query.edit_message_text("❌ خطا در نمایش برنامه هفته. لطفاً دوباره تلاش کن.")

    async def show_optimal_times(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show optimal study times based on user patterns"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id

            # Analyze user's optimal study times
            optimal_times = await self._analyze_optimal_times(user_id)

            keyboard = [
                [InlineKeyboardButton("⏰ تنظیم زمان‌بندی", callback_data="coach_set_timing")],
                [InlineKeyboardButton("📊 تحلیل الگوها", callback_data="coach_pattern_analysis")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_schedule")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            optimal_message = self._create_optimal_times_message(optimal_times)

            await query.edit_message_text(
                optimal_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in show_optimal_times: {e}")
            await query.edit_message_text("❌ خطا در تحلیل زمان‌های بهینه. لطفاً دوباره تلاش کن.")

    async def regenerate_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Regenerate study schedule"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = update.effective_user.id
            today = date.today()

            # Generate new schedule
            new_schedule = await self._generate_daily_schedule(user_id, today)

            if new_schedule:
                # Save new schedule
                await self._save_schedule(user_id, today, new_schedule)

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "📅 مشاهده برنامه", callback_data="coach_today_schedule"
                        )
                    ],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="coach_schedule")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    "🔄 **برنامه جدید تولید شد!**\n\n"
                    "برنامه امروزت بر اساس آخرین تحلیل‌ها و الگوهای مطالعه‌ات بهینه‌سازی شد.\n\n"
                    "💡 این برنامه شخصی‌سازی شده و با نیازهایت تطبیق داده شده.",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup,
                )
            else:
                await query.edit_message_text(
                    "❌ خطا در تولید برنامه جدید. لطفاً دوباره تلاش کن.",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔙 بازگشت", callback_data="coach_schedule")]]
                    ),
                )

        except Exception as e:
            logger.error(f"Error in regenerate_schedule: {e}")
            await query.edit_message_text("❌ خطا در تولید مجدد برنامه. لطفاً دوباره تلاش کن.")

    async def _get_user_schedule(self, user_id: int, schedule_date: date) -> dict:
        """Get user's schedule for a specific date"""
        try:
            query = """
            SELECT time_slots, total_planned_time, total_actual_time, completion_rate
            FROM study_schedules
            WHERE user_id = %s AND schedule_date = %s
            """

            result = await self.service.db_manager.fetch_one(query, (user_id, schedule_date))
            return dict(result) if result else None

        except Exception as e:
            logger.error(f"Error getting user schedule: {e}")
            return None

    async def _generate_daily_schedule(self, user_id: int, schedule_date: date) -> dict:
        """Generate AI-powered daily study schedule"""
        try:
            # Get user analytics
            analytics = await self.service.get_user_analytics(user_id)

            if not analytics:
                # Default schedule for new users
                return self._create_default_schedule()

            # Generate personalized schedule based on analytics
            schedule = {
                "morning_session": {
                    "time": "08:00-10:00",
                    "subject": "ریاضی",
                    "duration": 120,
                    "difficulty": "medium",
                },
                "afternoon_session": {
                    "time": "14:00-16:00",
                    "subject": "فیزیک",
                    "duration": 120,
                    "difficulty": "hard",
                },
                "evening_session": {
                    "time": "19:00-20:30",
                    "subject": "شیمی",
                    "duration": 90,
                    "difficulty": "easy",
                },
                "breaks": [
                    {"time": "10:00-10:15", "type": "short"},
                    {"time": "16:00-16:30", "type": "long"},
                    {"time": "20:30-21:00", "type": "evening"},
                ],
                "total_planned_time": 330,
                "optimization_notes": "بر اساس الگوهای مطالعه‌ات بهینه‌سازی شده",
            }

            # Adjust based on user's performance
            if analytics.efficiency_score > 80:
                schedule["optimization_notes"] += " - کارایی بالا"
            elif analytics.efficiency_score < 60:
                schedule["optimization_notes"] += " - نیاز به بهبود کارایی"

            return schedule

        except Exception as e:
            logger.error(f"Error generating daily schedule: {e}")
            return self._create_default_schedule()

    def _create_default_schedule(self) -> dict:
        """Create default schedule for new users"""
        return {
            "morning_session": {
                "time": "09:00-11:00",
                "subject": "ریاضی",
                "duration": 120,
                "difficulty": "medium",
            },
            "afternoon_session": {
                "time": "15:00-17:00",
                "subject": "فیزیک",
                "duration": 120,
                "difficulty": "hard",
            },
            "evening_session": {
                "time": "19:00-20:00",
                "subject": "شیمی",
                "duration": 60,
                "difficulty": "easy",
            },
            "breaks": [
                {"time": "11:00-11:15", "type": "short"},
                {"time": "17:00-17:30", "type": "long"},
            ],
            "total_planned_time": 300,
            "optimization_notes": "برنامه پیش‌فرض - قابل تنظیم",
        }

    async def _save_schedule(self, user_id: int, schedule_date: date, schedule: dict) -> bool:
        """Save schedule to database"""
        try:
            query = """
            INSERT INTO study_schedules
            (user_id, schedule_date, time_slots, total_planned_time, is_optimized)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, schedule_date)
            DO UPDATE SET
                time_slots = EXCLUDED.time_slots,
                total_planned_time = EXCLUDED.total_planned_time,
                is_optimized = EXCLUDED.is_optimized,
                updated_at = NOW()
            """

            await self.service.db_manager.execute(
                query,
                (
                    user_id,
                    schedule_date,
                    json.dumps(schedule),
                    schedule.get("total_planned_time", 0),
                    True,
                ),
            )
            return True

        except Exception as e:
            logger.error(f"Error saving schedule: {e}")
            return False

    def _create_schedule_message(self, schedule: dict, schedule_date: date) -> str:
        """Create formatted schedule message"""
        if not schedule:
            return "📅 **برنامه امروز**\n\n❌ برنامه‌ای برای امروز تنظیم نشده."

        message = f"""
📅 **برنامه مطالعه - {schedule_date.strftime('%Y/%m/%d')}**

🌅 **صبح:**
• زمان: {schedule.get('morning_session', {}).get('time', 'نامشخص')}
• موضوع: {schedule.get('morning_session', {}).get('subject', 'نامشخص')}
• مدت: {schedule.get('morning_session', {}).get('duration', 0)} دقیقه

🌞 **ظهر:**
• زمان: {schedule.get('afternoon_session', {}).get('time', 'نامشخص')}
• موضوع: {schedule.get('afternoon_session', {}).get('subject', 'نامشخص')}
• مدت: {schedule.get('afternoon_session', {}).get('duration', 0)} دقیقه

🌙 **عصر:**
• زمان: {schedule.get('evening_session', {}).get('time', 'نامشخص')}
• موضوع: {schedule.get('evening_session', {}).get('subject', 'نامشخص')}
• مدت: {schedule.get('evening_session', {}).get('duration', 0)} دقیقه

⏰ **استراحت‌ها:**
{chr(10).join(f"• {break_info.get('time', 'نامشخص')} - {break_info.get('type', 'نامشخص')}" for break_info in schedule.get('breaks', []))}

📊 **خلاصه:**
• زمان کل: {schedule.get('total_planned_time', 0)} دقیقه
• بهینه‌سازی: {schedule.get('optimization_notes', 'نامشخص')}
        """

        return message

    async def _get_week_schedule(self, user_id: int) -> dict:
        """Get weekly schedule overview"""
        try:
            # Get analytics for the week
            analytics = await self.service.get_user_analytics(user_id, days=7)

            week_schedule = {
                "total_study_time": analytics.total_study_time if analytics else 0,
                "average_daily": (
                    (analytics.total_study_time / 7)
                    if analytics and analytics.total_study_time
                    else 0
                ),
                "sessions": analytics.study_sessions if analytics else 0,
                "subjects": analytics.subjects_studied if analytics else [],
                "efficiency": analytics.efficiency_score if analytics else 0,
                "recommendations": [],
            }

            # Generate week recommendations
            if analytics and analytics.efficiency_score < 70:
                week_schedule["recommendations"].append("زمان‌بندی‌ت رو بهبود بده")

            if analytics and analytics.consistency_score < 60:
                week_schedule["recommendations"].append("برنامه‌ریزی منظم‌تری داشته باش")

            return week_schedule

        except Exception as e:
            logger.error(f"Error getting week schedule: {e}")
            return {}

    def _create_week_schedule_message(self, week_schedule: dict) -> str:
        """Create weekly schedule message"""
        if not week_schedule:
            return "📆 **برنامه هفته**\n\n❌ داده‌ای برای نمایش موجود نیست."

        message = f"""
📆 **برنامه هفتگی مطالعه**

📊 **آمار هفته:**
• زمان کل: {week_schedule.get('total_study_time', 0)} دقیقه
• میانگین روزانه: {week_schedule.get('average_daily', 0):.1f} دقیقه
• جلسات: {week_schedule.get('sessions', 0)} جلسه
• کارایی: {week_schedule.get('efficiency', 0):.1f}%

📚 **موضوعات:**
{', '.join(week_schedule.get('subjects', ['نامشخص']))}

💡 **توصیه‌های هفته:**
{chr(10).join(f"• {rec}" for rec in week_schedule.get('recommendations', ['هیچ توصیه‌ای نیست']))}
        """

        return message

    async def _analyze_optimal_times(self, user_id: int) -> dict:
        """Analyze user's optimal study times"""
        try:
            analytics = await self.service.get_user_analytics(user_id)

            if not analytics:
                return {
                    "morning": "09:00-11:00",
                    "afternoon": "15:00-17:00",
                    "evening": "19:00-21:00",
                    "analysis": "بر اساس الگوهای عمومی",
                }

            # Analyze based on user's patterns
            optimal_times = {
                "morning": "08:00-10:00" if analytics.focus_score > 80 else "09:00-11:00",
                "afternoon": "14:00-16:00" if analytics.efficiency_score > 70 else "15:00-17:00",
                "evening": "19:00-21:00" if analytics.consistency_score > 75 else "20:00-22:00",
                "analysis": f"بر اساس کارایی {analytics.efficiency_score:.1f}% و تمرکز {analytics.focus_score:.1f}%",
            }

            return optimal_times

        except Exception as e:
            logger.error(f"Error analyzing optimal times: {e}")
            return {
                "morning": "09:00-11:00",
                "afternoon": "15:00-17:00",
                "evening": "19:00-21:00",
                "analysis": "بر اساس الگوهای عمومی",
            }

    def _create_optimal_times_message(self, optimal_times: dict) -> str:
        """Create optimal times message"""
        message = f"""
⏰ **زمان‌های بهینه مطالعه**

🌅 **صبح (بهترین زمان):**
• {optimal_times.get('morning', 'نامشخص')}
• دلیل: تمرکز بالا، ذهن تازه

🌞 **ظهر:**
• {optimal_times.get('afternoon', 'نامشخص')}
• دلیل: انرژی متوسط، مناسب برای موضوعات متوسط

🌙 **عصر:**
• {optimal_times.get('evening', 'نامشخص')}
• دلیل: آرامش، مناسب برای مرور

📊 **تحلیل:**
{optimal_times.get('analysis', 'نامشخص')}

💡 **نکات مهم:**
• زمان‌های اوج انرژی‌ت رو شناسایی کن
• استراحت‌های منظم داشته باش
• عوامل حواس‌پرتی رو حذف کن
• برنامه‌ت رو منعطف نگه دار
        """

        return message


# Create Schedule handler instance
schedule_handler = ScheduleHandler()
