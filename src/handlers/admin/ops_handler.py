"""
🌌 SarlakBot v3.2.0 - Operations Handler
Admin operations and system monitoring
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from src.utils.error_handler import safe_async_handler
from src.utils.logging import get_logger
from src.utils.monitoring import system_monitor

logger = get_logger(__name__)


class OpsHandler:
    """
    🌌 Operations Handler
    Admin operations and system monitoring
    """

    def __init__(self):
        self.logger = logger

    async def register(self, application) -> None:
        """Register operations handlers"""
        try:
            self.logger.info("🚀 Registering operations handlers...")

            # Register command handlers
            application.add_handler(CommandHandler("ops", self.ops_command))
            application.add_handler(CommandHandler("status", self.status_command))
            application.add_handler(CommandHandler("health", self.health_command))
            application.add_handler(CommandHandler("metrics", self.metrics_command))

            # Register callback handlers
            application.add_handler(CallbackQueryHandler(self.ops_callback, pattern="^ops_"))

            self.logger.info("✅ Operations handlers registered successfully")

        except Exception as e:
            self.logger.error(f"❌ Failed to register operations handlers: {e}")
            raise

    @safe_async_handler
    async def ops_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /ops command"""
        try:
            user_id = update.effective_user.id

            # Check if user is admin
            if not await self._is_admin(user_id):
                await update.message.reply_text("❌ دسترسی ادمین نداری")
                return

            # Get system status
            status = await system_monitor.get_detailed_status()

            # Create operations menu
            text = f"""
🛠 **پنل عملیات سیستم** / **System Operations Panel**

📊 **وضعیت کلی** / **Overall Status:** {status['summary']['overall_status']}
⏱️ **زمان فعالیت** / **Uptime:** {status['summary']['uptime']}
📈 **تعداد درخواست‌ها** / **Request Count:** {status['summary']['request_count']}
❌ **نرخ خطا** / **Error Rate:** {status['summary']['error_rate']:.2f}%

**Available Operations:**
• 🔍 System Health Check
• 📊 Performance Metrics
• 🗄️ Database Status
• 📈 Request Statistics
• 🔄 System Restart
"""

            keyboard = [
                [
                    InlineKeyboardButton("🔍 Health Check", callback_data="ops_health"),
                    InlineKeyboardButton("📊 Metrics", callback_data="ops_metrics"),
                ],
                [
                    InlineKeyboardButton("🗄️ Database", callback_data="ops_database"),
                    InlineKeyboardButton("📈 Statistics", callback_data="ops_stats"),
                ],
                [
                    InlineKeyboardButton("🔄 Restart", callback_data="ops_restart"),
                    InlineKeyboardButton("📋 Logs", callback_data="ops_logs"),
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="ops_back")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            self.logger.error(f"❌ Ops command failed: {e}")
            await update.message.reply_text("❌ خطا در نمایش پنل عملیات")

    @safe_async_handler
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command"""
        try:
            user_id = update.effective_user.id

            # Check if user is admin
            if not await self._is_admin(user_id):
                await update.message.reply_text("❌ دسترسی ادمین نداری")
                return

            # Get system status
            status = await system_monitor.get_detailed_status()

            text = f"""
📊 **وضعیت سیستم** / **System Status**

🟢 **وضعیت کلی** / **Overall Status:** {status['summary']['overall_status']}
⏱️ **زمان فعالیت** / **Uptime:** {status['summary']['uptime']}
📈 **تعداد درخواست‌ها** / **Request Count:** {status['summary']['request_count']}
❌ **نرخ خطا** / **Error Rate:** {status['summary']['error_rate']:.2f}%

**Database Status:**
• Status: {status['health']['details'].get('database', {}).get('status', 'Unknown')}
• Pool Size: {status['health']['details'].get('database', {}).get('pool_stats', {}).get('size', 'Unknown')}

**System Resources:**
• Status: {status['health']['details'].get('system', {}).get('status', 'Unknown')}
"""

            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            self.logger.error(f"❌ Status command failed: {e}")
            await update.message.reply_text("❌ خطا در دریافت وضعیت سیستم")

    @safe_async_handler
    async def health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /health command"""
        try:
            user_id = update.effective_user.id

            # Check if user is admin
            if not await self._is_admin(user_id):
                await update.message.reply_text("❌ دسترسی ادمین نداری")
                return

            # Get health status
            health = await system_monitor.health_check()

            status_emoji = "🟢" if health.status == "healthy" else "🔴"

            text = f"""
{status_emoji} **Health Check Results**

**Overall Status:** {health.status}
**Timestamp:** {health.timestamp.isoformat()}

**Errors:**
{chr(10).join(f"• {error}" for error in health.errors) if health.errors else "• None"}

**Details:**
• Database: {health.details.get('database', {}).get('status', 'Unknown')}
• System: {health.details.get('system', {}).get('status', 'Unknown')}
• Bot: {health.details.get('bot', {}).get('status', 'Unknown')}
"""

            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            self.logger.error(f"❌ Health command failed: {e}")
            await update.message.reply_text("❌ خطا در بررسی سلامت سیستم")

    @safe_async_handler
    async def metrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /metrics command"""
        try:
            user_id = update.effective_user.id

            # Check if user is admin
            if not await self._is_admin(user_id):
                await update.message.reply_text("❌ دسترسی ادمین نداری")
                return

            # Get metrics
            metrics = system_monitor.get_metrics()

            text = f"""
📊 **Performance Metrics**

**Uptime:** {metrics.get('uptime_human', 'Unknown')}
**Request Count:** {metrics.get('request_count', 0)}
**Error Count:** {metrics.get('error_count', 0)}
**Error Rate:** {metrics.get('error_rate_percent', 0):.2f}%

**Timestamps:**
• Start Time: {metrics.get('start_time', 'Unknown')}
• Last Health Check: {metrics.get('last_health_check', 'Unknown')}
"""

            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            self.logger.error(f"❌ Metrics command failed: {e}")
            await update.message.reply_text("❌ خطا در دریافت معیارهای عملکرد")

    @safe_async_handler
    async def ops_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle operations callbacks"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = query.effective_user.id

            # Check if user is admin
            if not await self._is_admin(user_id):
                await query.edit_message_text("❌ دسترسی ادمین نداری")
                return

            action = query.data.split("_")[1]

            if action == "health":
                await self._show_health_details(query)
            elif action == "metrics":
                await self._show_metrics_details(query)
            elif action == "database":
                await self._show_database_details(query)
            elif action == "stats":
                await self._show_statistics_details(query)
            elif action == "restart":
                await self._show_restart_confirmation(query)
            elif action == "logs":
                await self._show_logs_details(query)
            elif action == "back":
                await self._show_ops_menu(query)

        except Exception as e:
            self.logger.error(f"❌ Ops callback failed: {e}")
            await query.answer("❌ خطا در پردازش درخواست")

    async def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        # This is a placeholder - implement proper admin check
        # In production, you'd check against a database or config
        return user_id in [123456789]  # Replace with actual admin IDs

    async def _show_health_details(self, query) -> None:
        """Show detailed health information"""
        try:
            health = await system_monitor.health_check()

            text = f"""
🔍 **Detailed Health Check**

**Status:** {health.status}
**Timestamp:** {health.timestamp.isoformat()}

**Database:**
• Status: {health.details.get('database', {}).get('status', 'Unknown')}
• Pool Size: {health.details.get('database', {}).get('pool_stats', {}).get('size', 'Unknown')}

**System:**
• Status: {health.details.get('system', {}).get('status', 'Unknown')}

**Bot:**
• Status: {health.details.get('bot', {}).get('status', 'Unknown')}
• Uptime: {health.details.get('bot', {}).get('uptime', 'Unknown')}

**Errors:**
{chr(10).join(f"• {error}" for error in health.errors) if health.errors else "• None"}
"""

            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="ops_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to show health details: {e}")

    async def _show_metrics_details(self, query) -> None:
        """Show detailed metrics"""
        try:
            metrics = system_monitor.get_metrics()

            text = f"""
📊 **Detailed Performance Metrics**

**Uptime:**
• Seconds: {metrics.get('uptime_seconds', 0):.2f}
• Human: {metrics.get('uptime_human', 'Unknown')}

**Requests:**
• Total: {metrics.get('request_count', 0)}
• Errors: {metrics.get('error_count', 0)}
• Error Rate: {metrics.get('error_rate_percent', 0):.2f}%

**Timestamps:**
• Start: {metrics.get('start_time', 'Unknown')}
• Last Check: {metrics.get('last_health_check', 'Unknown')}
"""

            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="ops_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to show metrics details: {e}")

    async def _show_database_details(self, query) -> None:
        """Show database details"""
        try:
            from src.database.connection import db_manager

            db_health = await db_manager.health_check()

            text = f"""
🗄️ **Database Status**

**Status:** {db_health.get('status', 'Unknown')}
**Database:** {db_health.get('database_info', {}).get('database_name', 'Unknown')}
**Version:** {db_health.get('database_info', {}).get('version', 'Unknown')}
**User:** {db_health.get('database_info', {}).get('current_user', 'Unknown')}

**Pool Stats:**
• Size: {db_health.get('pool_stats', {}).get('size', 'Unknown')}
• Idle: {db_health.get('pool_stats', {}).get('idle_size', 'Unknown')}
• Max: {db_health.get('pool_stats', {}).get('max_size', 'Unknown')}
"""

            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="ops_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to show database details: {e}")

    async def _show_statistics_details(self, query) -> None:
        """Show statistics details"""
        try:
            history = system_monitor.get_health_history(10)

            text = "📈 **System Statistics**\n\n"

            for i, health in enumerate(history[-5:], 1):  # Show last 5 checks
                status_emoji = "🟢" if health["status"] == "healthy" else "🔴"
                text += f"{i}. {status_emoji} {health['timestamp']}\n"

            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="ops_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to show statistics details: {e}")

    async def _show_restart_confirmation(self, query) -> None:
        """Show restart confirmation"""
        try:
            text = """
🔄 **System Restart Confirmation**

⚠️ **Warning:** This will restart the bot system.

Are you sure you want to restart?

**توجه:** این کار سیستم ربات را راه‌اندازی مجدد می‌کند.

آیا مطمئن هستید؟
"""

            keyboard = [
                [
                    InlineKeyboardButton("✅ Yes, Restart", callback_data="ops_restart_confirm"),
                    InlineKeyboardButton("❌ Cancel", callback_data="ops_back"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to show restart confirmation: {e}")

    async def _show_logs_details(self, query) -> None:
        """Show logs details"""
        try:
            text = """
📋 **System Logs**

Log viewing functionality will be implemented in future versions.

**قابلیت مشاهده لاگ‌ها در نسخه‌های آینده پیاده‌سازی خواهد شد.**
"""

            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="ops_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to show logs details: {e}")

    async def _show_ops_menu(self, query) -> None:
        """Show operations menu"""
        try:
            status = await system_monitor.get_detailed_status()

            text = f"""
🛠 **پنل عملیات سیستم** / **System Operations Panel**

📊 **وضعیت کلی** / **Overall Status:** {status['summary']['overall_status']}
⏱️ **زمان فعالیت** / **Uptime:** {status['summary']['uptime']}
📈 **تعداد درخواست‌ها** / **Request Count:** {status['summary']['request_count']}
❌ **نرخ خطا** / **Error Rate:** {status['summary']['error_rate']:.2f}%

**Available Operations:**
• 🔍 System Health Check
• 📊 Performance Metrics
• 🗄️ Database Status
• 📈 Request Statistics
• 🔄 System Restart
"""

            keyboard = [
                [
                    InlineKeyboardButton("🔍 Health Check", callback_data="ops_health"),
                    InlineKeyboardButton("📊 Metrics", callback_data="ops_metrics"),
                ],
                [
                    InlineKeyboardButton("🗄️ Database", callback_data="ops_database"),
                    InlineKeyboardButton("📈 Statistics", callback_data="ops_stats"),
                ],
                [
                    InlineKeyboardButton("🔄 Restart", callback_data="ops_restart"),
                    InlineKeyboardButton("📋 Logs", callback_data="ops_logs"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to show ops menu: {e}")


# Global operations handler instance
ops_handler = OpsHandler()
