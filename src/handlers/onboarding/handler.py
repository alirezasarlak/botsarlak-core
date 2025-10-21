"""
🌌 SarlakBot v3.0 - Onboarding Handler
Complete onboarding flow with conversation handler
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    ConversationHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters,
    ContextTypes
)
from src.config import config
from src.utils.logging import get_logger
from src.handlers.onboarding.state import OnboardingState
from src.handlers.onboarding.texts_fa import ONBOARDING_TEXTS

logger = get_logger(__name__)

class OnboardingHandler:
    """
    🌌 Onboarding Handler
    Handles the complete onboarding flow
    """
    
    def __init__(self):
        self.logger = logger
    
    async def register(self, application: Application) -> None:
        """Register onboarding handlers"""
        try:
            self.logger.info("🚀 Registering onboarding handlers...")
            
            # Create conversation handler
            conv_handler = ConversationHandler(
                entry_points=[
                    CallbackQueryHandler(self.start_registration_callback, pattern="^start_registration$")
                ],
                per_message=True,
                states={
                    OnboardingState.COLLECTING_NAME: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_real_name)
                    ],
                    OnboardingState.COLLECTING_NICKNAME: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_nickname)
                    ],
                    OnboardingState.SELECTING_TRACK: [
                        CallbackQueryHandler(self.handle_study_track, pattern="^track_")
                    ],
                    OnboardingState.SELECTING_GRADE_BAND: [
                        CallbackQueryHandler(self.handle_grade_band, pattern="^grade_band_")
                    ],
                    OnboardingState.SELECTING_GRADE_YEAR: [
                        CallbackQueryHandler(self.handle_grade_year, pattern="^grade_year_")
                    ],
                    OnboardingState.COLLECTING_PHONE: [
                        CallbackQueryHandler(self.handle_phone_choice, pattern="^phone_"),
                        MessageHandler(filters.CONTACT, self.handle_phone_contact)
                    ],
                },
                fallbacks=[
                    CallbackQueryHandler(self.cancel_onboarding, pattern="^cancel_onboarding$")
                ],
                per_chat=True,
                per_user=True
            )
            
            application.add_handler(conv_handler)
            
            self.logger.info("✅ Onboarding handlers registered successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Onboarding handler registration failed: {e}")
            raise
    
    async def start_registration_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the registration process"""
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            user_id = user.id
            
            self.logger.info(f"User {user_id} starting registration")
            
            # Check membership first
            try:
                chat_member = await context.bot.get_chat_member(
                    chat_id="@sarlak_academy",
                    user_id=user_id
                )
                
                if chat_member.status not in ['member', 'administrator', 'creator']:
                    await query.edit_message_text(
                        "❌ **ابتدا باید عضو کانال شوید!** 😔\n\n"
                        "لطفاً ابتدا عضو کانال @sarlak_academy شوید و سپس دوباره تلاش کنید.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("📣 عضویت در کانال", url=config.bot.telegram_channel_url),
                            InlineKeyboardButton("🔄 بررسی مجدد", callback_data="start_registration")
                        ]]),
                        parse_mode='Markdown'
                    )
                    return ConversationHandler.END
                    
            except Exception as e:
                self.logger.error(f"Error checking membership: {e}")
                await query.edit_message_text(
                    "❌ **خطا در بررسی عضویت!** 😔\n\n"
                    "لطفاً دوباره تلاش کنید.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔄 تلاش مجدد", callback_data="start_registration")
                    ]]),
                    parse_mode='Markdown'
                )
                return ConversationHandler.END
            
            # Start registration
            await query.edit_message_text(
                ONBOARDING_TEXTS["ask_real_name"],
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ لغو", callback_data="cancel_onboarding")
                ]]),
                parse_mode='Markdown'
            )
            
            return OnboardingState.COLLECTING_NAME
            
        except Exception as e:
            self.logger.error(f"❌ Start registration callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در شروع ثبت‌نام. لطفاً دوباره تلاش کنید.")
            return ConversationHandler.END
    
    async def handle_real_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle real name input"""
        try:
            user = update.effective_user
            user_id = user.id
            real_name = update.message.text.strip()
            
            self.logger.info(f"User {user_id} entered real name: {real_name}")
            
            # Store real name in context
            context.user_data['real_name'] = real_name
            
            # Ask for nickname
            await update.message.reply_text(
                ONBOARDING_TEXTS["ask_nickname"],
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ لغو", callback_data="cancel_onboarding")
                ]]),
                parse_mode='Markdown'
            )
            
            return OnboardingState.COLLECTING_NICKNAME
            
        except Exception as e:
            self.logger.error(f"❌ Handle real name failed: {e}")
            await update.message.reply_text("❌ خطا در پردازش نام. لطفاً دوباره تلاش کنید.")
            return ConversationHandler.END
    
    async def handle_nickname(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle nickname input"""
        try:
            user = update.effective_user
            user_id = user.id
            nickname = update.message.text.strip()
            
            self.logger.info(f"User {user_id} entered nickname: {nickname}")
            
            # Validate nickname
            if len(nickname) < 2 or len(nickname) > 20:
                await update.message.reply_text(
                    ONBOARDING_TEXTS["nickname_invalid_error"],
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("❌ لغو", callback_data="cancel_onboarding")
                    ]]),
                    parse_mode='Markdown'
                )
                return OnboardingState.COLLECTING_NICKNAME
            
            # Store nickname in context
            context.user_data['nickname'] = nickname
            
            # Ask for study track
            keyboard = []
            for track, text in ONBOARDING_TEXTS["study_track_buttons"].items():
                keyboard.append([InlineKeyboardButton(text, callback_data=f"track_{track}")])
            keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="cancel_onboarding")])
            
            await update.message.reply_text(
                ONBOARDING_TEXTS["ask_study_track"],
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return OnboardingState.SELECTING_TRACK
            
        except Exception as e:
            self.logger.error(f"❌ Handle nickname failed: {e}")
            await update.message.reply_text("❌ خطا در پردازش نام مستعار. لطفاً دوباره تلاش کنید.")
            return ConversationHandler.END
    
    async def handle_study_track(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle study track selection"""
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            user_id = user.id
            track = query.data.replace("track_", "")
            
            self.logger.info(f"User {user_id} selected track: {track}")
            
            # Store study track in context
            context.user_data['study_track'] = track
            
            # Ask for grade band
            keyboard = []
            for band, text in ONBOARDING_TEXTS["grade_band_buttons"].items():
                keyboard.append([InlineKeyboardButton(text, callback_data=f"grade_band_{band}")])
            keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="cancel_onboarding")])
            
            await query.edit_message_text(
                ONBOARDING_TEXTS["ask_grade_band"],
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return OnboardingState.SELECTING_GRADE_BAND
            
        except Exception as e:
            self.logger.error(f"❌ Handle study track failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در انتخاب رشته. لطفاً دوباره تلاش کنید.")
            return ConversationHandler.END
    
    async def handle_grade_band(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle grade band selection"""
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            user_id = user.id
            grade_band = query.data.replace("grade_band_", "")
            
            self.logger.info(f"User {user_id} selected grade band: {grade_band}")
            
            # Store grade band in context
            context.user_data['grade_band'] = grade_band
            
            # Ask for grade year based on band
            if grade_band == "متوسطه اول":
                text = ONBOARDING_TEXTS["ask_grade_year_motevasete_aval"]
                buttons = ONBOARDING_TEXTS["grade_year_buttons_motevasete_aval"]
            else:
                text = ONBOARDING_TEXTS["ask_grade_year_motevasete_dovom"]
                buttons = ONBOARDING_TEXTS["grade_year_buttons_motevasete_dovom"]
            
            keyboard = []
            for year, year_text in buttons.items():
                keyboard.append([InlineKeyboardButton(year_text, callback_data=f"grade_year_{year}")])
            keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="cancel_onboarding")])
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return OnboardingState.SELECTING_GRADE_YEAR
            
        except Exception as e:
            self.logger.error(f"❌ Handle grade band failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در انتخاب مقطع. لطفاً دوباره تلاش کنید.")
            return ConversationHandler.END
    
    async def handle_grade_year(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle grade year selection"""
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            user_id = user.id
            grade_year = query.data.replace("grade_year_", "")
            
            self.logger.info(f"User {user_id} selected grade year: {grade_year}")
            
            # Store grade year in context
            context.user_data['grade_year'] = grade_year
            
            # Ask for phone
            keyboard = [
                [InlineKeyboardButton("📱 ارسال شماره", callback_data="phone_send")],
                [InlineKeyboardButton("⏭️ رد کردن", callback_data="phone_skip")],
                [InlineKeyboardButton("❌ لغو", callback_data="cancel_onboarding")]
            ]
            
            await query.edit_message_text(
                ONBOARDING_TEXTS["ask_phone"],
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            return OnboardingState.COLLECTING_PHONE
            
        except Exception as e:
            self.logger.error(f"❌ Handle grade year failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در انتخاب پایه. لطفاً دوباره تلاش کنید.")
            return ConversationHandler.END
    
    async def handle_phone_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle phone choice"""
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            user_id = user.id
            choice = query.data.replace("phone_", "")
            
            self.logger.info(f"User {user_id} phone choice: {choice}")
            
            if choice == "send":
                await query.edit_message_text(
                    "📱 **لطفاً شماره تلفن خود را ارسال کنید:**\n\n"
                    "از دکمه 'ارسال شماره' استفاده کنید یا شماره را تایپ کنید.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("❌ لغو", callback_data="cancel_onboarding")
                    ]]),
                    parse_mode='Markdown'
                )
                return OnboardingState.COLLECTING_PHONE
            elif choice == "skip":
                context.user_data['phone'] = None
                await self.complete_onboarding(query, context)
                return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"❌ Handle phone choice failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در انتخاب شماره. لطفاً دوباره تلاش کنید.")
            return ConversationHandler.END
    
    async def handle_phone_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle phone contact"""
        try:
            user = update.effective_user
            user_id = user.id
            contact = update.message.contact
            
            self.logger.info(f"User {user_id} sent phone: {contact.phone_number}")
            
            # Store phone in context
            context.user_data['phone'] = contact.phone_number
            
            # Complete onboarding
            await self.complete_onboarding_message(update, context)
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"❌ Handle phone contact failed: {e}")
            await update.message.reply_text("❌ خطا در پردازش شماره. لطفاً دوباره تلاش کنید.")
            return ConversationHandler.END
    
    async def complete_onboarding(self, query, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Complete onboarding process"""
        try:
            user = query.from_user
            user_id = user.id
            
            # Get all user data
            real_name = context.user_data.get('real_name', 'نامشخص')
            nickname = context.user_data.get('nickname', 'نامشخص')
            study_track = context.user_data.get('study_track', 'نامشخص')
            grade_band = context.user_data.get('grade_band', 'نامشخص')
            grade_year = context.user_data.get('grade_year', 'نامشخص')
            phone = context.user_data.get('phone', 'ارسال نشده')
            
            self.logger.info(f"User {user_id} completed onboarding: {nickname}")
            
            # Save to database
            await self._save_user_to_database(user_id, user, context.user_data)
            
            # Show completion message
            welcome_text = ONBOARDING_TEXTS["final_welcome"].format(nickname=nickname)
            
            keyboard = [
                [InlineKeyboardButton("🌌 نقشه کیهانی", callback_data="go_home")]
            ]
            
            await query.edit_message_text(
                welcome_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Complete onboarding failed: {e}")
    
    async def complete_onboarding_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Complete onboarding process from message"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Get all user data
            real_name = context.user_data.get('real_name', 'نامشخص')
            nickname = context.user_data.get('nickname', 'نامشخص')
            study_track = context.user_data.get('study_track', 'نامشخص')
            grade_band = context.user_data.get('grade_band', 'نامشخص')
            grade_year = context.user_data.get('grade_year', 'نامشخص')
            phone = context.user_data.get('phone', 'ارسال نشده')
            
            self.logger.info(f"User {user_id} completed onboarding: {nickname}")
            
            # Save to database
            await self._save_user_to_database(user_id, user, context.user_data)
            
            # Show completion message
            welcome_text = ONBOARDING_TEXTS["final_welcome"].format(nickname=nickname)
            
            keyboard = [
                [InlineKeyboardButton("🌌 نقشه کیهانی", callback_data="go_home")]
            ]
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"❌ Complete onboarding message failed: {e}")
    
    async def cancel_onboarding(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel onboarding process"""
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            user_id = user.id
            
            self.logger.info(f"User {user_id} cancelled onboarding")
            
            # Clear user data
            context.user_data.clear()
            
            # Show cancellation message
            await query.edit_message_text(
                "❌ **ثبت‌نام لغو شد!** 😔\n\n"
                "هر وقت آماده بودی، دوباره `/start` رو بزن!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 خانه", callback_data="go_home")
                ]]),
                parse_mode='Markdown'
            )
            
            return ConversationHandler.END
            
        except Exception as e:
            self.logger.error(f"❌ Cancel onboarding failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در لغو ثبت‌نام. لطفاً دوباره تلاش کنید.")
            return ConversationHandler.END
    
    async def _save_user_to_database(self, user_id: int, user, user_data: dict) -> None:
        """Save user data to database"""
        try:
            from src.database.connection import db_manager
            
            # Prepare user data
            real_name = user_data.get('real_name', 'نامشخص')
            nickname = user_data.get('nickname', 'نامشخص')
            study_track = user_data.get('study_track', 'نامشخص')
            grade_band = user_data.get('grade_band', 'نامشخص')
            grade_year = user_data.get('grade_year', 'نامشخص')
            phone = user_data.get('phone', None)
            
            # Check if user already exists
            existing_user = await db_manager.fetch_one(
                "SELECT user_id FROM users WHERE user_id = $1", user_id
            )
            
            if existing_user:
                # Update existing user
                await db_manager.execute("""
                    UPDATE users SET
                        real_name = $2,
                        nickname = $3,
                        study_track = $4,
                        grade_band = $5,
                        grade_year = $6,
                        phone = $7,
                        updated_at = NOW()
                    WHERE user_id = $1
                """, user_id, real_name, nickname, study_track, grade_band, grade_year, phone)
                
                self.logger.info(f"Updated existing user {user_id} in database")
            else:
                # Insert new user
                await db_manager.execute("""
                    INSERT INTO users (
                        user_id, username, first_name, last_name,
                        real_name, nickname, study_track, grade_band,
                        grade_year, phone, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
                """, 
                user_id, 
                user.username, 
                user.first_name, 
                user.last_name,
                real_name, 
                nickname, 
                study_track, 
                grade_band,
                grade_year, 
                phone
                )
                
                self.logger.info(f"Inserted new user {user_id} to database")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save user {user_id} to database: {e}")
            # Don't raise exception to avoid breaking the onboarding flow