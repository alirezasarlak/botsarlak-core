"""
🌌 SarlakBot v3.1.0 - Referral Handler
Professional referral system with gamification and token rewards
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

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
from src.services.referral_service import referral_service
from src.services.token_service import token_service
from src.services.gamification_service import gamification_service
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Conversation states
(REFERRAL_MAIN, REFERRAL_CODE_INPUT, REFERRAL_CUSTOM_CODE) = range(3)


class ReferralHandler:
    """
    🌌 Referral Handler
    Professional referral system with gamification
    """
    
    def __init__(self):
        self.logger = logger
    
    async def register(self, application: Application) -> None:
        """Register referral handlers"""
        try:
            self.logger.info("🎯 Registering referral handlers...")
            
            # Referral command handler
            application.add_handler(CommandHandler("referral", self.referral_command))
            application.add_handler(CommandHandler("invite", self.referral_command))
            application.add_handler(CommandHandler("دعوت", self.referral_command))
            
            # Referral conversation handler
            referral_conv_handler = ConversationHandler(
                entry_points=[
                    CallbackQueryHandler(self.referral_callback, pattern="^referral_")
                ],
                states={
                    REFERRAL_MAIN: [CallbackQueryHandler(self.referral_callback, pattern="^referral_")],
                    REFERRAL_CODE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_referral_code_input)],
                    REFERRAL_CUSTOM_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_custom_code_input)]
                },
                fallbacks=[CallbackQueryHandler(self.referral_callback, pattern="^referral_main$")],
                per_message=True,
                per_chat=True,
                per_user=True
            )
            
            application.add_handler(referral_conv_handler)
            
            self.logger.info("✅ Referral handlers registered successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Referral handler registration failed: {e}")
            raise
    
    async def referral_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /referral command"""
        try:
            user_id = update.effective_user.id
            
            # Get user referral stats
            stats = await referral_service.get_user_referral_stats(user_id)
            
            # Create referral code if doesn't exist
            if not stats.get("referral_code"):
                referral_code = await referral_service.create_referral_code(user_id)
                stats["referral_code"] = referral_code
            
            # Create referral message
            message = await self._create_referral_message(user_id, stats)
            
            await update.message.reply_text(
                message["text"],
                reply_markup=message["keyboard"],
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Referral command failed: {e}")
            await update.message.reply_text("❌ خطا در نمایش سیستم دعوت")
    
    async def referral_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle referral callbacks"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            callback_data = query.data
            
            if callback_data == "referral_main":
                return await self._show_referral_main(query, user_id)
            elif callback_data == "referral_my_code":
                return await self._show_my_referral_code(query, user_id)
            elif callback_data == "referral_use_code":
                return await self._show_use_referral_code(query, user_id)
            elif callback_data == "referral_stats":
                return await self._show_referral_stats(query, user_id)
            elif callback_data == "referral_leaderboard":
                return await self._show_referral_leaderboard(query, user_id)
            elif callback_data == "referral_custom_code":
                return await self._show_custom_code_input(query, user_id)
            elif callback_data == "referral_tokens":
                return await self._show_token_balance(query, user_id)
            elif callback_data == "referral_lottery":
                return await self._show_lottery_info(query, user_id)
            
            return REFERRAL_MAIN
            
        except Exception as e:
            self.logger.error(f"❌ Referral callback failed: {e}")
            return ConversationHandler.END
    
    async def _show_referral_main(self, query, user_id: int) -> int:
        """Show main referral menu"""
        try:
            # Get user stats
            stats = await referral_service.get_user_referral_stats(user_id)
            
            # Create main menu text
            text = f"""
🎯 **سیستم دعوت دوستان** 🚀

**آمار شما:**
👥 دعوت‌های موفق: {stats.get('completed_referrals', 0)}
🏆 امتیاز کسب شده: {stats.get('total_points', 0):,}
🪙 توکن‌های شما: {stats.get('total_tokens', 0):,}

**چطور کار می‌کنه؟**
1️⃣ کد دعوت خودت رو دریافت کن
2️⃣ با دوستانت به اشتراک بذار
3️⃣ برای هر دعوت موفق امتیاز و توکن بگیر
4️⃣ توکن‌هات رو در قرعه‌کشی‌ها خرج کن

**آماده‌ای برای شروع؟** ✨
"""
            
            keyboard = [
                [InlineKeyboardButton("🎫 کد دعوت من", callback_data="referral_my_code")],
                [InlineKeyboardButton("📊 آمار کامل", callback_data="referral_stats")],
                [InlineKeyboardButton("🏆 جدول رتبه‌بندی", callback_data="referral_leaderboard")],
                [InlineKeyboardButton("🪙 موجودی توکن‌ها", callback_data="referral_tokens")],
                [InlineKeyboardButton("🎲 قرعه‌کشی‌ها", callback_data="referral_lottery")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_main")]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return REFERRAL_MAIN
            
        except Exception as e:
            self.logger.error(f"❌ Show referral main failed: {e}")
            return ConversationHandler.END
    
    async def _show_my_referral_code(self, query, user_id: int) -> int:
        """Show user's referral code"""
        try:
            # Get or create referral code
            referral_code = await referral_service.get_user_referral_code(user_id)
            if not referral_code:
                referral_code = await referral_service.create_referral_code(user_id)
            
            # Create referral link
            referral_link = f"https://t.me/{context.bot.username}?start=ref_{referral_code}"
            
            text = f"""
🎫 **کد دعوت شما** 🎯

**کد دعوت:** `{referral_code}`

**لینک دعوت:**
`{referral_link}`

**نحوه استفاده:**
1️⃣ لینک بالا رو کپی کن
2️⃣ برای دوستانت ارسال کن
3️⃣ وقتی دوستت با این لینک عضو شد، امتیاز و توکن می‌گیری

**پاداش‌ها:**
🎁 هر دعوت موفق: 100 امتیاز + 10 توکن
🏆 دعوت‌های بیشتر = پاداش‌های بهتر
"""
            
            keyboard = [
                [InlineKeyboardButton("📋 کپی لینک", url=f"https://t.me/share/url?url={referral_link}&text=به%20آکادمی%20سرلک%20بپیوندید!")],
                [InlineKeyboardButton("✏️ کد سفارشی", callback_data="referral_custom_code")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="referral_main")]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return REFERRAL_MAIN
            
        except Exception as e:
            self.logger.error(f"❌ Show my referral code failed: {e}")
            return ConversationHandler.END
    
    async def _show_use_referral_code(self, query, user_id: int) -> int:
        """Show use referral code interface"""
        try:
            text = """
🎫 **استفاده از کد دعوت** 🎯

لطفاً کد دعوت دوستت رو وارد کن:

**نحوه پیدا کردن کد:**
• از دوستت بپرس
• از پیام‌های دعوت استفاده کن
• کد معمولاً 8 کاراکتره (مثل: ABC12345)
"""
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت", callback_data="referral_main")]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return REFERRAL_CODE_INPUT
            
        except Exception as e:
            self.logger.error(f"❌ Show use referral code failed: {e}")
            return ConversationHandler.END
    
    async def handle_referral_code_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle referral code input"""
        try:
            user_id = update.effective_user.id
            referral_code = update.message.text.strip().upper()
            
            # Validate referral code
            referrer_id = await referral_service.validate_referral_code(referral_code)
            
            if not referrer_id:
                await update.message.reply_text(
                    "❌ کد دعوت نامعتبر است!\n\nلطفاً کد صحیح را وارد کنید:",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 بازگشت", callback_data="referral_main")
                    ]])
                )
                return REFERRAL_CODE_INPUT
            
            # Check if user is trying to use their own code
            if referrer_id == user_id:
                await update.message.reply_text(
                    "❌ نمی‌تونی از کد دعوت خودت استفاده کنی!\n\nلطفاً کد دوستت رو وارد کن:",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 بازگشت", callback_data="referral_main")
                    ]])
                )
                return REFERRAL_CODE_INPUT
            
            # Process referral
            success = await referral_service.process_referral(referrer_id, user_id, referral_code)
            
            if success:
                # Update gamification
                await gamification_service.update_quest_progress(user_id, "referral", 1)
                await gamification_service.update_streak(user_id, "referral")
                
                await update.message.reply_text(
                    "🎉 **کد دعوت با موفقیت اعمال شد!**\n\n"
                    "حالا می‌تونی از تمام امکانات ربات استفاده کنی و امتیاز و توکن کسب کنی!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🎯 سیستم دعوت", callback_data="referral_main"),
                        InlineKeyboardButton("🏠 خانه", callback_data="menu_main")
                    ]])
                )
            else:
                await update.message.reply_text(
                    "❌ خطا در اعمال کد دعوت!\n\nلطفاً دوباره تلاش کنید:",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 بازگشت", callback_data="referral_main")
                    ]])
                )
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"❌ Handle referral code input failed: {e}")
            return ConversationHandler.END
    
    async def _show_referral_stats(self, query, user_id: int) -> int:
        """Show detailed referral statistics"""
        try:
            # Get user stats
            stats = await referral_service.get_user_referral_stats(user_id)
            
            # Get token balance
            token_balance = await token_service.get_user_tokens(user_id)
            
            # Get recent referrals
            recent_referrals = stats.get("recent_referrals", [])
            
            text = f"""
📊 **آمار کامل دعوت‌ها** 🎯

**آمار کلی:**
👥 کل دعوت‌ها: {stats.get('total_referrals', 0)}
✅ دعوت‌های موفق: {stats.get('completed_referrals', 0)}
🏆 امتیاز کسب شده: {stats.get('total_points', 0):,}
🪙 توکن‌های شما: {token_balance.get('available_tokens', 0):,}

**دعوت‌های اخیر:**
"""
            
            if recent_referrals:
                for i, referral in enumerate(recent_referrals[:5], 1):
                    status_emoji = "✅" if referral["referral_status"] == "completed" else "⏳"
                    text += f"{i}. {status_emoji} @{referral['username']} - {referral['referred_at']}\n"
            else:
                text += "هنوز دعوتی نداشته‌اید\n"
            
            text += f"""
**مرحله بعدی:**
🎁 {self._get_next_milestone(stats.get('completed_referrals', 0))}
"""
            
            keyboard = [
                [InlineKeyboardButton("🔄 بروزرسانی", callback_data="referral_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="referral_main")]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return REFERRAL_MAIN
            
        except Exception as e:
            self.logger.error(f"❌ Show referral stats failed: {e}")
            return ConversationHandler.END
    
    async def _show_referral_leaderboard(self, query, user_id: int) -> int:
        """Show referral leaderboard"""
        try:
            # Get leaderboard
            leaderboard = await referral_service.get_referral_leaderboard(10)
            
            text = "🏆 **جدول رتبه‌بندی دعوت‌ها** 🎯\n\n"
            
            if leaderboard:
                for i, user in enumerate(leaderboard, 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    text += f"{medal} **{user['first_name']}** (@{user['username']})\n"
                    text += f"   👥 {user['referral_count']} دعوت | 🪙 {user['total_tokens']} توکن\n\n"
            else:
                text += "هنوز کسی دعوتی نداشته است\n"
            
            # Get user's position
            user_position = await self._get_user_leaderboard_position(user_id, leaderboard)
            if user_position:
                text += f"**رتبه شما:** {user_position}\n"
            
            keyboard = [
                [InlineKeyboardButton("🔄 بروزرسانی", callback_data="referral_leaderboard")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="referral_main")]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return REFERRAL_MAIN
            
        except Exception as e:
            self.logger.error(f"❌ Show referral leaderboard failed: {e}")
            return ConversationHandler.END
    
    async def _show_token_balance(self, query, user_id: int) -> int:
        """Show user token balance"""
        try:
            # Get token balance
            token_balance = await token_service.get_user_tokens(user_id)
            
            # Get recent transactions
            transactions = await token_service.get_token_transactions(user_id, 5)
            
            text = f"""
🪙 **موجودی توکن‌های شما** 💰

**موجودی:**
🪙 کل توکن‌ها: {token_balance.get('total_tokens', 0):,}
✅ قابل استفاده: {token_balance.get('available_tokens', 0):,}
💸 خرج شده: {token_balance.get('spent_tokens', 0):,}
🔒 قفل شده: {token_balance.get('locked_tokens', 0):,}

**تراکنش‌های اخیر:**
"""
            
            if transactions:
                for transaction in transactions:
                    emoji = "➕" if transaction["transaction_type"] == "earn" else "➖"
                    text += f"{emoji} {transaction['amount']} توکن - {transaction['source']}\n"
            else:
                text += "هنوز تراکنشی نداشته‌اید\n"
            
            text += f"""
**چطور توکن کسب کنم؟**
🎯 دعوت دوستان
📚 مطالعه روزانه
🏆 تکمیل مأموریت‌ها
🎲 شرکت در قرعه‌کشی‌ها
"""
            
            keyboard = [
                [InlineKeyboardButton("🎲 قرعه‌کشی‌ها", callback_data="referral_lottery")],
                [InlineKeyboardButton("📊 آمار کامل", callback_data="referral_stats")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="referral_main")]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return REFERRAL_MAIN
            
        except Exception as e:
            self.logger.error(f"❌ Show token balance failed: {e}")
            return ConversationHandler.END
    
    async def _show_lottery_info(self, query, user_id: int) -> int:
        """Show lottery information"""
        try:
            # Get active lotteries
            lotteries = await token_service.get_active_lotteries()
            
            text = "🎲 **قرعه‌کشی‌های فعال** 🎰\n\n"
            
            if lotteries:
                for lottery in lotteries:
                    text += f"**{lottery['lottery_name']}**\n"
                    text += f"💰 جایزه: {lottery['prize_pool']} {lottery['prize_currency']}\n"
                    text += f"🪙 هزینه هر ورودی: {lottery['token_cost_per_entry']} توکن\n"
                    text += f"📅 پایان: {lottery['ends_at']}\n\n"
            else:
                text += "در حال حاضر قرعه‌کشی فعالی وجود ندارد\n"
            
            text += "**نحوه شرکت:**\n"
            text += "1️⃣ توکن‌های کافی داشته باش\n"
            text += "2️⃣ در قرعه‌کشی شرکت کن\n"
            text += "3️⃣ منتظر قرعه‌کشی بمان\n"
            text += "4️⃣ اگر برنده شدی، جایزه‌ت رو دریافت کن\n"
            
            keyboard = [
                [InlineKeyboardButton("🪙 موجودی توکن‌ها", callback_data="referral_tokens")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="referral_main")]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return REFERRAL_MAIN
            
        except Exception as e:
            self.logger.error(f"❌ Show lottery info failed: {e}")
            return ConversationHandler.END
    
    async def _show_custom_code_input(self, query, user_id: int) -> int:
        """Show custom code input interface"""
        try:
            text = """
✏️ **کد دعوت سفارشی** 🎫

کد دعوت سفارشی خودت رو وارد کن:

**قوانین:**
• فقط حروف انگلیسی و اعداد
• حداقل 4 کاراکتر
• حداکثر 20 کاراکتر
• باید منحصر به فرد باشه
"""
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت", callback_data="referral_my_code")]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return REFERRAL_CUSTOM_CODE
            
        except Exception as e:
            self.logger.error(f"❌ Show custom code input failed: {e}")
            return ConversationHandler.END
    
    async def handle_custom_code_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle custom code input"""
        try:
            user_id = update.effective_user.id
            custom_code = update.message.text.strip().upper()
            
            # Validate custom code
            if len(custom_code) < 4 or len(custom_code) > 20:
                await update.message.reply_text(
                    "❌ کد باید بین 4 تا 20 کاراکتر باشد!\n\nلطفاً کد جدید وارد کنید:",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 بازگشت", callback_data="referral_my_code")
                    ]])
                )
                return REFERRAL_CUSTOM_CODE
            
            # Check if code is valid (only letters and numbers)
            if not custom_code.isalnum():
                await update.message.reply_text(
                    "❌ کد فقط باید حروف انگلیسی و اعداد باشد!\n\nلطفاً کد جدید وارد کنید:",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 بازگشت", callback_data="referral_my_code")
                    ]])
                )
                return REFERRAL_CUSTOM_CODE
            
            # Create custom referral code
            try:
                referral_code = await referral_service.create_referral_code(user_id, custom_code)
                
                await update.message.reply_text(
                    f"✅ **کد دعوت سفارشی ایجاد شد!**\n\n"
                    f"**کد شما:** `{referral_code}`\n\n"
                    f"حالا می‌تونی این کد رو با دوستانت به اشتراک بذاری!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🎫 کد دعوت من", callback_data="referral_my_code"),
                        InlineKeyboardButton("🔙 بازگشت", callback_data="referral_main")
                    ]])
                )
            except Exception as e:
                await update.message.reply_text(
                    "❌ این کد قبلاً استفاده شده است!\n\nلطفاً کد دیگری انتخاب کنید:",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 بازگشت", callback_data="referral_my_code")
                    ]])
                )
                return REFERRAL_CUSTOM_CODE
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"❌ Handle custom code input failed: {e}")
            return ConversationHandler.END
    
    async def _create_referral_message(self, user_id: int, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Create referral message"""
        try:
            referral_code = stats.get("referral_code", "در حال ایجاد...")
            referral_link = f"https://t.me/{config.bot.username}?start=ref_{referral_code}"
            
            text = f"""
🎯 **سیستم دعوت دوستان** 🚀

**کد دعوت شما:** `{referral_code}`

**لینک دعوت:**
`{referral_link}`

**آمار شما:**
👥 دعوت‌های موفق: {stats.get('completed_referrals', 0)}
🏆 امتیاز کسب شده: {stats.get('total_points', 0):,}
🪙 توکن‌های شما: {stats.get('total_tokens', 0):,}

**چطور کار می‌کنه؟**
1️⃣ لینک بالا رو کپی کن
2️⃣ برای دوستانت ارسال کن
3️⃣ برای هر دعوت موفق امتیاز و توکن بگیر
4️⃣ توکن‌هات رو در قرعه‌کشی‌ها خرج کن
"""
            
            keyboard = [
                [InlineKeyboardButton("📋 کپی لینک", url=f"https://t.me/share/url?url={referral_link}&text=به%20آکادمی%20سرلک%20بپیوندید!")],
                [InlineKeyboardButton("📊 آمار کامل", callback_data="referral_stats")],
                [InlineKeyboardButton("🏆 جدول رتبه‌بندی", callback_data="referral_leaderboard")],
                [InlineKeyboardButton("🪙 موجودی توکن‌ها", callback_data="referral_tokens")],
                [InlineKeyboardButton("🎲 قرعه‌کشی‌ها", callback_data="referral_lottery")]
            ]
            
            return {
                "text": text,
                "keyboard": InlineKeyboardMarkup(keyboard)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Create referral message failed: {e}")
            return {
                "text": "❌ خطا در ایجاد پیام دعوت",
                "keyboard": InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="menu_main")
                ]])
            }
    
    def _get_next_milestone(self, current_referrals: int) -> str:
        """Get next milestone message"""
        milestones = [1, 5, 10, 25, 50, 100]
        
        for milestone in milestones:
            if current_referrals < milestone:
                remaining = milestone - current_referrals
                return f"🎯 {remaining} دعوت دیگر تا {milestone} دعوت"
        
        return "🏆 شما به بالاترین مرحله رسیده‌اید!"
    
    async def _get_user_leaderboard_position(self, user_id: int, leaderboard: List[Dict[str, Any]]) -> Optional[int]:
        """Get user's position in leaderboard"""
        for i, user in enumerate(leaderboard, 1):
            if user["user_id"] == user_id:
                return i
        return None


# Global referral handler instance
referral_handler = ReferralHandler()
