"""
🌌 SarlakBot v3.2.0 - Onboarding Handler
Clean, production-ready async Telegram onboarding flow
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.services.user_profile_service import (
    GradeLevel,
    Language,
    OnboardingState,
    ProfileData,
    StudyTrack,
    user_profile_service,
)
from src.utils.error_handler import safe_async_handler
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Conversation states
(
    SELECTING_LANGUAGE,
    ENTERING_NAME,
    ENTERING_NICKNAME,
    SELECTING_GRADE,
    SELECTING_TRACK,
    SELECTING_YEAR,
    CONFIRMING_PROFILE,
) = range(7)


class OnboardingHandler:
    """
    🌌 Onboarding Handler
    Clean, production-ready async Telegram onboarding flow
    """

    def __init__(self):
        self.logger = logger

    async def register(self, application: Application) -> None:
        """Register onboarding handlers"""
        try:
            self.logger.info("🚀 Registering onboarding handlers...")

            # Create conversation handler
            conversation_handler = ConversationHandler(
                entry_points=[
                    CommandHandler("start", self.start_command),
                    CallbackQueryHandler(
                        self.start_onboarding_callback, pattern="^start_onboarding$"
                    ),
                ],
                states={
                    SELECTING_LANGUAGE: [
                        CallbackQueryHandler(self.language_callback, pattern="^lang_")
                    ],
                    ENTERING_NAME: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.name_handler)
                    ],
                    ENTERING_NICKNAME: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.nickname_handler)
                    ],
                    SELECTING_GRADE: [CallbackQueryHandler(self.grade_callback, pattern="^grade_")],
                    SELECTING_TRACK: [CallbackQueryHandler(self.track_callback, pattern="^track_")],
                    SELECTING_YEAR: [CallbackQueryHandler(self.year_callback, pattern="^year_")],
                    CONFIRMING_PROFILE: [
                        CallbackQueryHandler(self.confirm_callback, pattern="^confirm_")
                    ],
                },
                fallbacks=[
                    CommandHandler("cancel", self.cancel_command),
                    CallbackQueryHandler(self.cancel_callback, pattern="^cancel$"),
                ],
                name="onboarding",
                persistent=True,
                per_message=False,
                per_chat=True,
                per_user=True,
            )

            # Register conversation handler
            application.add_handler(conversation_handler)

            # Register other handlers
            application.add_handler(CommandHandler("profile", self.profile_command))
            application.add_handler(CommandHandler("edit_profile", self.edit_profile_command))
            application.add_handler(
                CallbackQueryHandler(self.edit_profile_callback, pattern="^edit_profile$")
            )

            self.logger.info("✅ Onboarding handlers registered successfully")

        except Exception as e:
            self.logger.error(f"❌ Failed to register onboarding handlers: {e}")
            raise

    @safe_async_handler
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /start command"""
        try:
            user = update.effective_user
            user_id = user.id

            self.logger.info(f"🚀 User {user_id} started onboarding")

            # Check if user already has a profile
            existing_profile = await user_profile_service.get_user_profile(user_id)
            if existing_profile:
                await self._show_existing_profile_dashboard(update, existing_profile)
                return ConversationHandler.END

            # Check for referral code
            referral_code = None
            if context.args and context.args[0].startswith("ref_"):
                referral_code = context.args[0][4:]
                self.logger.info(f"Referral code detected: {referral_code}")

            # Process referral if code provided
            if referral_code:
                await self._process_referral(user_id, referral_code)

            # Start onboarding flow
            await self._show_language_selection(update)
            return SELECTING_LANGUAGE

        except Exception as e:
            self.logger.error(f"❌ Start command failed: {e}")
            await update.message.reply_text("❌ خطا در شروع ربات")
            return ConversationHandler.END

    @safe_async_handler
    async def start_onboarding_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle start onboarding callback"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = query.effective_user.id

            # Check if user already has a profile
            existing_profile = await user_profile_service.get_user_profile(user_id)
            if existing_profile:
                await self._show_existing_profile_dashboard(query, existing_profile)
                return ConversationHandler.END

            # Start onboarding flow
            await self._show_language_selection(query)
            return SELECTING_LANGUAGE

        except Exception as e:
            self.logger.error(f"❌ Start onboarding callback failed: {e}")
            await query.answer("❌ خطا در شروع فرآیند ثبت‌نام")
            return ConversationHandler.END

    async def _show_language_selection(self, update_or_query) -> None:
        """Show language selection"""
        try:
            text = """
🌟 **خوش آمدید به آکادمی سرلک!** / **Welcome to Sarlak Academy!**

🌍 **لطفاً زبان خود را انتخاب کنید** / **Please select your language:**

برای شروع سفر کیهانی‌ات، ابتدا زبان مورد نظرت رو انتخاب کن!
To begin your cosmic journey, first select your preferred language!
"""

            keyboard = [
                [
                    InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
                    InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if hasattr(update_or_query, "edit_message_text"):
                await update_or_query.edit_message_text(
                    text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update_or_query.reply_text(
                    text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
                )

        except Exception as e:
            self.logger.error(f"❌ Failed to show language selection: {e}")

    @safe_async_handler
    async def language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle language selection"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = query.effective_user.id
            language_code = query.data.split("_")[1]
            language = Language(language_code)

            # Save language to state
            state = OnboardingState(user_id=user_id, language=language)
            await user_profile_service.save_onboarding_state(state)

            # Get localized texts
            texts = user_profile_service.get_language_texts(language)

            # Show name input
            text = f"""
{texts['enter_name']}

⚠️ **نکات مهم:**
• نام باید بین 2 تا 50 کاراکتر باشد
• فقط حروف فارسی و انگلیسی مجاز است
• از کاراکترهای خاص استفاده نکنید

**Important Notes:**
• Name must be 2-50 characters
• Only Persian and English letters allowed
• No special characters
"""

            keyboard = [[InlineKeyboardButton("❌ لغو", callback_data="cancel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

            return ENTERING_NAME

        except Exception as e:
            self.logger.error(f"❌ Language callback failed: {e}")
            await query.answer("❌ خطا در انتخاب زبان")
            return ConversationHandler.END

    @safe_async_handler
    async def name_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle name input"""
        try:
            user_id = update.effective_user.id
            name = update.message.text.strip()

            # Get current state
            state = await user_profile_service.get_onboarding_state(user_id)
            if not state:
                await update.message.reply_text("❌ خطا در دریافت اطلاعات. لطفاً دوباره شروع کنید.")
                return ConversationHandler.END

            # Sanitize and validate name
            sanitized_name = user_profile_service.sanitize_input(name)
            is_valid, error_message = user_profile_service.validate_display_name(sanitized_name)

            if not is_valid:
                await update.message.reply_text(f"❌ {error_message}")
                return ENTERING_NAME

            # Update state
            state.display_name = sanitized_name
            await user_profile_service.save_onboarding_state(state)

            # Get localized texts
            texts = user_profile_service.get_language_texts(state.language)

            # Show nickname input
            text = f"""
{texts['enter_nickname']}

⚠️ **نکات مهم:**
• نام مستعار باید بین 2 تا 30 کاراکتر باشد
• فقط حروف، اعداد و _ مجاز است
• از فاصله و کاراکترهای خاص استفاده نکنید

**Important Notes:**
• Nickname must be 2-30 characters
• Only letters, numbers and _ allowed
• No spaces or special characters
"""

            keyboard = [[InlineKeyboardButton("❌ لغو", callback_data="cancel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

            return ENTERING_NICKNAME

        except Exception as e:
            self.logger.error(f"❌ Name handler failed: {e}")
            await update.message.reply_text("❌ خطا در پردازش نام")
            return ConversationHandler.END

    @safe_async_handler
    async def nickname_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle nickname input"""
        try:
            user_id = update.effective_user.id
            nickname = update.message.text.strip()

            # Get current state
            state = await user_profile_service.get_onboarding_state(user_id)
            if not state:
                await update.message.reply_text("❌ خطا در دریافت اطلاعات. لطفاً دوباره شروع کنید.")
                return ConversationHandler.END

            # Sanitize and validate nickname
            sanitized_nickname = user_profile_service.sanitize_input(nickname)
            is_valid, error_message = user_profile_service.validate_nickname(sanitized_nickname)

            if not is_valid:
                await update.message.reply_text(f"❌ {error_message}")
                return ENTERING_NICKNAME

            # Update state
            state.nickname = sanitized_nickname
            await user_profile_service.save_onboarding_state(state)

            # Get localized texts
            texts = user_profile_service.get_language_texts(state.language)

            # Show grade selection
            await self._show_grade_selection(update, texts)
            return SELECTING_GRADE

        except Exception as e:
            self.logger.error(f"❌ Nickname handler failed: {e}")
            await update.message.reply_text("❌ خطا در پردازش نام مستعار")
            return ConversationHandler.END

    async def _show_grade_selection(self, update, texts: dict) -> None:
        """Show grade level selection"""
        try:
            text = f"""
{texts['select_grade']}

لطفاً مقطع تحصیلی فعلی خود را انتخاب کنید:
Please select your current grade level:
"""

            keyboard = [
                [
                    InlineKeyboardButton("دهم / Grade 10", callback_data="grade_10"),
                    InlineKeyboardButton("یازدهم / Grade 11", callback_data="grade_11"),
                ],
                [
                    InlineKeyboardButton("دوازدهم / Grade 12", callback_data="grade_12"),
                    InlineKeyboardButton("فارغ‌التحصیل / Graduate", callback_data="grade_graduate"),
                ],
                [InlineKeyboardButton("دانشجو / Student", callback_data="grade_student")],
                [InlineKeyboardButton("❌ لغو", callback_data="cancel")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to show grade selection: {e}")

    @safe_async_handler
    async def grade_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle grade selection"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = query.effective_user.id
            grade_code = query.data.split("_")[1]
            grade = GradeLevel(grade_code)

            # Get current state
            state = await user_profile_service.get_onboarding_state(user_id)
            if not state:
                await query.edit_message_text("❌ خطا در دریافت اطلاعات. لطفاً دوباره شروع کنید.")
                return ConversationHandler.END

            # Update state
            state.grade_level = grade
            await user_profile_service.save_onboarding_state(state)

            # Get localized texts
            texts = user_profile_service.get_language_texts(state.language)

            # Show track selection
            await self._show_track_selection(query, texts)
            return SELECTING_TRACK

        except Exception as e:
            self.logger.error(f"❌ Grade callback failed: {e}")
            await query.answer("❌ خطا در انتخاب مقطع")
            return ConversationHandler.END

    async def _show_track_selection(self, query, texts: dict) -> None:
        """Show study track selection"""
        try:
            text = f"""
{texts['select_track']}

لطفاً رشته تحصیلی خود را انتخاب کنید:
Please select your study track:
"""

            keyboard = [
                [
                    InlineKeyboardButton("ریاضی و فیزیک", callback_data="track_math"),
                    InlineKeyboardButton("تجربی", callback_data="track_experimental"),
                ],
                [
                    InlineKeyboardButton("انسانی", callback_data="track_humanities"),
                    InlineKeyboardButton("هنر", callback_data="track_art"),
                ],
                [
                    InlineKeyboardButton("زبان", callback_data="track_language"),
                    InlineKeyboardButton("فنی و حرفه‌ای", callback_data="track_technical"),
                ],
                [InlineKeyboardButton("❌ لغو", callback_data="cancel")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to show track selection: {e}")

    @safe_async_handler
    async def track_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle track selection"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = query.effective_user.id
            track_code = query.data.split("_")[1]
            track = StudyTrack(track_code)

            # Get current state
            state = await user_profile_service.get_onboarding_state(user_id)
            if not state:
                await query.edit_message_text("❌ خطا در دریافت اطلاعات. لطفاً دوباره شروع کنید.")
                return ConversationHandler.END

            # Update state
            state.study_track = track
            await user_profile_service.save_onboarding_state(state)

            # Get localized texts
            texts = user_profile_service.get_language_texts(state.language)

            # Show year selection
            await self._show_year_selection(query, texts)
            return SELECTING_YEAR

        except Exception as e:
            self.logger.error(f"❌ Track callback failed: {e}")
            await query.answer("❌ خطا در انتخاب رشته")
            return ConversationHandler.END

    async def _show_year_selection(self, query, texts: dict) -> None:
        """Show target year selection"""
        try:
            current_year = 2025
            years = [current_year, current_year + 1, current_year + 2, current_year + 3]

            text = f"""
{texts['select_year']}

لطفاً سال هدف کنکور خود را انتخاب کنید:
Please select your target exam year:
"""

            keyboard = []
            for year in years:
                keyboard.append([InlineKeyboardButton(f"{year}", callback_data=f"year_{year}")])

            keyboard.append([InlineKeyboardButton("❌ لغو", callback_data="cancel")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to show year selection: {e}")

    @safe_async_handler
    async def year_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle year selection"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = query.effective_user.id
            year = int(query.data.split("_")[1])

            # Get current state
            state = await user_profile_service.get_onboarding_state(user_id)
            if not state:
                await query.edit_message_text("❌ خطا در دریافت اطلاعات. لطفاً دوباره شروع کنید.")
                return ConversationHandler.END

            # Update state
            state.target_year = year
            await user_profile_service.save_onboarding_state(state)

            # Show profile confirmation
            await self._show_profile_confirmation(query, state)
            return CONFIRMING_PROFILE

        except Exception as e:
            self.logger.error(f"❌ Year callback failed: {e}")
            await query.answer("❌ خطا در انتخاب سال")
            return ConversationHandler.END

    async def _show_profile_confirmation(self, query, state: OnboardingState) -> None:
        """Show profile confirmation"""
        try:
            # Get localized texts
            texts = user_profile_service.get_language_texts(state.language)

            text = f"""
{texts['confirm_profile']}

👤 **نام:** {state.display_name}
🏷️ **نام مستعار:** {state.nickname}
📚 **مقطع:** {state.grade_level.value}
🎯 **رشته:** {state.study_track.value}
📅 **سال هدف:** {state.target_year}

**Name:** {state.display_name}
**Nickname:** {state.nickname}
**Grade:** {state.grade_level.value}
**Track:** {state.study_track.value}
**Target Year:** {state.target_year}

آیا اطلاعات درست است؟
Is the information correct?
"""

            keyboard = [
                [
                    InlineKeyboardButton("✅ تأیید / Confirm", callback_data="confirm_yes"),
                    InlineKeyboardButton("✏️ ویرایش / Edit", callback_data="confirm_edit"),
                ],
                [InlineKeyboardButton("❌ لغو / Cancel", callback_data="cancel")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to show profile confirmation: {e}")

    @safe_async_handler
    async def confirm_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle profile confirmation"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = query.effective_user.id
            action = query.data.split("_")[1]

            if action == "yes":
                # Complete profile
                state = await user_profile_service.get_onboarding_state(user_id)
                if not state:
                    await query.edit_message_text(
                        "❌ خطا در دریافت اطلاعات. لطفاً دوباره شروع کنید."
                    )
                    return ConversationHandler.END

                # Create profile data
                profile_data = ProfileData(
                    user_id=state.user_id,
                    language=state.language,
                    display_name=state.display_name,
                    nickname=state.nickname,
                    study_track=state.study_track,
                    grade_level=state.grade_level,
                    target_year=state.target_year,
                    is_completed=True,
                )

                # Complete profile
                success = await user_profile_service.complete_profile(user_id, profile_data)

                if success:
                    # Get localized texts
                    texts = user_profile_service.get_language_texts(state.language)

                    text = f"""
{texts['profile_completed']}

🎉 **پروفایل شما با موفقیت تکمیل شد!**
🎉 **Your profile has been completed successfully!**

حالا می‌تونید از تمام امکانات ربات استفاده کنید!
Now you can use all bot features!

🚀 **امکانات موجود:**
• 📚 مطالعه هوشمند
• 🎯 آزمون‌های آنلاین
• 📊 تحلیل پیشرفت
• 🏆 رقابت و انگیزه
• 💬 پشتیبانی ۲۴/۷

**Available Features:**
• 📚 Smart Study
• 🎯 Online Tests
• 📊 Progress Analysis
• 🏆 Competition & Motivation
• 💬 24/7 Support
"""

                    keyboard = [
                        [
                            InlineKeyboardButton(
                                "🏠 منوی اصلی / Main Menu", callback_data="main_menu"
                            )
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await query.edit_message_text(
                        text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
                    )

                    self.logger.info(f"Profile completed for user {user_id}")
                    return ConversationHandler.END
                else:
                    await query.edit_message_text("❌ خطا در تکمیل پروفایل. لطفاً دوباره تلاش کنید.")
                    return ConversationHandler.END

            elif action == "edit":
                # Go back to language selection
                await self._show_language_selection(query)
                return SELECTING_LANGUAGE

        except Exception as e:
            self.logger.error(f"❌ Confirm callback failed: {e}")
            await query.answer("❌ خطا در تأیید پروفایل")
            return ConversationHandler.END

    @safe_async_handler
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /cancel command"""
        try:
            user_id = update.effective_user.id

            # Clean up state
            await user_profile_service._cleanup_onboarding_state(user_id)

            await update.message.reply_text(
                "❌ فرآیند ثبت‌نام لغو شد.\n❌ Onboarding process cancelled.",
                reply_markup=ReplyKeyboardRemove(),
            )

            self.logger.info(f"Onboarding cancelled for user {user_id}")
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

            user_id = query.effective_user.id

            # Clean up state
            await user_profile_service._cleanup_onboarding_state(user_id)

            await query.edit_message_text(
                "❌ فرآیند ثبت‌نام لغو شد.\n❌ Onboarding process cancelled."
            )

            self.logger.info(f"Onboarding cancelled for user {user_id}")
            return ConversationHandler.END

        except Exception as e:
            self.logger.error(f"❌ Cancel callback failed: {e}")
            return ConversationHandler.END

    @safe_async_handler
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /profile command"""
        try:
            user_id = update.effective_user.id

            # Get user profile
            profile = await user_profile_service.get_user_profile(user_id)

            if profile:
                await self._show_existing_profile_dashboard(update, profile)
            else:
                # Start onboarding
                await self._show_language_selection(update)

        except Exception as e:
            self.logger.error(f"❌ Profile command failed: {e}")
            await update.message.reply_text("❌ خطا در نمایش پروفایل")

    async def edit_profile_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /edit_profile command"""
        try:
            user_id = update.effective_user.id

            # Get user profile
            profile = await user_profile_service.get_user_profile(user_id)

            if profile:
                await self._show_edit_profile_options(update, profile)
            else:
                await update.message.reply_text("❌ پروفایل یافت نشد. لطفاً ابتدا ثبت‌نام کنید.")

        except Exception as e:
            self.logger.error(f"❌ Edit profile command failed: {e}")
            await update.message.reply_text("❌ خطا در ویرایش پروفایل")

    async def edit_profile_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle edit profile callback"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = query.effective_user.id

            # Get user profile
            profile = await user_profile_service.get_user_profile(user_id)

            if profile:
                await self._show_edit_profile_options(query, profile)
            else:
                await query.edit_message_text("❌ پروفایل یافت نشد. لطفاً ابتدا ثبت‌نام کنید.")

        except Exception as e:
            self.logger.error(f"❌ Edit profile callback failed: {e}")
            await query.answer("❌ خطا در ویرایش پروفایل")

    async def _show_existing_profile_dashboard(self, update_or_query, profile: ProfileData) -> None:
        """Show existing profile dashboard"""
        try:
            # Get localized texts
            texts = user_profile_service.get_language_texts(profile.language)

            text = f"""
🌟 **خوش برگشتی {profile.display_name}!** / **Welcome back {profile.display_name}!**

👤 **پروفایل شما** / **Your Profile:**
• نام / Name: {profile.display_name}
• نام مستعار / Nickname: {profile.nickname}
• مقطع / Grade: {profile.grade_level.value}
• رشته / Track: {profile.study_track.value}
• سال هدف / Target Year: {profile.target_year}

🚀 **امکانات موجود** / **Available Features:**
• 📚 مطالعه هوشمند / Smart Study
• 🎯 آزمون‌های آنلاین / Online Tests
• 📊 تحلیل پیشرفت / Progress Analysis
• 🏆 رقابت و انگیزه / Competition & Motivation
• 💬 پشتیبانی ۲۴/۷ / 24/7 Support
"""

            keyboard = [
                [
                    InlineKeyboardButton(
                        "✏️ ویرایش پروفایل / Edit Profile", callback_data="edit_profile"
                    ),
                    InlineKeyboardButton("📊 آمار / Statistics", callback_data="profile_stats"),
                ],
                [InlineKeyboardButton("🏠 منوی اصلی / Main Menu", callback_data="main_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if hasattr(update_or_query, "edit_message_text"):
                await update_or_query.edit_message_text(
                    text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update_or_query.reply_text(
                    text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
                )

        except Exception as e:
            self.logger.error(f"❌ Failed to show existing profile dashboard: {e}")

    async def _show_edit_profile_options(self, update_or_query, profile: ProfileData) -> None:
        """Show edit profile options"""
        try:
            # Get localized texts
            texts = user_profile_service.get_language_texts(profile.language)

            text = f"""
✏️ **ویرایش پروفایل** / **Edit Profile**

لطفاً بخش مورد نظر برای ویرایش را انتخاب کنید:
Please select the section you want to edit:

👤 **اطلاعات شخصی** / **Personal Information:**
• نام / Name: {profile.display_name}
• نام مستعار / Nickname: {profile.nickname}

📚 **اطلاعات تحصیلی** / **Academic Information:**
• مقطع / Grade: {profile.grade_level.value}
• رشته / Track: {profile.study_track.value}
• سال هدف / Target Year: {profile.target_year}
"""

            keyboard = [
                [
                    InlineKeyboardButton(
                        "👤 اطلاعات شخصی / Personal Info", callback_data="edit_personal"
                    ),
                    InlineKeyboardButton(
                        "📚 اطلاعات تحصیلی / Academic Info", callback_data="edit_academic"
                    ),
                ],
                [InlineKeyboardButton("🔙 بازگشت / Back", callback_data="profile_back")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if hasattr(update_or_query, "edit_message_text"):
                await update_or_query.edit_message_text(
                    text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update_or_query.reply_text(
                    text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
                )

        except Exception as e:
            self.logger.error(f"❌ Failed to show edit profile options: {e}")

    async def _process_referral(self, user_id: int, referral_code: str) -> None:
        """Process referral code"""
        try:
            # This is a placeholder for referral processing
            # In production, you'd implement actual referral logic
            self.logger.info(f"Processing referral code {referral_code} for user {user_id}")

        except Exception as e:
            self.logger.error(f"❌ Failed to process referral: {e}")


# Global handler instance
onboarding_handler = OnboardingHandler()
