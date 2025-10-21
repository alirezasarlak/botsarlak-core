"""
🌌 SarlakBot v3.0 - Profile Creation Handler
Clean, async ConversationHandler for profile creation flow
"""

import asyncio
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, 
    ConversationHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    CommandHandler,
    ContextTypes,
    filters
)
from telegram.error import TelegramError

from src.config import config
from src.utils.logging import get_logger
from src.database.connection import db_manager
from src.utils.error_handler import safe_async_handler
from src.utils.input_validator import input_validator

logger = get_logger(__name__)

# Conversation states
PROFILE_NAME, PROFILE_GRADE, PROFILE_GOAL, PROFILE_CONFIRM = range(4)


class ProfileCreationHandler:
    """
    🌌 Profile Creation Handler
    Clean ConversationHandler for profile creation flow
    """
    
    def __init__(self):
        self.logger = logger
    
    async def register(self, application: Application) -> None:
        """Register profile creation conversation handler"""
        try:
            self.logger.info("🚀 Registering profile creation handler...")
            
            # Create conversation handler
            conversation_handler = ConversationHandler(
                entry_points=[
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_input)
                ],
                states={
                    PROFILE_NAME: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_name_input)
                    ],
                    PROFILE_GRADE: [
                        CallbackQueryHandler(self.handle_grade_selection, pattern="^grade_")
                    ],
                    PROFILE_GOAL: [
                        CallbackQueryHandler(self.handle_goal_selection, pattern="^goal_")
                    ],
                    PROFILE_CONFIRM: [
                        CallbackQueryHandler(self.handle_confirmation, pattern="^confirm_")
                    ]
                },
                fallbacks=[
                    CommandHandler("cancel", self.cancel_command),
                    CallbackQueryHandler(self.cancel_callback, pattern="^cancel$")
                ],
                name="profile_creation",
                persistent=True,
                per_message=False,
                per_chat=True,
                per_user=True
            )
            
            application.add_handler(conversation_handler)
            self.logger.info("✅ Profile creation handler registered successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Profile creation handler registration failed: {e}")
            raise
    
    @safe_async_handler
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle text input to start profile creation"""
        try:
            # Check if this is a profile creation request
            if context.user_data.get('conversation_state') == 'profile_name':
                return await self.handle_name_input(update, context)
            elif context.user_data.get('conversation_state') == 'edit_name':
                return await self.handle_edit_name_input(update, context)
            else:
                # Not in profile creation mode
                return ConversationHandler.END
                
        except Exception as e:
            self.logger.error(f"❌ Handle text input failed: {e}")
            await self._send_error_message(update, "مشکلی در پردازش ورودی پیش آمد.")
            return ConversationHandler.END
    
    @safe_async_handler
    async def handle_name_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle name input"""
        try:
            name = update.message.text.strip()
            
            # Validate name
            if not self._validate_name(name):
                await update.message.reply_text(
                    "❌ نام وارد شده معتبر نیست. لطفا نام کامل خود را وارد کنید:"
                )
                return PROFILE_NAME
            
            # Sanitize input
            sanitized_name = input_validator.sanitize_input(name)
            
            # Store name
            context.user_data['profile_name'] = sanitized_name
            
            # Ask for grade level
            keyboard = [
                [InlineKeyboardButton("🎓 دبیرستان", callback_data="grade_highschool")],
                [InlineKeyboardButton("🎓 پیش دانشگاهی", callback_data="grade_pre_uni")],
                [InlineKeyboardButton("🎓 دانشگاه", callback_data="grade_university")],
                [InlineKeyboardButton("❌ لغو", callback_data="cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ نام شما: {sanitized_name}\n\n🎓 لطفا سطح تحصیلی خود را انتخاب کنید:",
                reply_markup=reply_markup
            )
            
            return PROFILE_GRADE
            
        except Exception as e:
            self.logger.error(f"❌ Handle name input failed: {e}")
            await self._send_error_message(update, "مشکلی در پردازش نام پیش آمد.")
            return ConversationHandler.END
    
    @safe_async_handler
    async def handle_edit_name_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle edit name input"""
        try:
            name = update.message.text.strip()
            
            # Validate name
            if not self._validate_name(name):
                await update.message.reply_text(
                    "❌ نام وارد شده معتبر نیست. لطفا نام کامل خود را وارد کنید:"
                )
                return ConversationHandler.END
            
            # Sanitize input
            sanitized_name = input_validator.sanitize_input(name)
            
            # Update user in database
            user_id = update.effective_user.id
            await self._update_user_name(user_id, sanitized_name)
            
            await update.message.reply_text(
                f"✅ نام شما به {sanitized_name} تغییر یافت!",
                reply_markup=ReplyKeyboardRemove()
            )
            
            # Clear conversation state
            context.user_data.pop('conversation_state', None)
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"❌ Handle edit name input failed: {e}")
            await self._send_error_message(update, "مشکلی در ویرایش نام پیش آمد.")
            return ConversationHandler.END
    
    @safe_async_handler
    async def handle_grade_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle grade level selection"""
        try:
            query = update.callback_query
            await query.answer()
            
            grade = query.data.replace('grade_', '')
            grade_text = self._get_grade_text(grade)
            
            # Store grade
            context.user_data['profile_grade'] = grade
            
            # Ask for goal
            keyboard = [
                [InlineKeyboardButton("🎯 کنکور ریاضی", callback_data="goal_math")],
                [InlineKeyboardButton("🎯 کنکور تجربی", callback_data="goal_bio")],
                [InlineKeyboardButton("🎯 کنکور انسانی", callback_data="goal_humanities")],
                [InlineKeyboardButton("🎯 کنکور هنر", callback_data="goal_art")],
                [InlineKeyboardButton("🎯 کنکور زبان", callback_data="goal_language")],
                [InlineKeyboardButton("❌ لغو", callback_data="cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"✅ سطح تحصیلی: {grade_text}\n\n🎯 لطفا هدف خود را انتخاب کنید:",
                reply_markup=reply_markup
            )
            
            return PROFILE_GOAL
            
        except Exception as e:
            self.logger.error(f"❌ Handle grade selection failed: {e}")
            await self._send_error_message(update, "مشکلی در انتخاب سطح تحصیلی پیش آمد.")
            return ConversationHandler.END
    
    @safe_async_handler
    async def handle_goal_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle goal selection"""
        try:
            query = update.callback_query
            await query.answer()
            
            goal = query.data.replace('goal_', '')
            goal_text = self._get_goal_text(goal)
            
            # Store goal
            context.user_data['profile_goal'] = goal
            
            # Show confirmation
            name = context.user_data.get('profile_name', 'نامشخص')
            grade = self._get_grade_text(context.user_data.get('profile_grade', ''))
            
            keyboard = [
                [InlineKeyboardButton("✅ تایید و ذخیره", callback_data="confirm_yes")],
                [InlineKeyboardButton("❌ لغو", callback_data="confirm_no")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            confirmation_text = f"""
📋 تایید اطلاعات پروفایل:

👤 نام: {name}
🎓 سطح تحصیلی: {grade}
🎯 هدف: {goal_text}

آیا اطلاعات درست است؟
            """.strip()
            
            await query.edit_message_text(
                confirmation_text,
                reply_markup=reply_markup
            )
            
            return PROFILE_CONFIRM
            
        except Exception as e:
            self.logger.error(f"❌ Handle goal selection failed: {e}")
            await self._send_error_message(update, "مشکلی در انتخاب هدف پیش آمد.")
            return ConversationHandler.END
    
    @safe_async_handler
    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle profile confirmation"""
        try:
            query = update.callback_query
            await query.answer()
            
            if query.data == 'confirm_yes':
                # Save profile to database
                user_id = query.from_user.id
                success = await self._save_profile(user_id, context.user_data)
                
                if success:
                    await query.edit_message_text(
                        "🎉 پروفایل شما با موفقیت ساخته شد!\n\nحالا می‌توانید از تمام امکانات ربات استفاده کنید.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🏠 منوی اصلی", callback_data="go_home")
                        ]])
                    )
                else:
                    await query.edit_message_text(
                        "❌ مشکلی در ذخیره پروفایل پیش آمد. لطفا دوباره تلاش کنید.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔄 تلاش مجدد", callback_data="start_profile")
                        ]])
                    )
            else:
                # User cancelled
                await query.edit_message_text(
                    "❌ ساخت پروفایل لغو شد.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🏠 منوی اصلی", callback_data="go_home")
                    ]])
                )
            
            # Clear conversation data
            context.user_data.clear()
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"❌ Handle confirmation failed: {e}")
            await self._send_error_message(update, "مشکلی در تایید پروفایل پیش آمد.")
            return ConversationHandler.END
    
    @safe_async_handler
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle cancel command"""
        try:
            await update.message.reply_text(
                "❌ ساخت پروفایل لغو شد.",
                reply_markup=ReplyKeyboardRemove()
            )
            
            # Clear conversation data
            context.user_data.clear()
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"❌ Cancel command failed: {e}")
            return ConversationHandler.END
    
    @safe_async_handler
    async def cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle cancel callback"""
        try:
            query = update.callback_query
            await query.answer()
            
            await query.edit_message_text(
                "❌ ساخت پروفایل لغو شد.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 منوی اصلی", callback_data="go_home")
                ]])
            )
            
            # Clear conversation data
            context.user_data.clear()
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"❌ Cancel callback failed: {e}")
            return ConversationHandler.END
    
    def _validate_name(self, name: str) -> bool:
        """Validate name input"""
        if not name or len(name) < 2 or len(name) > 50:
            return False
        
        # Check for valid characters (Persian and English letters, spaces)
        import re
        if not re.match(r'^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z\s]+$', name):
            return False
        
        return True
    
    def _get_grade_text(self, grade: str) -> str:
        """Get grade text in Persian"""
        grade_map = {
            'highschool': 'دبیرستان',
            'pre_uni': 'پیش دانشگاهی',
            'university': 'دانشگاه'
        }
        return grade_map.get(grade, 'نامشخص')
    
    def _get_goal_text(self, goal: str) -> str:
        """Get goal text in Persian"""
        goal_map = {
            'math': 'کنکور ریاضی',
            'bio': 'کنکور تجربی',
            'humanities': 'کنکور انسانی',
            'art': 'کنکور هنر',
            'language': 'کنکور زبان'
        }
        return goal_map.get(goal, 'نامشخص')
    
    async def _save_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Save profile to database"""
        try:
            # Extract data
            name = profile_data.get('profile_name', '')
            grade = profile_data.get('profile_grade', '')
            goal = profile_data.get('profile_goal', '')
            
            # Split name into first and last name
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Insert or update user
            await db_manager.execute("""
                INSERT INTO users (id, first_name, last_name, grade_level, target_goal, joined_at)
                VALUES ($1, $2, $3, $4, $5, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    grade_level = EXCLUDED.grade_level,
                    target_goal = EXCLUDED.target_goal
            """, user_id, first_name, last_name, grade, goal)
            
            self.logger.info(f"✅ Profile saved for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save profile: {e}")
            return False
    
    async def _update_user_name(self, user_id: int, name: str) -> bool:
        """Update user name in database"""
        try:
            # Split name into first and last name
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Update user
            await db_manager.execute("""
                UPDATE users 
                SET first_name = $2, last_name = $3
                WHERE id = $1
            """, user_id, first_name, last_name)
            
            self.logger.info(f"✅ User name updated for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update user name: {e}")
            return False
    
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
profile_creation_handler = ProfileCreationHandler()
