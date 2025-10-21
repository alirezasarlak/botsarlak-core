"""
🌌 SarlakBot v3.0 - Clean Start Handler
Clean, async, production-ready start command with proper user detection
"""

import asyncio
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError

from src.config import config
from src.utils.logging import get_logger
from src.database.connection import db_manager
from src.utils.error_handler import safe_async_handler

logger = get_logger(__name__)


class StartHandler:
    """
    🌌 Clean Start Handler
    Handles /start command with proper user detection and flow
    """
    
    def __init__(self):
        self.logger = logger
    
    async def register(self, application: Application) -> None:
        """Register start command and related handlers"""
        try:
            self.logger.info("🚀 Registering start command handler...")
            
            # Register command handler
            application.add_handler(CommandHandler("start", self.start_command))
            
            # Register callback handlers
            application.add_handler(CallbackQueryHandler(self.start_profile_callback, pattern="^start_profile$"))
            application.add_handler(CallbackQueryHandler(self.go_home_callback, pattern="^go_home$"))
            application.add_handler(CallbackQueryHandler(self.show_profile_callback, pattern="^show_profile$"))
            application.add_handler(CallbackQueryHandler(self.edit_profile_callback, pattern="^edit_profile$"))
            
            self.logger.info("✅ Start command handler registered successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Start command handler registration failed: {e}")
            raise
    
    @safe_async_handler
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command with proper user detection"""
        try:
            user = update.effective_user
            user_id = user.id
            
            self.logger.info(f"🚀 User {user_id} started the bot")
            
            # Check if user exists in database
            user_data = await self._get_user_data(user_id)
            
            if user_data:
                # User exists - show main menu
                await self._show_main_menu(update, user_data)
            else:
                # New user - show welcome and profile setup option
                await self._show_welcome_new_user(update)
                
        except Exception as e:
            self.logger.error(f"❌ Start command failed: {e}")
            await self._send_error_message(update, "مشکلی پیش آمد. لطفا دوباره تلاش کنید.")
    
    async def _get_user_data(self, user_id: int) -> Optional[dict]:
        """Get user data from database"""
        try:
            user_data = await db_manager.fetch_one(
                "SELECT * FROM users WHERE id = $1", user_id
            )
            return user_data
        except Exception as e:
            self.logger.error(f"❌ Failed to get user data: {e}")
            return None
    
    async def _show_main_menu(self, update: Update, user_data: dict) -> None:
        """Show main menu for existing users"""
        try:
            # Create main menu keyboard
            keyboard = [
                [InlineKeyboardButton("👤 پروفایل من", callback_data="show_profile")],
                [InlineKeyboardButton("✏️ ویرایش پروفایل", callback_data="edit_profile")],
                [InlineKeyboardButton("📊 گزارش روزانه", callback_data="daily_report")],
                [InlineKeyboardButton("🏆 لیگ", callback_data="league")],
                [InlineKeyboardButton("❓ سوال و جواب", callback_data="qa")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_text = f"""
🌌 خوش آمدید {user_data.get('first_name', 'کاربر')}!

به سفر کیهانی یادگیری خوش آمدید! 🚀
چه کاری می‌خواهید انجام دهید؟
            """.strip()
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to show main menu: {e}")
            await self._send_error_message(update, "مشکلی در نمایش منو پیش آمد.")
    
    async def _show_welcome_new_user(self, update: Update) -> None:
        """Show welcome message for new users"""
        try:
            keyboard = [
                [InlineKeyboardButton("🚀 شروع ساخت پروفایل", callback_data="start_profile")],
                [InlineKeyboardButton("🏠 منوی اصلی", callback_data="go_home")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_text = """
🌌 به سارلاک خوش آمدید!

سلام! من دستیار هوشمند شما برای سفر کیهانی یادگیری هستم! 🚀

برای شروع، ابتدا پروفایل خود را بسازید تا بتوانم بهتر به شما کمک کنم.

آماده‌اید که سفر کیهانی یادگیری را شروع کنیم؟ ✨
            """.strip()
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to show welcome: {e}")
            await self._send_error_message(update, "مشکلی در نمایش پیام خوش‌آمدگویی پیش آمد.")
    
    @safe_async_handler
    async def start_profile_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle start profile callback"""
        try:
            query = update.callback_query
            await query.answer()
            
            # Start profile creation conversation
            await query.edit_message_text(
                "🚀 عالی! بیایید پروفایل شما را بسازیم.\n\nلطفا نام کامل خود را وارد کنید:",
                reply_markup=None
            )
            
            # Set conversation state
            context.user_data['conversation_state'] = 'profile_name'
            
        except Exception as e:
            self.logger.error(f"❌ Start profile callback failed: {e}")
            await self._send_error_message(update, "مشکلی در شروع ساخت پروفایل پیش آمد.")
    
    @safe_async_handler
    async def go_home_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle go home callback"""
        try:
            query = update.callback_query
            await query.answer()
            
            # Show main menu
            user_id = query.from_user.id
            user_data = await self._get_user_data(user_id)
            
            if user_data:
                await self._show_main_menu_from_callback(query, user_data)
            else:
                await self._show_welcome_new_user_from_callback(query)
                
        except Exception as e:
            self.logger.error(f"❌ Go home callback failed: {e}")
            await self._send_error_message(update, "مشکلی در بازگشت به منو پیش آمد.")
    
    @safe_async_handler
    async def show_profile_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle show profile callback"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            user_data = await self._get_user_data(user_id)
            
            if user_data:
                profile_text = f"""
👤 پروفایل شما:

📝 نام: {user_data.get('first_name', 'نامشخص')} {user_data.get('last_name', '')}
🎓 سطح تحصیلی: {user_data.get('grade_level', 'نامشخص')}
🎯 هدف: {user_data.get('target_goal', 'نامشخص')}
📅 تاریخ عضویت: {user_data.get('joined_at', 'نامشخص')}
                """.strip()
                
                keyboard = [
                    [InlineKeyboardButton("✏️ ویرایش پروفایل", callback_data="edit_profile")],
                    [InlineKeyboardButton("🏠 منوی اصلی", callback_data="go_home")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    profile_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                await query.edit_message_text(
                    "❌ پروفایل شما یافت نشد. لطفا ابتدا پروفایل خود را بسازید.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🚀 ساخت پروفایل", callback_data="start_profile")
                    ]])
                )
                
        except Exception as e:
            self.logger.error(f"❌ Show profile callback failed: {e}")
            await self._send_error_message(update, "مشکلی در نمایش پروفایل پیش آمد.")
    
    @safe_async_handler
    async def edit_profile_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle edit profile callback"""
        try:
            query = update.callback_query
            await query.answer()
            
            await query.edit_message_text(
                "✏️ ویرایش پروفایل\n\nلطفا نام جدید خود را وارد کنید:",
                reply_markup=None
            )
            
            # Set conversation state
            context.user_data['conversation_state'] = 'edit_name'
            
        except Exception as e:
            self.logger.error(f"❌ Edit profile callback failed: {e}")
            await self._send_error_message(update, "مشکلی در ویرایش پروفایل پیش آمد.")
    
    async def _show_main_menu_from_callback(self, query, user_data: dict) -> None:
        """Show main menu from callback"""
        keyboard = [
            [InlineKeyboardButton("👤 پروفایل من", callback_data="show_profile")],
            [InlineKeyboardButton("✏️ ویرایش پروفایل", callback_data="edit_profile")],
            [InlineKeyboardButton("📊 گزارش روزانه", callback_data="daily_report")],
            [InlineKeyboardButton("🏆 لیگ", callback_data="league")],
            [InlineKeyboardButton("❓ سوال و جواب", callback_data="qa")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🌌 خوش آمدید {user_data.get('first_name', 'کاربر')}!

به سفر کیهانی یادگیری خوش آمدید! 🚀
چه کاری می‌خواهید انجام دهید؟
        """.strip()
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def _show_welcome_new_user_from_callback(self, query) -> None:
        """Show welcome message from callback"""
        keyboard = [
            [InlineKeyboardButton("🚀 شروع ساخت پروفایل", callback_data="start_profile")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="go_home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🌌 به سارلاک خوش آمدید!

سلام! من دستیار هوشمند شما برای سفر کیهانی یادگیری هستم! 🚀

برای شروع، ابتدا پروفایل خود را بسازید تا بتوانم بهتر به شما کمک کنم.

آماده‌اید که سفر کیهانی یادگیری را شروع کنیم؟ ✨
        """.strip()
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def _send_error_message(self, update: Update, message: str) -> None:
        """Send error message to user"""
        try:
            if update.callback_query:
                await update.callback_query.edit_message_text(message)
            else:
                await update.message.reply_text(message)
        except Exception as e:
            self.logger.error(f"❌ Failed to send error message: {e}")


# Global instance
start_handler = StartHandler()
