"""
🌌 SarlakBot v3.2.0 - Error Handling System
Comprehensive error handling and recovery mechanisms
"""

import traceback
from collections.abc import Callable
from datetime import datetime
from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.services.user_profile_service import user_profile_service
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ErrorHandler:
    """
    🌌 Comprehensive Error Handler
    Handles all types of errors with proper logging and user feedback
    """

    def __init__(self):
        self.logger = logger
        self.error_counts = {}
        self.max_errors_per_user = 5
        self.error_reset_time = 3600  # 1 hour

    async def handle_error(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        error: Exception,
        user_friendly_message: str = "❌ خطا در پردازش درخواست. لطفاً دوباره تلاش کنید.",
    ) -> None:
        """
        Handle errors with proper logging and user feedback

        Args:
            update: Telegram update object
            context: Bot context
            error: Exception that occurred
            user_friendly_message: Message to show to user
        """
        try:
            user_id = update.effective_user.id if update.effective_user else 0

            # Log error details
            error_details = {
                "user_id": user_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": datetime.now().isoformat(),
                "update_type": (
                    update.callback_query.__class__.__name__ if update.callback_query else "Message"
                ),
            }

            self.logger.error(f"Error occurred: {error_details}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")

            # Check if user has exceeded error limit
            if await self._check_error_limit(user_id):
                await self._send_error_limit_message(update)
                return

            # Send user-friendly error message
            await self._send_error_message(update, user_friendly_message)

            # Clean up conversation state if needed
            await self._cleanup_on_error(update, context)

        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")

    def _check_error_limit(self, user_id: int) -> bool:
        """Check if user has exceeded error limit"""
        try:
            current_time = datetime.now().timestamp()

            # Clean old errors
            if user_id in self.error_counts:
                self.error_counts[user_id] = [
                    error_time
                    for error_time in self.error_counts[user_id]
                    if current_time - error_time < self.error_reset_time
                ]
            else:
                self.error_counts[user_id] = []

            # Add current error
            self.error_counts[user_id].append(current_time)

            # Check if limit exceeded
            return len(self.error_counts[user_id]) > self.max_errors_per_user

        except Exception as e:
            self.logger.error(f"Error checking error limit: {e}")
            return False

    async def _send_error_limit_message(self, update: Update) -> None:
        """Send error limit exceeded message"""
        try:
            text = """
🚫 **خطا در تعداد درخواست‌ها**

شما بیش از حد مجاز درخواست ارسال کرده‌اید. لطفاً یک ساعت صبر کنید و دوباره تلاش کنید.

**Error Limit Exceeded**

You have exceeded the maximum number of requests. Please wait one hour and try again.
"""

            keyboard = [
                [InlineKeyboardButton("🏠 منوی اصلی / Main Menu", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
                )

        except Exception as e:
            self.logger.error(f"Error sending error limit message: {e}")

    async def _send_error_message(self, update: Update, message: str) -> None:
        """Send error message to user"""
        try:
            keyboard = [
                [InlineKeyboardButton("🔄 تلاش مجدد / Retry", callback_data="retry")],
                [InlineKeyboardButton("🏠 منوی اصلی / Main Menu", callback_data="main_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if update.callback_query:
                await update.callback_query.edit_message_text(
                    message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
                )

        except Exception as e:
            self.logger.error(f"Error sending error message: {e}")

    async def _cleanup_on_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Clean up conversation state on error"""
        try:
            user_id = update.effective_user.id if update.effective_user else 0

            # Clean up onboarding state if in conversation
            if context.user_data.get("conversation_state"):
                await user_profile_service._cleanup_onboarding_state(user_id)
                context.user_data.clear()

        except Exception as e:
            self.logger.error(f"Error cleaning up on error: {e}")


def safe_handler(func: Callable) -> Callable:
    """
    Decorator for safe error handling in handlers

    Args:
        func: Handler function to wrap

    Returns:
        Wrapped function with error handling
    """

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            error_handler = ErrorHandler()
            await error_handler.handle_error(update, context, e)
            return None

    return wrapper


def safe_async_handler(func: Callable) -> Callable:
    """
    Decorator for safe error handling in async handlers

    Args:
        func: Async handler function to wrap

    Returns:
        Wrapped function with error handling
    """

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            error_handler = ErrorHandler()
            await error_handler.handle_error(update, context, e)
            return None

    return wrapper


# Global error handler instance
error_handler = ErrorHandler()
