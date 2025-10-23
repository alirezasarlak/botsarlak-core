"""
🌌 SarlakBot v3.1.0 - Report Handler
Complete study report and tracking system handler
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.config import config
from src.services.report_service import report_service, StudyStatistics
from src.services.auto_tracking_service import auto_tracking_service
from src.database.connection import db_manager
from src.core.menu_manager import menu_manager
from src.core.security_audit import security_auditor, ActionType, SecurityLevel, AuditLog
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ReportHandler:
    """
    🌌 Report Handler
    Complete study report and tracking system
    """
    
    def __init__(self):
        self.logger = logger
    
    async def register(self, application) -> None:
        """Register report handlers"""
        try:
            from telegram.ext import CommandHandler, CallbackQueryHandler
            
            # Register commands
            application.add_handler(CommandHandler("report", self.report_command))
            application.add_handler(CommandHandler("study", self.study_command))
            application.add_handler(CommandHandler("stats", self.stats_command))
            
            # Register callbacks
            application.add_handler(CallbackQueryHandler(self.report_callback, pattern="^report_"))
            application.add_handler(CallbackQueryHandler(self.menu_reports_callback, pattern="^menu_reports"))
            
            self.logger.info("✅ Report Handler registered")
            
        except Exception as e:
            self.logger.error(f"Failed to register Report Handler: {e}")
            raise
    
    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /report command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Log report access
            await security_auditor.log_audit_event(
                AuditLog(
                    user_id=user_id,
                    action=ActionType.ROUTE_ACCESS,
                    resource="report_command",
                    details={"command": "report"},
                    security_level=SecurityLevel.INFO
                )
            )
            
            # Show main report menu
            await self._show_main_report_menu(update, context)
            
        except Exception as e:
            self.logger.error(f"Report command failed: {e}")
            await update.message.reply_text("❌ خطا در نمایش گزارش کار. لطفاً دوباره تلاش کنید.")
    
    async def study_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /study command - quick study logging"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Show quick study logging menu
            await self._show_quick_study_menu(update, context)
            
        except Exception as e:
            self.logger.error(f"Study command failed: {e}")
            await update.message.reply_text("❌ خطا در ثبت مطالعه. لطفاً دوباره تلاش کنید.")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /stats command - show statistics"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Show statistics
            await self._show_statistics(update, context)
            
        except Exception as e:
            self.logger.error(f"Stats command failed: {e}")
            await update.message.reply_text("❌ خطا در نمایش آمار. لطفاً دوباره تلاش کنید.")
    
    async def menu_reports_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle menu_reports callback"""
        try:
            query = update.callback_query
            await query.answer()
            
            await self._show_main_report_menu(update, context)
            
        except Exception as e:
            self.logger.error(f"Menu reports callback failed: {e}")
            await query.edit_message_text("❌ خطا در نمایش منوی گزارش کار.")
    
    async def report_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle report callbacks"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            callback_data = query.data
            
            # Log report interaction
            await security_auditor.log_audit_event(
                AuditLog(
                    user_id=user_id,
                    action=ActionType.ROUTE_ACCESS,
                    resource="report_callback",
                    details={"callback": callback_data},
                    security_level=SecurityLevel.INFO
                )
            )
            
            # Handle different report actions
            if callback_data == "report_today":
                await self._show_today_report(update, context)
            elif callback_data == "report_weekly":
                await self._show_weekly_report(update, context)
            elif callback_data == "report_monthly":
                await self._show_monthly_report(update, context)
            elif callback_data == "report_statistics":
                await self._show_statistics(update, context)
            elif callback_data == "report_subjects":
                await self._show_subject_statistics(update, context)
            elif callback_data == "report_goals":
                await self._show_goals_menu(update, context)
            elif callback_data == "report_log_study":
                await self._show_study_logging_menu(update, context)
            elif callback_data == "report_auto_tracking":
                await self._show_auto_tracking_menu(update, context)
            elif callback_data == "report_start_auto_tracking":
                await self._start_auto_tracking(update, context)
            elif callback_data == "report_stop_auto_tracking":
                await self._stop_auto_tracking(update, context)
            elif callback_data == "report_auto_insights":
                await self._show_auto_insights(update, context)
            elif callback_data == "report_smart_recommendations":
                await self._show_smart_recommendations(update, context)
            elif callback_data.startswith("report_goal_"):
                goal_id = int(callback_data.split("_")[2])
                await self._show_goal_details(update, context, goal_id)
            elif callback_data == "report_new_goal":
                await self._create_new_goal(update, context)
            elif callback_data == "report_goal_progress":
                await self._show_goals_progress(update, context)
            elif callback_data.startswith("report_log_"):
                duration = int(callback_data.split("_")[2])
                await self._log_study_session(update, context, duration)
            elif callback_data == "report_back":
                await self._show_main_report_menu(update, context)
            elif callback_data == "report_home":
                await self._go_home(update, context)
            
        except Exception as e:
            self.logger.error(f"Report callback failed: {e}")
            await query.edit_message_text("❌ خطا در پردازش درخواست گزارش کار.")
    
    async def _show_main_report_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show main report menu"""
        try:
            text = """
🌕 **گزارش کار و پیگیری مطالعه**

📊 **گزینه‌های موجود:**
• 📅 گزارش امروز
• 📈 گزارش هفتگی  
• 📊 گزارش ماهانه
• 📋 آمار کامل
• 📚 آمار موضوعات
• 🎯 اهداف مطالعه
• ➕ ثبت جلسه مطالعه
• 🤖 ردیابی خودکار
• 💡 توصیه‌های هوشمند

🎯 **هدف:** پیگیری دقیق پیشرفت تحصیلی و بهبود عملکرد
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("📅 گزارش امروز", callback_data="report_today"),
                    InlineKeyboardButton("📈 گزارش هفتگی", callback_data="report_weekly")
                ],
                [
                    InlineKeyboardButton("📊 گزارش ماهانه", callback_data="report_monthly"),
                    InlineKeyboardButton("📋 آمار کامل", callback_data="report_statistics")
                ],
                [
                    InlineKeyboardButton("📚 آمار موضوعات", callback_data="report_subjects"),
                    InlineKeyboardButton("🎯 اهداف مطالعه", callback_data="report_goals")
                ],
                [
                    InlineKeyboardButton("➕ ثبت جلسه مطالعه", callback_data="report_log_study"),
                    InlineKeyboardButton("🤖 ردیابی خودکار", callback_data="report_auto_tracking")
                ],
                [
                    InlineKeyboardButton("💡 توصیه‌های هوشمند", callback_data="report_smart_recommendations")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text, reply_markup=reply_markup, parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    text, reply_markup=reply_markup, parse_mode='Markdown'
                )
                
        except Exception as e:
            self.logger.error(f"Error showing main report menu: {e}")
            raise
    
    async def _show_today_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show today's study report"""
        try:
            user_id = update.effective_user.id
            
            # Get today's report
            today_report = await report_service.get_today_report(user_id)
            
            if not today_report:
                text = """
📅 **گزارش امروز**

❌ **هیچ فعالیتی ثبت نشده است**

💡 **نکته:** برای شروع مطالعه از دکمه "ثبت جلسه مطالعه" استفاده کنید.
                """
            else:
                # Calculate accuracy
                accuracy = 0
                if today_report.total_questions > 0:
                    accuracy = round((today_report.correct_answers / today_report.total_questions) * 100, 1)
                
                # Format subjects
                subjects_text = ", ".join(today_report.subjects_studied) if today_report.subjects_studied else "ثبت نشده"
                
                text = f"""
📅 **گزارش امروز - {date.today().strftime('%Y/%m/%d')}**

⏱️ **زمان مطالعه:** {today_report.study_minutes} دقیقه
🧪 **تعداد تست:** {today_report.tests_count}
📝 **سوالات پاسخ داده:** {today_report.total_questions}
✅ **پاسخ‌های صحیح:** {today_report.correct_answers}
📊 **دقت:** {accuracy}%
📚 **موضوعات:** {subjects_text}
🔄 **جلسات مطالعه:** {today_report.study_sessions}

🎯 **هدف روزانه:** 120 دقیقه
📈 **پیشرفت:** {round((today_report.study_minutes / 120) * 100, 1)}%
                """
            
            keyboard = [
                [
                    InlineKeyboardButton("➕ ثبت جلسه مطالعه", callback_data="report_log_study"),
                    InlineKeyboardButton("📈 گزارش هفتگی", callback_data="report_weekly")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing today's report: {e}")
            raise
    
    async def _show_weekly_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show weekly study report"""
        try:
            user_id = update.effective_user.id
            
            # Get weekly summary
            weekly_summary = await report_service.get_weekly_summary(user_id)
            
            text = f"""
📈 **گزارش هفتگی**

⏱️ **کل زمان مطالعه:** {weekly_summary['total_minutes']} دقیقه
🧪 **تعداد تست:** {weekly_summary['total_tests']}
📅 **روزهای مطالعه:** {weekly_summary['study_days']}/7 روز
📊 **میانگین روزانه:** {weekly_summary['average_daily']} دقیقه

📋 **جزئیات روزانه:**
            """
            
            # Add daily breakdown
            for day_data in weekly_summary['daily_data'][:7]:  # Last 7 days
                day_name = day_data['report_date'].strftime('%a')
                minutes = day_data['study_minutes']
                tests = day_data['tests_count']
                text += f"\n• {day_name}: {minutes} دقیقه ({tests} تست)"
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 گزارش ماهانه", callback_data="report_monthly"),
                    InlineKeyboardButton("📋 آمار کامل", callback_data="report_statistics")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing weekly report: {e}")
            raise
    
    async def _show_monthly_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show monthly study report"""
        try:
            user_id = update.effective_user.id
            
            # Get monthly summary
            monthly_summary = await report_service.get_monthly_summary(user_id)
            
            text = f"""
📊 **گزارش ماهانه**

⏱️ **کل زمان مطالعه:** {monthly_summary['total_minutes']} دقیقه
🧪 **تعداد تست:** {monthly_summary['total_tests']}
📅 **روزهای مطالعه:** {monthly_summary['study_days']}/30 روز
📊 **دقت کلی:** {monthly_summary['accuracy_rate']}%

🏆 **برترین موضوعات:**
            """
            
            # Add top subjects
            for i, subject in enumerate(monthly_summary['top_subjects'][:3], 1):
                text += f"\n{i}. {subject['subject']}: {subject['study_minutes']} دقیقه ({subject['accuracy_rate']}%)"
            
            keyboard = [
                [
                    InlineKeyboardButton("📚 آمار موضوعات", callback_data="report_subjects"),
                    InlineKeyboardButton("🎯 اهداف مطالعه", callback_data="report_goals")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing monthly report: {e}")
            raise
    
    async def _show_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show comprehensive statistics"""
        try:
            user_id = update.effective_user.id
            
            # Get statistics
            stats = await report_service.get_study_statistics(user_id, 30)
            
            if not stats:
                text = """
📋 **آمار کامل**

❌ **هیچ داده‌ای یافت نشد**

💡 **نکته:** برای مشاهده آمار، ابتدا جلسات مطالعه خود را ثبت کنید.
                """
            else:
                text = f"""
📋 **آمار کامل (30 روز گذشته)**

⏱️ **کل زمان مطالعه:** {stats.total_study_minutes} دقیقه
🧪 **تعداد تست:** {stats.total_tests}
📝 **سوالات پاسخ داده:** {stats.total_questions}
✅ **پاسخ‌های صحیح:** {stats.correct_answers}
📊 **دقت کلی:** {stats.accuracy_rate}%
📅 **روزهای مطالعه:** {stats.study_days}/30 روز
🔥 **Streak فعلی:** {stats.current_streak} روز
📈 **میانگین جلسه:** {stats.average_session_minutes} دقیقه

🎯 **نمره کلی:** {self._calculate_overall_score(stats)}/100
                """
            
            keyboard = [
                [
                    InlineKeyboardButton("📚 آمار موضوعات", callback_data="report_subjects"),
                    InlineKeyboardButton("🎯 اهداف مطالعه", callback_data="report_goals")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing statistics: {e}")
            raise
    
    async def _show_subject_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show subject-wise statistics"""
        try:
            user_id = update.effective_user.id
            
            # Get subject statistics
            subject_stats = await report_service.get_subject_statistics(user_id, 30)
            
            if not subject_stats:
                text = """
📚 **آمار موضوعات**

❌ **هیچ داده‌ای یافت نشد**

💡 **نکته:** برای مشاهده آمار موضوعات، ابتدا جلسات مطالعه خود را ثبت کنید.
                """
            else:
                text = """
📚 **آمار موضوعات (30 روز گذشته)**

🏆 **موضوعات برتر:**
                """
                
                for i, subject in enumerate(subject_stats[:5], 1):
                    text += f"""
{i}. **{subject['subject']}**
   ⏱️ {subject['study_minutes']} دقیقه
   🧪 {subject['tests_count']} تست
   📊 {subject['accuracy_rate']}% دقت
                    """
            
            keyboard = [
                [
                    InlineKeyboardButton("📋 آمار کامل", callback_data="report_statistics"),
                    InlineKeyboardButton("🎯 اهداف مطالعه", callback_data="report_goals")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing subject statistics: {e}")
            raise
    
    async def _show_goals_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show study goals menu"""
        try:
            user_id = update.effective_user.id
            
            # Get user goals
            goals = await report_service.get_study_goals(user_id)
            
            text = """
🎯 **اهداف مطالعه**

📋 **اهداف فعال:**
            """
            
            if not goals:
                text += "\n❌ **هیچ هدفی تعریف نشده است**"
                text += "\n\n💡 **نکته:** برای تعریف هدف جدید، از دکمه زیر استفاده کنید."
            else:
                for goal in goals[:5]:  # Show first 5 goals
                    progress_percent = round((goal.current_progress / goal.goal_target) * 100, 1)
                    status = "✅" if goal.is_completed else "🔄"
                    text += f"""
{status} **{goal.goal_type.title()} - {goal.goal_target} {goal.goal_unit}**
   📈 پیشرفت: {goal.current_progress}/{goal.goal_target} ({progress_percent}%)
                    """
            
            keyboard = [
                [
                    InlineKeyboardButton("➕ هدف جدید", callback_data="report_new_goal"),
                    InlineKeyboardButton("📊 پیشرفت", callback_data="report_goal_progress")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing goals menu: {e}")
            raise

    async def _create_new_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Create a new simple daily study-time goal (quick action)"""
        try:
            user_id = update.effective_user.id
            # Create a default goal: 120 minutes per day if none exists
            created = await report_service.ensure_default_daily_goal(user_id, target_minutes=120)
            if created:
                text = """
✅ **هدف جدید ایجاد شد**

🎯 هدف روزانه: 120 دقیقه مطالعه
📌 می‌تونی هر زمان از بخش اهداف تغییرش بدی.
                """
            else:
                text = """
ℹ️ **هدف قبلاً تعریف شده است**

برای تغییر یا حذف، از منوی اهداف استفاده کن.
                """

            keyboard = [
                [InlineKeyboardButton("📊 پیشرفت", callback_data="report_goal_progress"),
                 InlineKeyboardButton("🎯 اهداف", callback_data="report_goals")],
                [InlineKeyboardButton("🏠 خانه", callback_data="report_home")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as e:
            self.logger.error(f"Error creating new goal: {e}")
            raise

    async def _show_goals_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show progress for current goals"""
        try:
            user_id = update.effective_user.id
            progress = await report_service.get_goals_progress(user_id)
            if not progress:
                text = """
📊 **پیشرفت اهداف**

❌ هیچ هدف فعالی یافت نشد.
برای شروع، یک هدف جدید بساز.
                """
            else:
                text = """
📊 **پیشرفت اهداف**
                """
                for item in progress[:5]:
                    text += f"\n• {item['title']}: {item['current']}/{item['target']} ({item['percent']}%)"

            keyboard = [
                [InlineKeyboardButton("🎯 اهداف", callback_data="report_goals"),
                 InlineKeyboardButton("🏠 خانه", callback_data="report_home")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as e:
            self.logger.error(f"Error showing goals progress: {e}")
            raise
    
    async def _show_study_logging_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show study logging menu"""
        try:
            text = """
➕ **ثبت جلسه مطالعه**

⏱️ **مدت زمان مطالعه:**
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("15 دقیقه", callback_data="report_log_15"),
                    InlineKeyboardButton("30 دقیقه", callback_data="report_log_30"),
                    InlineKeyboardButton("45 دقیقه", callback_data="report_log_45")
                ],
                [
                    InlineKeyboardButton("60 دقیقه", callback_data="report_log_60"),
                    InlineKeyboardButton("90 دقیقه", callback_data="report_log_90"),
                    InlineKeyboardButton("120 دقیقه", callback_data="report_log_120")
                ],
                [
                    InlineKeyboardButton("180 دقیقه", callback_data="report_log_180"),
                    InlineKeyboardButton("240 دقیقه", callback_data="report_log_240")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing study logging menu: {e}")
            raise
    
    async def _log_study_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE, duration: int) -> None:
        """Log a study session"""
        try:
            user_id = update.effective_user.id
            
            # Log the study session
            success = await report_service.log_study_session(
                user_id=user_id,
                duration_minutes=duration,
                subject="عمومی",  # Default subject
                session_type="study"
            )
            
            if success:
                text = f"""
✅ **جلسه مطالعه ثبت شد**

⏱️ **مدت زمان:** {duration} دقیقه
📅 **تاریخ:** {date.today().strftime('%Y/%m/%d')}
🕐 **زمان:** {datetime.now().strftime('%H:%M')}

🎉 **تبریک!** جلسه مطالعه شما با موفقیت ثبت شد.

💡 **نکته:** برای مشاهده گزارش کامل، از منوی گزارش کار استفاده کنید.
                """
            else:
                text = """
❌ **خطا در ثبت جلسه مطالعه**

لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.
                """
            
            keyboard = [
                [
                    InlineKeyboardButton("📅 گزارش امروز", callback_data="report_today"),
                    InlineKeyboardButton("📈 گزارش هفتگی", callback_data="report_weekly")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error logging study session: {e}")
            raise
    
    async def _show_quick_study_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show quick study menu for /study command"""
        try:
            text = """
⚡ **ثبت سریع مطالعه**

⏱️ **مدت زمان مطالعه:**
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("30 دقیقه", callback_data="report_log_30"),
                    InlineKeyboardButton("60 دقیقه", callback_data="report_log_60")
                ],
                [
                    InlineKeyboardButton("90 دقیقه", callback_data="report_log_90"),
                    InlineKeyboardButton("120 دقیقه", callback_data="report_log_120")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing quick study menu: {e}")
            raise
    
    async def _go_home(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Go to main menu"""
        try:
            from src.utils.navigation import NavigationKeyboard
            
            text = """
🌌 **منوی اصلی**

خوش برگشتی به کیهان یادگیری! 🚀
            """
            
            keyboard = NavigationKeyboard.create_main_menu_keyboard()
            await update.callback_query.edit_message_text(
                text, reply_markup=keyboard, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error going home: {e}")
            raise
    
    async def _show_auto_tracking_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show auto tracking menu"""
        try:
            user_id = update.effective_user.id
            
            # Check if auto tracking is active
            async with db_manager.get_connection() as conn:
                tracking_status = await conn.fetchrow(
                    """
                    SELECT is_active, start_time 
                    FROM auto_tracking_sessions 
                    WHERE user_id = $1 AND is_active = TRUE
                    """,
                    user_id
                )
            
            if tracking_status:
                status_text = f"🟢 فعال از {tracking_status['start_time'].strftime('%H:%M')}"
                button_text = "⏹️ توقف ردیابی خودکار"
                callback_data = "report_stop_auto_tracking"
            else:
                status_text = "🔴 غیرفعال"
                button_text = "▶️ شروع ردیابی خودکار"
                callback_data = "report_start_auto_tracking"
            
            text = f"""
🤖 **ردیابی خودکار مطالعه**

📊 **وضعیت فعلی:** {status_text}

🎯 **قابلیت‌ها:**
• 🔍 تشخیص خودکار جلسات مطالعه
• 📈 تحلیل الگوهای مطالعه
• 💡 توصیه‌های شخصی‌سازی شده
• 🎯 تنظیم خودکار اهداف
• 📊 گزارش‌های هوشمند

💡 **نکته:** ردیابی خودکار به شما کمک می‌کند تا بدون نیاز به ثبت دستی، پیشرفت خود را پیگیری کنید.
            """
            
            keyboard = [
                [
                    InlineKeyboardButton(button_text, callback_data=callback_data),
                    InlineKeyboardButton("📊 بینش‌های خودکار", callback_data="report_auto_insights")
                ],
                [
                    InlineKeyboardButton("💡 توصیه‌های هوشمند", callback_data="report_smart_recommendations"),
                    InlineKeyboardButton("📈 الگوهای مطالعه", callback_data="report_study_patterns")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing auto tracking menu: {e}")
            raise
    
    async def _start_auto_tracking(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start auto tracking"""
        try:
            user_id = update.effective_user.id
            
            # Start auto tracking
            success = await auto_tracking_service.start_auto_tracking(user_id)
            
            if success:
                text = """
✅ **ردیابی خودکار شروع شد!**

🤖 **سیستم ردیابی فعال:**
• 🔍 تشخیص خودکار جلسات مطالعه
• 📊 ثبت آمار و پیشرفت
• 💡 تحلیل الگوهای مطالعه
• 🎯 تنظیم خودکار اهداف

💡 **نکته:** حالا می‌توانید به مطالعه بپردازید و سیستم به طور خودکار فعالیت‌های شما را ردیابی می‌کند.
                """
            else:
                text = """
❌ **خطا در شروع ردیابی خودکار**

🚫 **دلایل احتمالی:**
• ردیابی قبلاً فعال است
• خطا در سیستم

💡 **نکته:** لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.
                """
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 وضعیت ردیابی", callback_data="report_auto_tracking"),
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back")
                ],
                [
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error starting auto tracking: {e}")
            raise
    
    async def _stop_auto_tracking(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Stop auto tracking"""
        try:
            user_id = update.effective_user.id
            
            # Stop auto tracking
            success = await auto_tracking_service.stop_auto_tracking(user_id)
            
            if success:
                text = """
⏹️ **ردیابی خودکار متوقف شد!**

📊 **آمار نهایی:**
• تمام فعالیت‌های ردیابی شده ذخیره شدند
• گزارش‌های تولید شده در دسترس هستند
• می‌توانید دوباره ردیابی را فعال کنید

💡 **نکته:** برای شروع مجدد ردیابی، از دکمه "شروع ردیابی خودکار" استفاده کنید.
                """
            else:
                text = """
❌ **خطا در توقف ردیابی خودکار**

💡 **نکته:** لطفاً دوباره تلاش کنید.
                """
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 وضعیت ردیابی", callback_data="report_auto_tracking"),
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back")
                ],
                [
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error stopping auto tracking: {e}")
            raise
    
    async def _show_auto_insights(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show auto insights"""
        try:
            user_id = update.effective_user.id
            
            # Get auto insights
            async with db_manager.get_connection() as conn:
                insights = await conn.fetch(
                    """
                    SELECT * FROM study_insights 
                    WHERE user_id = $1 
                    ORDER BY created_at DESC 
                    LIMIT 5
                    """,
                    user_id
                )
            
            if not insights:
                text = """
💡 **بینش‌های خودکار**

❌ **هیچ بینشی یافت نشد**

💡 **نکته:** برای دریافت بینش‌های هوشمند، ابتدا ردیابی خودکار را فعال کنید و مدتی مطالعه کنید.
                """
            else:
                text = """
💡 **بینش‌های خودکار**

🧠 **تحلیل‌های هوشمند:**
                """
                
                for i, insight in enumerate(insights[:3], 1):
                    text += f"""
{i}. **{insight['insight_type'].title()}**
   📊 {insight['insight_data'].get('description', 'بدون توضیح')}
   🎯 اعتماد: {int(insight['confidence'] * 100)}%
                    """
            
            keyboard = [
                [
                    InlineKeyboardButton("🤖 ردیابی خودکار", callback_data="report_auto_tracking"),
                    InlineKeyboardButton("💡 توصیه‌های هوشمند", callback_data="report_smart_recommendations")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing auto insights: {e}")
            raise
    
    async def _show_smart_recommendations(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show smart recommendations"""
        try:
            user_id = update.effective_user.id
            
            # Get smart recommendations
            async with db_manager.get_connection() as conn:
                recommendations = await conn.fetch(
                    "SELECT * FROM generate_smart_recommendations($1)",
                    user_id
                )
            
            if not recommendations or not recommendations[0][0]:
                text = """
💡 **توصیه‌های هوشمند**

❌ **هیچ توصیه‌ای یافت نشد**

💡 **نکته:** برای دریافت توصیه‌های شخصی‌سازی شده، ابتدا مدتی مطالعه کنید.
                """
            else:
                text = """
💡 **توصیه‌های هوشمند**

🎯 **توصیه‌های شخصی‌سازی شده:**
                """
                
                for i, rec in enumerate(recommendations[0][0][:5], 1):
                    text += f"""
{i}. {rec}
                    """
            
            keyboard = [
                [
                    InlineKeyboardButton("🤖 ردیابی خودکار", callback_data="report_auto_tracking"),
                    InlineKeyboardButton("📊 بینش‌های خودکار", callback_data="report_auto_insights")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="report_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="report_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing smart recommendations: {e}")
            raise
    
    async def show_daily_report(self, query) -> None:
        """Show daily report for user"""
        try:
            user_id = query.from_user.id
            
            # Get today's study statistics
            today = date.today()
            stats = await report_service.get_daily_statistics(user_id, today)
            
            if not stats:
                text = """
📊 **گزارش روزانه**

❌ **هیچ مطالعه‌ای امروز ثبت نشده**

💡 **نکته:** برای ثبت مطالعه، از دکمه "ثبت جلسه مطالعه" استفاده کنید.
                """
            else:
                text = f"""
📊 **گزارش روزانه - {today.strftime('%Y/%m/%d')}**

⏰ **زمان مطالعه:** {stats.total_minutes} دقیقه
📚 **تعداد جلسات:** {stats.session_count}
🎯 **موضوعات:** {', '.join(stats.subjects) if stats.subjects else 'نامشخص'}

📈 **پیشرفت امروز:**
• زمان مطالعه: {stats.total_minutes} دقیقه
• جلسات تکمیل شده: {stats.session_count}
• امتیاز کسب شده: {stats.points_earned}
                """
            
            keyboard = [
                [
                    InlineKeyboardButton("📝 ثبت جلسه مطالعه", callback_data="report_log_study"),
                    InlineKeyboardButton("📊 آمار کامل", callback_data="report_statistics")
                ],
                [
                    InlineKeyboardButton("📅 گزارش هفتگی", callback_data="report_weekly"),
                    InlineKeyboardButton("📈 نمودار پیشرفت", callback_data="report_progress")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="go_home"),
                    InlineKeyboardButton("🏠 خانه", callback_data="menu_main")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing daily report: {e}")
            await query.edit_message_text("❌ خطا در نمایش گزارش روزانه")
    
    def _calculate_overall_score(self, stats: StudyStatistics) -> int:
        """Calculate overall study score"""
        try:
            # Base score from study time (max 40 points)
            time_score = min(stats.total_study_minutes / 10, 40)
            
            # Accuracy score (max 30 points)
            accuracy_score = (stats.accuracy_rate / 100) * 30
            
            # Consistency score (max 20 points)
            consistency_score = (stats.study_days / 30) * 20
            
            # Streak bonus (max 10 points)
            streak_score = min(stats.current_streak, 10)
            
            total_score = time_score + accuracy_score + consistency_score + streak_score
            return min(int(total_score), 100)
            
        except Exception as e:
            self.logger.error(f"Error calculating overall score: {e}")
            return 0
