"""
🌌 SarlakBot v3.0 - Start Command Handler (Clean Version)
Gen-Z cosmic journey start experience - No onboarding conflicts
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from src.config import config
from src.utils.logging import get_logger
from src.database.connection import db_manager
# UserQueries import removed - using direct database queries

logger = get_logger(__name__)

class StartHandler:
    """
    🌌 Start Command Handler (Clean Version)
    Handles the /start command with cosmic welcome experience
    No onboarding conflicts - delegates to OnboardingHandler
    """
    
    def __init__(self):
        self.logger = logger
    
    async def register(self, application: Application) -> None:
        """Register start command handler"""
        try:
            self.logger.info("🚀 Registering start command handler...")
            
            # Register command handler
            application.add_handler(CommandHandler("start", self.start_command))
            
            # Register only essential callback handlers (no onboarding conflicts)
            application.add_handler(CallbackQueryHandler(self.start_onboarding_callback, pattern="^start_onboarding$"))
            application.add_handler(CallbackQueryHandler(self.check_membership_callback, pattern="^check_membership$"))
            application.add_handler(CallbackQueryHandler(self.skip_onboarding_callback, pattern="^skip_onboarding$"))
            application.add_handler(CallbackQueryHandler(self.go_home_callback, pattern="^go_home$"))
            
            self.logger.info("✅ Start command handler registered successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Start command handler registration failed: {e}")
            raise
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            self.logger.info(f"🚀 User {user_id} started the bot")
            
            # Check for referral code
            referral_code = None
            if context.args and context.args[0].startswith('ref_'):
                referral_code = context.args[0][4:]  # Remove 'ref_' prefix
                self.logger.info(f"Referral code detected: {referral_code}")
            
            # Upsert user data
            await self._upsert_user_data(user)
            
            # Process referral if code provided
            if referral_code:
                await self._process_referral(user_id, referral_code)
            
            # Check if user completed onboarding
            await db_manager.initialize()
            user_data = await db_manager.fetch_one("SELECT * FROM users WHERE id = $1", user_id)
            if user_data and user_data.get('onboarding_completed'):
                await self._send_user_welcome(update, user_data, is_returning=True)
            else:
                await self._send_user_welcome(update, user_data, is_returning=False)
            
        except Exception as e:
            self.logger.error(f"❌ Start command failed: {e}")
            await update.message.reply_text("❌ خطا در شروع ربات")
    
    async def _upsert_user_data(self, user) -> None:
        """Upsert user data to database"""
        try:
            await db_manager.initialize()
            
            user_data = {
                'id': user.id,
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'username': user.username or '',
                'language_code': user.language_code or 'fa',
                'is_bot': getattr(user, 'is_bot', False),
                'last_seen_at': 'NOW()'
            }
            
            # Use direct database query instead of UserQueries class
            await db_manager.execute("""
                INSERT INTO users (id, first_name, last_name, username, language_code, is_bot, last_seen_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
                ON CONFLICT (id) 
                DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    username = EXCLUDED.username,
                    language_code = EXCLUDED.language_code,
                    is_bot = EXCLUDED.is_bot,
                    last_seen_at = NOW()
            """, user_data['id'], user_data['first_name'], user_data['last_name'], 
                user_data['username'], user_data['language_code'], user_data['is_bot'])
            
        except Exception as e:
            self.logger.error(f"❌ Failed to upsert user data: {e}")
    
    async def _send_user_welcome(self, update, user_data, is_returning=False) -> None:
        """Send welcome message to user"""
        try:
            if is_returning:
                await self._show_welcome_back_message(update, user_data)
            else:
                await self._show_new_user_welcome(update)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to send welcome message: {e}")
    
    async def _show_welcome_back_message(self, update, user_data) -> None:
        """Show welcome back message for returning users"""
        try:
            first_name = user_data.get('first_name', 'عزیز')
            
            welcome_text = f"""
🌟 **خوش برگشتی {first_name}!** ✨

آماده‌ای برای ادامه سفر کیهانی‌ات؟ 🚀

**منوی جدید فعال شد!** 🎯
"""
            
            keyboard = [
                [InlineKeyboardButton("🎯 دعوت دوستان", callback_data="referral_main")],
                [InlineKeyboardButton("🚀 شروع سفر", callback_data="start_onboarding")],
                [InlineKeyboardButton("🏠 خانه", callback_data="go_home")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to show welcome back message: {e}")
    
    async def _show_new_user_welcome(self, update) -> None:
        """Show welcome message for new users"""
        try:
            welcome_text = """
🌟 **خوش اومدی به آکادمی سرلک!** ✨

من ربات هوشمند آکادمی سرلک هستم و اینجا هستم تا تو رو در سفر کیهانی کنکور همراهی کنم! 🚀

**چیکار می‌تونم برات بکنم:**
• 📚 **مطالعه هوشمند** - برنامه‌ریزی شخصی‌سازی شده
• 🎯 **آزمون‌های آنلاین** - تست‌های استاندارد کنکور
• 📊 **تحلیل پیشرفت** - گزارش‌های دقیق عملکرد
• 🏆 **رقابت و انگیزه** - چالش‌های جذاب
• 💬 **پشتیبانی ۲۴/۷** - پاسخ به سوالاتت

**آماده‌ای برای شروع این سفر هیجان‌انگیز؟** 🌟
"""
            
            keyboard = [
                [InlineKeyboardButton("🎯 دعوت دوستان", callback_data="referral_main")],
                [InlineKeyboardButton("🚀 شروع سفر", callback_data="start_onboarding")],
                [InlineKeyboardButton("📣 عضویت در کانال", url=config.bot.telegram_channel_url)],
                [InlineKeyboardButton("🏠 خانه", callback_data="go_home")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to show new user welcome: {e}")
    
    async def _process_referral(self, user_id: int, referral_code: str) -> None:
        """Process referral code"""
        try:
            from src.services.referral_service import referral_service
            from src.services.gamification_service import gamification_service
            
            # Validate referral code
            referrer_id = await referral_service.validate_referral_code(referral_code)
            
            if not referrer_id:
                self.logger.warning(f"Invalid referral code: {referral_code}")
                return
            
            # Check if user is trying to use their own code
            if referrer_id == user_id:
                self.logger.warning(f"User {user_id} tried to use their own referral code")
                return
            
            # Process referral
            success = await referral_service.process_referral(referrer_id, user_id, referral_code)
            
            if success:
                # Update gamification
                await gamification_service.update_quest_progress(user_id, "referral", 1)
                await gamification_service.update_streak(user_id, "referral")
                
                self.logger.info(f"Referral processed successfully: {referrer_id} -> {user_id}")
            else:
                self.logger.warning(f"Failed to process referral: {referrer_id} -> {user_id}")
                
        except Exception as e:
            self.logger.error(f"❌ Process referral failed: {e}")
    
    async def start_onboarding_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle start onboarding callback - delegate to onboarding handler"""
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            user_id = user.id
            
            # Log onboarding start
            self.logger.info(f"🚀 User {user_id} started onboarding")
            
            # Show onboarding welcome message and let ConversationHandler handle the flow
            welcome_text = """
🌟 **خوش اومدی به آکادمی سرلک!** ✨

حالا وقتشه که خودت رو معرفی کنی و سفر کیهانی‌ات رو شروع کنی! 🚀

**مراحل ثبت‌نام:**
1️⃣ **عضویت در کانال** - برای دریافت آخرین اخبار
2️⃣ **معرفی خودت** - اسم و نام مستعار
3️⃣ **انتخاب رشته** - تجربی، ریاضی، انسانی یا زبان
4️⃣ **تنظیم پروفایل** - پایه تحصیلی و اطلاعات تکمیلی

**آماده‌ای برای شروع این سفر هیجان‌انگیز؟** 🌟
"""
            
            keyboard = [
                [
                    InlineKeyboardButton("📣 عضویت در کانال", url=config.bot.telegram_channel_url),
                    InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")
                ],
                [
                    InlineKeyboardButton("🚀 شروع ثبت‌نام", callback_data="start_registration")
                ],
                [
                    InlineKeyboardButton("🏠 خانه", callback_data="go_home")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Start onboarding callback failed: {e}")
            await query.answer("❌ خطا در شروع فرآیند ثبت‌نام")
    
    async def check_membership_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle check membership callback"""
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            user_id = user.id
            
            # Log membership check
            self.logger.info(f"🔍 User {user_id} checking membership")
            
            # Check membership status
            await self._check_membership_status(query, user_id)
            
        except Exception as e:
            self.logger.error(f"❌ Check membership callback failed: {e}")
            await query.answer("❌ خطا در بررسی عضویت")
    
    async def _check_membership_status(self, query, user_id) -> None:
        """Check user's membership status"""
        try:
            # This is a placeholder - implement actual membership check
            membership_text = """
✅ **وضعیت عضویت شما:**

شما در کانال آکادمی سرلک عضو هستید! 🎉

حالا می‌تونید از تمام امکانات ربات استفاده کنید.
"""
            
            keyboard = [
                [InlineKeyboardButton("🚀 ادامه", callback_data="start_onboarding")],
                [InlineKeyboardButton("🏠 خانه", callback_data="go_home")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                membership_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to check membership status: {e}")
    
    async def skip_onboarding_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle skip onboarding callback"""
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            user_id = user.id
            
            # Log skip onboarding
            self.logger.info(f"⏭️ User {user_id} skipped onboarding")
            
            # Mark onboarding as completed with minimal data
            await self._skip_onboarding_completion(user_id)
            
            # Show main menu
            await self._show_main_menu(query)
            
        except Exception as e:
            self.logger.error(f"❌ Skip onboarding callback failed: {e}")
            await query.answer("❌ خطا در رد کردن ثبت‌نام")
    
    async def _skip_onboarding_completion(self, user_id) -> None:
        """Complete onboarding with minimal data"""
        try:
            await db_manager.initialize()
            
            # Update user with minimal data
            user_data = {
                'id': user_id,
                'first_name': 'کاربر',
                'nickname': f'user_{user_id}',
                'onboarding_completed': True
            }
            
            # Use direct database query instead of UserQueries class
            await db_manager.execute("""
                UPDATE users 
                SET first_name = $2, nickname = $3, onboarding_completed = $4
                WHERE id = $1
            """, user_data['id'], user_data['first_name'], user_data['nickname'], user_data['onboarding_completed'])
            
        except Exception as e:
            self.logger.error(f"❌ Failed to skip onboarding completion: {e}")
    
    async def go_home_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle go home callback"""
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            user_id = user.id
            
            # Log go home
            self.logger.info(f"🏠 User {user_id} went to home")
            
            # Show main menu
            await self._show_main_menu(query)
            
        except Exception as e:
            self.logger.error(f"❌ Go home callback failed: {e}")
            await query.answer("❌ خطا در بازگشت به خانه")
    
    async def _show_main_menu(self, query) -> None:
        """Show main menu"""
        try:
            # Delegate to main menu handler
            from src.handlers.main_menu.handler import MainMenuHandler
            main_menu_handler = MainMenuHandler()
            await main_menu_handler.show_main_menu(query)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to show main menu: {e}")
            await query.edit_message_text("❌ خطا در نمایش منو")
