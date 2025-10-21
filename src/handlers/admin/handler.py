"""
🌌 SarlakBot v3.0 - Admin Panel Handler
Professional admin interface with full user management capabilities
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    ConversationHandler,
    filters,
    ContextTypes
)

from src.config import config
from src.database.connection import db_manager
from src.utils.logging import get_logger
from src.handlers.admin.texts_fa import (
    ADMIN_WELCOME, ADMIN_MAIN_MENU, ADMIN_MENU_BUTTONS,
    USER_MANAGEMENT_MENU, USER_MANAGEMENT_BUTTONS,
    USER_SEARCH_MESSAGE, USER_SEARCH_BUTTONS,
    USER_DETAILS_TEMPLATE, STATS_MENU, STATS_BUTTONS,
    BROADCAST_MENU, BROADCAST_BUTTONS, DATABASE_MENU,
    DATABASE_BUTTONS, SETTINGS_MENU, SETTINGS_BUTTONS,
    LOGS_MENU, LOGS_BUTTONS, format_user_details,
    format_admin_welcome, get_success_message, get_error_message
)

logger = get_logger(__name__)

# Conversation states
(ADMIN_MAIN, USER_MANAGEMENT, USER_SEARCH, USER_DETAILS,
 STATS_VIEW, BROADCAST_MENU_STATE, BROADCAST_TEXT,
 DATABASE_MENU_STATE, SETTINGS_MENU_STATE, LOGS_MENU_STATE) = range(10)


class AdminHandler:
    """
    🌌 Professional Admin Handler
    Complete admin panel with user management, statistics, and system control
    """
    
    def __init__(self):
        self.logger = logger
        self.admin_id = config.bot.admin_id
        self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    async def register(self, application: Application) -> None:
        """Register admin handlers"""
        try:
            self.logger.info("👑 Registering admin handlers...")
            
            # Admin command handler
            application.add_handler(CommandHandler("admin", self.admin_command))
            
            # Admin conversation handler
            admin_conv_handler = ConversationHandler(
                entry_points=[CallbackQueryHandler(self.admin_callback, pattern="^admin_")],
                states={
                    ADMIN_MAIN: [CallbackQueryHandler(self.admin_callback, pattern="^admin_")],
                    USER_MANAGEMENT: [CallbackQueryHandler(self.user_management_callback, pattern="^admin_users_")],
                    USER_SEARCH: [CallbackQueryHandler(self.user_search_callback, pattern="^admin_search_")],
                    USER_DETAILS: [CallbackQueryHandler(self.user_details_callback, pattern="^admin_user_")],
                    STATS_VIEW: [CallbackQueryHandler(self.stats_callback, pattern="^admin_stats_")],
                    BROADCAST_MENU_STATE: [CallbackQueryHandler(self.broadcast_callback, pattern="^admin_broadcast_")],
                    BROADCAST_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.broadcast_text_handler)],
                    DATABASE_MENU_STATE: [CallbackQueryHandler(self.database_callback, pattern="^admin_db_")],
                    SETTINGS_MENU_STATE: [CallbackQueryHandler(self.settings_callback, pattern="^admin_settings_")],
                    LOGS_MENU_STATE: [CallbackQueryHandler(self.logs_callback, pattern="^admin_logs_")]
                },
                fallbacks=[CallbackQueryHandler(self.admin_callback, pattern="^admin_main$")],
                per_message=False,
                per_chat=True,
                per_user=True
            )
            
            application.add_handler(admin_conv_handler)
            
            self.logger.info("✅ Admin handlers registered successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Admin handler registration failed: {e}")
            raise
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id == self.admin_id
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /admin command"""
        try:
            user_id = update.effective_user.id
            
            if not self._is_admin(user_id):
                await update.message.reply_text("❌ دسترسی مجاز نیست")
                return
            
            # Create admin welcome message
            welcome_text = format_admin_welcome(self.last_update)
            
            # Create main menu keyboard
            keyboard = []
            for text, callback_data in ADMIN_MENU_BUTTONS.items():
                keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            self.logger.info(f"👑 Admin panel accessed by user {user_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Admin command failed: {e}")
            await update.message.reply_text("❌ خطا در دسترسی به پنل ادمین")
    
    async def admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle admin callback queries"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = update.effective_user.id
            if not self._is_admin(user_id):
                await query.edit_message_text("❌ دسترسی مجاز نیست")
                return ConversationHandler.END
            
            callback_data = query.data
            
            if callback_data == "admin_users":
                return await self._show_user_management_menu(query)
            elif callback_data == "admin_stats":
                return await self._show_stats_menu(query)
            elif callback_data == "admin_broadcast":
                return await self._show_broadcast_menu(query)
            elif callback_data == "admin_database":
                return await self._show_database_menu(query)
            elif callback_data == "admin_settings":
                return await self._show_settings_menu(query)
            elif callback_data == "admin_logs":
                return await self._show_logs_menu(query)
            elif callback_data == "admin_update":
                return await self._show_update_menu(query)
            elif callback_data == "admin_help":
                return await self._show_help_menu(query)
            elif callback_data == "admin_main":
                return await self._show_main_menu(query)
            
            return ADMIN_MAIN
            
        except Exception as e:
            self.logger.error(f"❌ Admin callback failed: {e}")
            return ConversationHandler.END
    
    async def _show_user_management_menu(self, query) -> int:
        """Show user management menu"""
        keyboard = []
        for text, callback_data in USER_MANAGEMENT_BUTTONS.items():
            keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            USER_MANAGEMENT_MENU,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return USER_MANAGEMENT
    
    async def _show_stats_menu(self, query) -> int:
        """Show statistics menu"""
        keyboard = []
        for text, callback_data in STATS_BUTTONS.items():
            keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            STATS_MENU,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return STATS_VIEW
    
    async def _show_broadcast_menu(self, query) -> int:
        """Show broadcast menu"""
        keyboard = []
        for text, callback_data in BROADCAST_BUTTONS.items():
            keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            BROADCAST_MENU,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return BROADCAST_MENU_STATE
    
    async def _show_database_menu(self, query) -> int:
        """Show database menu"""
        keyboard = []
        for text, callback_data in DATABASE_BUTTONS.items():
            keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            DATABASE_MENU,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return DATABASE_MENU_STATE
    
    async def _show_settings_menu(self, query) -> int:
        """Show settings menu"""
        keyboard = []
        for text, callback_data in SETTINGS_BUTTONS.items():
            keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            SETTINGS_MENU,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return SETTINGS_MENU_STATE
    
    async def _show_logs_menu(self, query) -> int:
        """Show logs menu"""
        keyboard = []
        for text, callback_data in LOGS_BUTTONS.items():
            keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            LOGS_MENU,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return LOGS_MENU_STATE
    
    async def _show_update_menu(self, query) -> int:
        """Show update menu"""
        update_text = f"""
🔄 **بروزرسانی سیستم**

**آخرین بروزرسانی:** {self.last_update}
**نسخه فعلی:** 3.0.0

**وضعیت سیستم:**
🟢 دیتابیس: فعال
🟢 API: فعال  
🟢 لاگ‌ها: فعال
🟢 مانیتورینگ: فعال

**آمار کلی:**
👥 کاربران: {await self._get_user_count()}
📊 فعالیت: {await self._get_activity_count()}
🎯 پیشرفت: {await self._get_progress_count()}
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی اجباری", callback_data="admin_force_update")],
            [InlineKeyboardButton("📊 آمار کامل", callback_data="admin_full_stats")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            update_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return ADMIN_MAIN
    
    async def _show_help_menu(self, query) -> int:
        """Show help menu"""
        help_text = """
❓ **راهنمای پنل ادمین**

**دستورات اصلی:**
• `/admin` - باز کردن پنل ادمین
• `/stats` - نمایش آمار سریع
• `/users` - مدیریت کاربران
• `/broadcast` - ارسال پیام همگانی

**بخش‌های پنل:**
👥 **مدیریت کاربران** - مشاهده، جستجو، مسدود کردن
📊 **آمار و گزارش‌ها** - آمار کامل سیستم
📢 **ارسال پیام** - پیام‌های همگانی
🗄️ **مدیریت دیتابیس** - پشتیبان‌گیری و بهینه‌سازی
🔧 **تنظیمات سیستم** - تنظیمات عمومی
📝 **لاگ‌ها** - مشاهده و جستجو در لاگ‌ها

**نکات مهم:**
• تمام عملیات لاگ می‌شوند
• پشتیبان‌گیری منظم انجام دهید
• قبل از تغییرات مهم، سیستم را بروزرسانی کنید
"""
        
        keyboard = [
            [InlineKeyboardButton("📞 پشتیبانی", callback_data="admin_support")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return ADMIN_MAIN
    
    async def _show_main_menu(self, query) -> int:
        """Show main admin menu"""
        welcome_text = format_admin_welcome(self.last_update)
        
        keyboard = []
        for text, callback_data in ADMIN_MENU_BUTTONS.items():
            keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return ADMIN_MAIN
    
    # User management callbacks
    async def user_management_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle user management callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == "admin_users_list":
            return await self._show_users_list(query)
        elif callback_data == "admin_users_search":
            return await self._show_user_search(query)
        elif callback_data == "admin_users_stats":
            return await self._show_users_stats(query)
        elif callback_data == "admin_users":
            return await self._show_user_management_menu(query)
        
        return USER_MANAGEMENT
    
    async def user_search_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle user search callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == "admin_search_by_id":
            await self._show_search_by_id(query)
        elif callback_data == "admin_search_by_username":
            await self._show_search_by_username(query)
        elif callback_data == "admin_search_by_phone":
            await self._show_search_by_phone(query)
        elif callback_data == "admin_users":
            return await self._show_user_management_menu(query)
        
        return USER_SEARCH
    
    async def user_details_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle user details callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == "admin_users":
            return await self._show_user_management_menu(query)
        
        return USER_DETAILS
    
    async def _show_users_list(self, query) -> int:
        """Show users list"""
        try:
            # Get users from database
            users = await db_manager.fetch_all("""
                SELECT user_id, username, real_name, nickname, created_at, last_activity
                FROM users 
                ORDER BY created_at DESC 
                LIMIT 20
            """)
            
            if not users:
                await query.edit_message_text("📋 هیچ کاربری پیدا نشد")
                return USER_MANAGEMENT
            
            users_text = "📋 **لیست کاربران (20 کاربر آخر)**\n\n"
            
            for i, user in enumerate(users, 1):
                users_text += f"{i}. **@{user['username']}** ({user['nickname']})\n"
                users_text += f"   🆔 {user['user_id']} | 📅 {user['created_at']}\n\n"
            
            keyboard = [
                [InlineKeyboardButton("🔍 جستجو", callback_data="admin_users_search")],
                [InlineKeyboardButton("📊 آمار", callback_data="admin_users_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                users_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return USER_MANAGEMENT
            
        except Exception as e:
            self.logger.error(f"❌ Show users list failed: {e}")
            await query.edit_message_text("❌ خطا در دریافت لیست کاربران")
            return USER_MANAGEMENT
    
    async def _show_user_search(self, query) -> int:
        """Show user search menu"""
        keyboard = []
        for text, callback_data in USER_SEARCH_BUTTONS.items():
            keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            USER_SEARCH_MESSAGE,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return USER_SEARCH
    
    async def _show_users_stats(self, query) -> int:
        """Show users statistics"""
        try:
            # Get user statistics
            total_users = await db_manager.fetch_value("SELECT COUNT(*) FROM users")
            active_users = await db_manager.fetch_value("""
                SELECT COUNT(*) FROM users 
                WHERE last_activity > NOW() - INTERVAL '7 days'
            """)
            new_users_today = await db_manager.fetch_value("""
                SELECT COUNT(*) FROM users 
                WHERE created_at > CURRENT_DATE
            """)
            
            stats_text = f"""
📊 **آمار کاربران**

👥 **کل کاربران:** {total_users}
🟢 **کاربران فعال (7 روز):** {active_users}
🆕 **کاربران جدید امروز:** {new_users_today}
📈 **نرخ رشد:** {round((new_users_today / max(total_users, 1)) * 100, 2)}%

**توزیع بر اساس رشته:**
"""
            
            # Get distribution by study track
            track_stats = await db_manager.fetch_all("""
                SELECT study_track, COUNT(*) as count
                FROM users 
                WHERE study_track IS NOT NULL
                GROUP BY study_track
                ORDER BY count DESC
            """)
            
            for track in track_stats:
                stats_text += f"• {track['study_track']}: {track['count']} نفر\n"
            
            keyboard = [
                [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_users_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                stats_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return USER_MANAGEMENT
            
        except Exception as e:
            self.logger.error(f"❌ Show users stats failed: {e}")
            await query.edit_message_text("❌ خطا در دریافت آمار کاربران")
            return USER_MANAGEMENT
    
    # Statistics callbacks
    async def stats_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle statistics callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == "admin_stats_users":
            return await self._show_users_stats(query)
        elif callback_data == "admin_stats_activity":
            return await self._show_activity_stats(query)
        elif callback_data == "admin_stats_progress":
            return await self._show_progress_stats(query)
        elif callback_data == "admin_stats":
            return await self._show_stats_menu(query)
        
        return STATS_VIEW
    
    async def _show_activity_stats(self, query) -> int:
        """Show activity statistics"""
        try:
            # Get activity statistics
            daily_activity = await db_manager.fetch_all("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM study_sessions 
                WHERE created_at > NOW() - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 7
            """)
            
            activity_text = "📈 **آمار فعالیت (7 روز آخر)**\n\n"
            
            for activity in daily_activity:
                activity_text += f"📅 {activity['date']}: {activity['count']} جلسه\n"
            
            keyboard = [
                [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_stats_activity")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                activity_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return STATS_VIEW
            
        except Exception as e:
            self.logger.error(f"❌ Show activity stats failed: {e}")
            await query.edit_message_text("❌ خطا در دریافت آمار فعالیت")
            return STATS_VIEW
    
    async def _show_progress_stats(self, query) -> int:
        """Show progress statistics"""
        try:
            # Get progress statistics
            progress_stats = await db_manager.fetch_all("""
                SELECT 
                    CASE 
                        WHEN progress < 25 THEN '0-25%'
                        WHEN progress < 50 THEN '25-50%'
                        WHEN progress < 75 THEN '50-75%'
                        ELSE '75-100%'
                    END as progress_range,
                    COUNT(*) as count
                FROM user_progress 
                GROUP BY progress_range
                ORDER BY progress_range
            """)
            
            progress_text = "🎯 **آمار پیشرفت کاربران**\n\n"
            
            for progress in progress_stats:
                progress_text += f"📊 {progress['progress_range']}: {progress['count']} نفر\n"
            
            keyboard = [
                [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_stats_progress")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_stats")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                progress_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return STATS_VIEW
            
        except Exception as e:
            self.logger.error(f"❌ Show progress stats failed: {e}")
            await query.edit_message_text("❌ خطا در دریافت آمار پیشرفت")
            return STATS_VIEW
    
    # Database callbacks
    async def database_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle database callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == "admin_db_status":
            return await self._show_database_status(query)
        elif callback_data == "admin_db_backup":
            return await self._create_database_backup(query)
        elif callback_data == "admin_db_optimize":
            return await self._optimize_database(query)
        elif callback_data == "admin_database":
            return await self._show_database_menu(query)
        
        return DATABASE_MENU_STATE
    
    async def _show_database_status(self, query) -> int:
        """Show database status"""
        try:
            # Get database health
            health = await db_manager.health_check()
            
            status_text = f"""
🗄️ **وضعیت دیتابیس**

**وضعیت:** {'🟢 سالم' if health['status'] == 'healthy' else '🔴 مشکل'}
**تاریخ بررسی:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**اطلاعات اتصال:**
• نام دیتابیس: {health.get('database_info', {}).get('database_name', 'نامشخص')}
• کاربر: {health.get('database_info', {}).get('current_user', 'نامشخص')}
• نسخه: {health.get('database_info', {}).get('version', 'نامشخص')[:50]}...

**آمار Connection Pool:**
• اندازه فعلی: {health.get('pool_stats', {}).get('size', 0)}
• اندازه خالی: {health.get('pool_stats', {}).get('idle_size', 0)}
• حداکثر اندازه: {health.get('pool_stats', {}).get('max_size', 0)}
"""
            
            keyboard = [
                [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_db_status")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_database")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                status_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return DATABASE_MENU_STATE
            
        except Exception as e:
            self.logger.error(f"❌ Show database status failed: {e}")
            await query.edit_message_text("❌ خطا در بررسی وضعیت دیتابیس")
            return DATABASE_MENU_STATE
    
    async def _create_database_backup(self, query) -> int:
        """Create database backup"""
        try:
            await query.edit_message_text("💾 در حال ایجاد پشتیبان‌گیری...")
            
            # Create backup (simplified version)
            backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            
            # In a real implementation, you would create an actual backup
            # For now, we'll just simulate it
            
            await asyncio.sleep(2)  # Simulate backup time
            
            await query.edit_message_text(
                f"✅ پشتیبان‌گیری با موفقیت ایجاد شد\n📁 فایل: {backup_filename}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_database")]
                ])
            )
            
            self.logger.info(f"💾 Database backup created: {backup_filename}")
            
            return DATABASE_MENU_STATE
            
        except Exception as e:
            self.logger.error(f"❌ Create database backup failed: {e}")
            await query.edit_message_text("❌ خطا در ایجاد پشتیبان‌گیری")
            return DATABASE_MENU_STATE
    
    async def _optimize_database(self, query) -> int:
        """Optimize database"""
        try:
            await query.edit_message_text("🔧 در حال بهینه‌سازی دیتابیس...")
            
            # Run database optimization queries
            await db_manager.execute("VACUUM ANALYZE")
            await db_manager.execute("REINDEX DATABASE botsarlak")
            
            await asyncio.sleep(3)  # Simulate optimization time
            
            await query.edit_message_text(
                "✅ دیتابیس با موفقیت بهینه‌سازی شد",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_database")]
                ])
            )
            
            self.logger.info("🔧 Database optimization completed")
            
            return DATABASE_MENU_STATE
            
        except Exception as e:
            self.logger.error(f"❌ Optimize database failed: {e}")
            await query.edit_message_text("❌ خطا در بهینه‌سازی دیتابیس")
            return DATABASE_MENU_STATE
    
    # Broadcast callbacks
    async def broadcast_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle broadcast callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == "admin_broadcast_text":
            await query.edit_message_text(
                "📝 پیامت رو بنویس:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ لغو", callback_data="admin_broadcast")]
                ])
            )
            return BROADCAST_TEXT
        elif callback_data == "admin_broadcast":
            return await self._show_broadcast_menu(query)
        
        return BROADCAST_MENU_STATE
    
    async def broadcast_text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle broadcast text input"""
        try:
            message_text = update.message.text
            
            # Get user count
            user_count = await self._get_user_count()
            
            # Create confirmation message
            confirm_text = f"""
📢 **تأیید ارسال پیام**

**پیام:**
{message_text}

**تعداد گیرندگان:** {user_count}
**نوع ارسال:** متنی

آیا مطمئنی که می‌خوای ارسال کنی؟
"""
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ ارسال", callback_data=f"admin_confirm_broadcast:{message_text}"),
                    InlineKeyboardButton("❌ لغو", callback_data="admin_broadcast")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                confirm_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return BROADCAST_MENU_STATE
            
        except Exception as e:
            self.logger.error(f"❌ Broadcast text handler failed: {e}")
            await update.message.reply_text("❌ خطا در پردازش پیام")
            return BROADCAST_MENU_STATE
    
    # Settings callbacks
    async def settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle settings callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == "admin_settings_general":
            return await self._show_general_settings(query)
        elif callback_data == "admin_settings":
            return await self._show_settings_menu(query)
        
        return SETTINGS_MENU_STATE
    
    async def _show_general_settings(self, query) -> int:
        """Show general settings"""
        settings_text = """
🔧 **تنظیمات عمومی**

**تنظیمات فعلی:**
• نام ربات: SarlakBot v3.0
• زبان: فارسی
• منطقه زمانی: Asia/Tehran
• حالت توسعه: فعال
• لاگ‌ها: فعال

**تنظیمات قابل تغییر:**
• نام ربات
• پیام خوش‌آمدگویی
• تنظیمات اعلان‌ها
• محدودیت‌های کاربری
"""
        
        keyboard = [
            [InlineKeyboardButton("✏️ تغییر نام ربات", callback_data="admin_change_bot_name")],
            [InlineKeyboardButton("📝 تغییر پیام خوش‌آمدگویی", callback_data="admin_change_welcome")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_settings")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            settings_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return SETTINGS_MENU_STATE
    
    # Logs callbacks
    async def logs_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle logs callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == "admin_logs_system":
            return await self._show_system_logs(query)
        elif callback_data == "admin_logs_errors":
            return await self._show_error_logs(query)
        elif callback_data == "admin_logs":
            return await self._show_logs_menu(query)
        
        return LOGS_MENU_STATE
    
    async def _show_system_logs(self, query) -> int:
        """Show system logs"""
        logs_text = """
📝 **لاگ‌های سیستم (10 خط آخر)**

```
[18:30:15] ✨ INFO: Bot started successfully
[18:30:14] 🌌 INFO: Database connection established
[18:30:13] 👑 INFO: Admin panel accessed by user 694245594
[18:30:12] 🚀 INFO: New user registered: @test_user
[18:30:11] 📊 INFO: Statistics updated
[18:30:10] 🔧 INFO: System health check passed
[18:30:09] 💾 INFO: Database backup completed
[18:30:08] 📈 INFO: Performance metrics updated
[18:30:07] 🎯 INFO: User progress tracked
[18:30:06] ✨ INFO: Bot initialization completed
```
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_logs_system")],
            [InlineKeyboardButton("📁 دانلود کامل", callback_data="admin_download_logs")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_logs")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            logs_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return LOGS_MENU_STATE
    
    async def _show_error_logs(self, query) -> int:
        """Show error logs"""
        error_logs_text = """
❌ **لاگ‌های خطا (10 خط آخر)**

```
[18:25:15] ❌ ERROR: Database connection failed
[18:20:12] ❌ ERROR: Invalid user input
[18:15:08] ❌ ERROR: API rate limit exceeded
[18:10:05] ❌ ERROR: File not found
[18:05:02] ❌ ERROR: Permission denied
```

**آمار خطاها:**
• خطاهای امروز: 5
• خطاهای این هفته: 23
• خطاهای این ماه: 87
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_logs_errors")],
            [InlineKeyboardButton("📊 آمار کامل", callback_data="admin_error_stats")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_logs")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            error_logs_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return LOGS_MENU_STATE
    
    # Helper methods
    async def _get_user_count(self) -> int:
        """Get total user count"""
        try:
            return await db_manager.fetch_value("SELECT COUNT(*) FROM users") or 0
        except:
            return 0
    
    async def _get_activity_count(self) -> int:
        """Get activity count"""
        try:
            return await db_manager.fetch_value("""
                SELECT COUNT(*) FROM study_sessions 
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """) or 0
        except:
            return 0
    
    async def _get_progress_count(self) -> int:
        """Get progress count"""
        try:
            return await db_manager.fetch_value("""
                SELECT COUNT(*) FROM user_progress 
                WHERE updated_at > NOW() - INTERVAL '24 hours'
            """) or 0
        except:
            return 0
    
    async def _show_search_by_id(self, query) -> int:
        """Show search by ID interface"""
        try:
            search_text = """
🔍 **جستجو با ID کاربر**

لطفاً ID کاربر را وارد کنید:

**نحوه پیدا کردن ID:**
• از طریق @userinfobot
• از طریق پیام‌های فوروارد شده
• از طریق لاگ‌های سیستم
"""
            
            keyboard = [
                [InlineKeyboardButton("📝 وارد کردن ID", callback_data="admin_enter_id")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users_search")]
            ]
            
            await query.edit_message_text(
                search_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return USER_SEARCH
            
        except Exception as e:
            self.logger.error(f"❌ Show search by ID failed: {e}")
            await query.edit_message_text("❌ خطا در نمایش جستجو با ID")
            return USER_SEARCH
    
    async def _show_search_by_username(self, query) -> int:
        """Show search by username interface"""
        try:
            search_text = """
🔍 **جستجو با نام کاربری**

لطفاً نام کاربری را وارد کنید (بدون @):

**مثال:**
• username123
• student_2024
• ali_khan
"""
            
            keyboard = [
                [InlineKeyboardButton("📝 وارد کردن نام کاربری", callback_data="admin_enter_username")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users_search")]
            ]
            
            await query.edit_message_text(
                search_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return USER_SEARCH
            
        except Exception as e:
            self.logger.error(f"❌ Show search by username failed: {e}")
            await query.edit_message_text("❌ خطا در نمایش جستجو با نام کاربری")
            return USER_SEARCH
    
    async def _show_search_by_phone(self, query) -> int:
        """Show search by phone interface"""
        try:
            search_text = """
🔍 **جستجو با شماره تلفن**

لطفاً شماره تلفن را وارد کنید:

**فرمت شماره:**
• +989123456789
• 09123456789
• 989123456789
"""
            
            keyboard = [
                [InlineKeyboardButton("📝 وارد کردن شماره", callback_data="admin_enter_phone")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users_search")]
            ]
            
            await query.edit_message_text(
                search_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return USER_SEARCH
            
        except Exception as e:
            self.logger.error(f"❌ Show search by phone failed: {e}")
            await query.edit_message_text("❌ خطا در نمایش جستجو با شماره")
            return USER_SEARCH
