"""
🌌 SarlakBot v3.0 - Main Menu Handler
Universe Map and navigation system
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler

from src.utils.logging import get_logger

logger = get_logger(__name__)


class MainMenuHandler:
    """
    🌌 Main Menu Handler
    Handles the universe map and main navigation
    """

    def __init__(self):
        self.logger = logger

    async def register(self, application: Application) -> None:
        """Register main menu handlers"""
        try:
            self.logger.info("🌌 Registering main menu handler...")

            # Register menu callbacks
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_callback, pattern="^menu_")
            )

            # Register go_home callback
            application.add_handler(
                CallbackQueryHandler(self._handle_go_home_callback, pattern="^go_home$")
            )

            # Register study callbacks
            application.add_handler(
                CallbackQueryHandler(self._handle_study_callback, pattern="^study_")
            )

            # Register coach callback
            application.add_handler(
                CallbackQueryHandler(self._handle_coach_callback, pattern="^coach$")
            )

            # Register main_menu callback
            application.add_handler(
                CallbackQueryHandler(self._handle_main_menu_callback, pattern="^main_menu$")
            )

            # Register profile_back callback
            application.add_handler(
                CallbackQueryHandler(self._handle_profile_back_callback, pattern="^profile_back$")
            )

            # Register menu_study callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_study_callback, pattern="^menu_study$")
            )

            # Register menu_profile callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_profile_callback, pattern="^menu_profile$")
            )

            # Register menu_reports callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_reports_callback, pattern="^menu_reports$")
            )

            # Register menu_motivation callback
            application.add_handler(
                CallbackQueryHandler(
                    self._handle_menu_motivation_callback, pattern="^menu_motivation$"
                )
            )

            # Register menu_competition callback
            application.add_handler(
                CallbackQueryHandler(
                    self._handle_menu_competition_callback, pattern="^menu_competition$"
                )
            )

            # Register menu_store callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_store_callback, pattern="^menu_store$")
            )

            # Register menu_compass callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_compass_callback, pattern="^menu_compass$")
            )

            # Register menu_settings callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_settings_callback, pattern="^menu_settings$")
            )

            # Register menu_help callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_help_callback, pattern="^menu_help$")
            )

            # Register menu_qa callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_qa_callback, pattern="^menu_qa$")
            )

            # Register menu_auto_tracking callback
            application.add_handler(
                CallbackQueryHandler(
                    self._handle_menu_auto_tracking_callback, pattern="^menu_auto_tracking$"
                )
            )

            # Register menu_referral callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_referral_callback, pattern="^menu_referral$")
            )

            # Register menu_competition callback
            application.add_handler(
                CallbackQueryHandler(
                    self._handle_menu_competition_callback, pattern="^menu_competition$"
                )
            )

            # Register menu_store callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_store_callback, pattern="^menu_store$")
            )

            # Register menu_compass callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_compass_callback, pattern="^menu_compass$")
            )

            # Register menu_settings callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_settings_callback, pattern="^menu_settings$")
            )

            # Register menu_help callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_help_callback, pattern="^menu_help$")
            )

            # Register menu_qa callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_qa_callback, pattern="^menu_qa$")
            )

            # Register menu_auto_tracking callback
            application.add_handler(
                CallbackQueryHandler(
                    self._handle_menu_auto_tracking_callback, pattern="^menu_auto_tracking$"
                )
            )

            # Register menu_referral callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_referral_callback, pattern="^menu_referral$")
            )

            # Register menu_competition callback
            application.add_handler(
                CallbackQueryHandler(
                    self._handle_menu_competition_callback, pattern="^menu_competition$"
                )
            )

            # Register menu_store callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_store_callback, pattern="^menu_store$")
            )

            # Register menu_compass callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_compass_callback, pattern="^menu_compass$")
            )

            # Register menu_settings callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_settings_callback, pattern="^menu_settings$")
            )

            # Register menu_help callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_help_callback, pattern="^menu_help$")
            )

            # Register menu_qa callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_qa_callback, pattern="^menu_qa$")
            )

            # Register menu_auto_tracking callback
            application.add_handler(
                CallbackQueryHandler(
                    self._handle_menu_auto_tracking_callback, pattern="^menu_auto_tracking$"
                )
            )

            # Register menu_referral callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_referral_callback, pattern="^menu_referral$")
            )

            # Register menu_competition callback
            application.add_handler(
                CallbackQueryHandler(
                    self._handle_menu_competition_callback, pattern="^menu_competition$"
                )
            )

            # Register menu_store callback
            application.add_handler(
                CallbackQueryHandler(self._handle_menu_store_callback, pattern="^menu_store$")
            )

            self.logger.info("✅ Main menu handler registered successfully")

        except Exception as e:
            self.logger.error(f"❌ Main menu handler registration failed: {e}")
            raise

    async def show_main_menu(self, query) -> None:
        """Render the main menu with primary navigation buttons"""
        try:
            text = "🏠 **صفحه اصلی**\n\n" "از منوی زیر یکی را انتخاب کن تا سفرت را ادامه دهیم 🚀"

            keyboard = [
                [
                    InlineKeyboardButton("🚀 شروع مطالعه", callback_data="menu_study"),
                    InlineKeyboardButton("🎯 دعوت دوستان", callback_data="referral_main"),
                ],
                [
                    InlineKeyboardButton("📝 گزارش کار", callback_data="menu_reports"),
                    InlineKeyboardButton("🪐 پروفایل", callback_data="menu_profile"),
                ],
                [
                    InlineKeyboardButton("🎯 انگیزه", callback_data="menu_motivation"),
                    InlineKeyboardButton("☄️ رقابت", callback_data="menu_competition"),
                ],
                [
                    InlineKeyboardButton("🛍️ فروشگاه", callback_data="menu_store"),
                    InlineKeyboardButton("🧭 قطب‌نما", callback_data="menu_compass"),
                ],
                [
                    InlineKeyboardButton("❓ پرسش و پاسخ", callback_data="menu_qa"),
                    InlineKeyboardButton("⚙️ تنظیمات", callback_data="menu_settings"),
                ],
                [
                    InlineKeyboardButton("🤖 ردیابی خودکار", callback_data="menu_auto_tracking"),
                    InlineKeyboardButton("🆘 راهنما", callback_data="menu_help"),
                ],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

        except Exception as e:
            self.logger.error(f"❌ Failed to show main menu: {e}")
            await query.edit_message_text("❌ خطا در نمایش منو")

    async def _handle_menu_callback(self, update, context) -> None:
        """Handle menu callbacks"""
        try:
            query = update.callback_query
            await query.answer()

            callback_data = query.data
            user = update.effective_user
            user_id = user.id

            self.logger.info(f"User {user_id} clicked menu: {callback_data}")

            # Handle different menu items
            if callback_data == "menu_study":
                await self._show_study_section(query)
            elif callback_data == "menu_reports":
                await self._show_reports_section(query)
            elif callback_data == "menu_profile":
                await self._show_profile_section(query)
            elif callback_data == "menu_referral":
                await self._show_referral_section(query)
            elif callback_data == "menu_motivation":
                await self._show_motivation_section(query)
            elif callback_data == "menu_competition":
                await self._show_competition_section(query)
            elif callback_data == "menu_store":
                await self._show_store_section(query)
            elif callback_data == "menu_compass":
                await self._show_compass_section(query)
            elif callback_data == "menu_settings":
                await self._show_settings_section(query)
            elif callback_data == "menu_help":
                await self._show_help_section(query)
            elif callback_data == "menu_qa":
                await self._show_qa_section(query)
            elif callback_data == "menu_auto_tracking":
                await self._show_auto_tracking_section(query)
            else:
                await query.edit_message_text(
                    "🚧 این بخش هنوز آماده نیست!\n\n" "به زودی اضافه می‌شه! ✨",
                    parse_mode="Markdown",
                )

        except Exception as e:
            self.logger.error(f"❌ Menu callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در navigation. لطفاً دوباره تلاش کنید.")

    async def _handle_go_home_callback(self, update, context) -> None:
        """Handle go_home callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show main menu
            await self.show_main_menu(query)

        except Exception as e:
            self.logger.error(f"❌ Go home callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به خانه")

    async def _handle_study_callback(self, update, context) -> None:
        """Handle study callbacks"""
        try:
            query = update.callback_query
            await query.answer()

            callback_data = query.data
            user_id = query.effective_user.id

            self.logger.info(f"User {user_id} clicked study: {callback_data}")

            if callback_data == "study_start_session":
                from src.handlers.main_menu.study_methods import study_methods

                await study_methods.show_study_session_start(query)
            elif callback_data == "study_content":
                from src.handlers.main_menu.study_methods import study_methods

                await study_methods.show_study_content(query)
            elif callback_data == "study_quiz":
                from src.handlers.main_menu.study_methods import study_methods

                await study_methods.show_study_quiz(query)
            elif callback_data == "study_progress":
                from src.handlers.main_menu.study_methods import study_methods

                await study_methods.show_study_progress(query)
            elif callback_data == "study_goals":
                from src.handlers.main_menu.study_methods import study_methods

                await study_methods.show_study_goals(query)
            else:
                await query.edit_message_text(
                    "🚧 این بخش هنوز آماده نیست!\n\n" "به زودی اضافه می‌شه! ✨",
                    parse_mode="Markdown",
                )

        except Exception as e:
            self.logger.error(f"❌ Study callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بخش مطالعه")

    async def _handle_coach_callback(self, update, context) -> None:
        """Handle coach callback"""
        try:
            query = update.callback_query
            await query.answer()

            user_id = query.effective_user.id
            self.logger.info(f"User {user_id} clicked coach")

            # Delegate to AI Coach handler
            from src.handlers.ai_coach.ai_coach_integration import ai_coach_integration

            await ai_coach_integration.coach_handler.start_ai_coach(query, context)

        except Exception as e:
            self.logger.error(f"❌ Coach callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در دسترسی به AI Coach")

    async def _handle_main_menu_callback(self, update, context) -> None:
        """Handle main_menu callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show main menu
            await self.show_main_menu(query)

        except Exception as e:
            self.logger.error(f"❌ Main menu callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به منوی اصلی")

    async def _handle_profile_back_callback(self, update, context) -> None:
        """Handle profile_back callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show profile section
            await self._show_profile_section(query)

        except Exception as e:
            self.logger.error(f"❌ Profile back callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به پروفایل")

    async def _handle_menu_study_callback(self, update, context) -> None:
        """Handle menu_study callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show study section
            await self._show_study_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu study callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش مطالعه")

    async def _handle_menu_profile_callback(self, update, context) -> None:
        """Handle menu_profile callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show profile section
            await self._show_profile_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu profile callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش پروفایل")

    async def _handle_menu_reports_callback(self, update, context) -> None:
        """Handle menu_reports callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show reports section
            await self._show_reports_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu reports callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش گزارش‌ها")

    async def _handle_menu_motivation_callback(self, update, context) -> None:
        """Handle menu_motivation callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show motivation section
            await self._show_motivation_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu motivation callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش انگیزه")

    async def _handle_menu_competition_callback(self, update, context) -> None:
        """Handle menu_competition callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show competition section
            await self._show_competition_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu competition callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش رقابت")

    async def _handle_menu_store_callback(self, update, context) -> None:
        """Handle menu_store callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show store section
            await self._show_store_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu store callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش فروشگاه")

    async def _handle_menu_compass_callback(self, update, context) -> None:
        """Handle menu_compass callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show compass section
            await self._show_compass_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu compass callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش قطب‌نما")

    async def _handle_menu_settings_callback(self, update, context) -> None:
        """Handle menu_settings callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show settings section
            await self._show_settings_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu settings callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش تنظیمات")

    async def _handle_menu_help_callback(self, update, context) -> None:
        """Handle menu_help callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show help section
            await self._show_help_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu help callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش راهنما")

    async def _handle_menu_qa_callback(self, update, context) -> None:
        """Handle menu_qa callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show Q&A section
            await self._show_qa_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu Q&A callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش پرسش و پاسخ")

    async def _handle_menu_auto_tracking_callback(self, update, context) -> None:
        """Handle menu_auto_tracking callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show auto tracking section
            await self._show_auto_tracking_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu auto tracking callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش ردیابی خودکار")

    async def _handle_menu_referral_callback(self, update, context) -> None:
        """Handle menu_referral callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show referral section
            await self._show_referral_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu referral callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش دعوت دوستان")

    async def _handle_menu_competition_callback(self, update, context) -> None:
        """Handle menu_competition callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show competition section
            await self._show_competition_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu competition callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش رقابت")

    async def _handle_menu_store_callback(self, update, context) -> None:
        """Handle menu_store callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show store section
            await self._show_store_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu store callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش فروشگاه")

    async def _handle_menu_compass_callback(self, update, context) -> None:
        """Handle menu_compass callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show compass section
            await self._show_compass_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu compass callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش قطب‌نما")

    async def _handle_menu_settings_callback(self, update, context) -> None:
        """Handle menu_settings callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show settings section
            await self._show_settings_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu settings callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش تنظیمات")

    async def _handle_menu_help_callback(self, update, context) -> None:
        """Handle menu_help callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show help section
            await self._show_help_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu help callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش راهنما")

    async def _handle_menu_qa_callback(self, update, context) -> None:
        """Handle menu_qa callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show Q&A section
            await self._show_qa_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu Q&A callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش پرسش و پاسخ")

    async def _handle_menu_auto_tracking_callback(self, update, context) -> None:
        """Handle menu_auto_tracking callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show auto tracking section
            await self._show_auto_tracking_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu auto tracking callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش ردیابی خودکار")

    async def _handle_menu_referral_callback(self, update, context) -> None:
        """Handle menu_referral callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show referral section
            await self._show_referral_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu referral callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش دعوت دوستان")

    async def _handle_menu_competition_callback(self, update, context) -> None:
        """Handle menu_competition callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show competition section
            await self._show_competition_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu competition callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش رقابت")

    async def _handle_menu_store_callback(self, update, context) -> None:
        """Handle menu_store callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show store section
            await self._show_store_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu store callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش فروشگاه")

    async def _handle_menu_compass_callback(self, update, context) -> None:
        """Handle menu_compass callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show compass section
            await self._show_compass_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu compass callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش قطب‌نما")

    async def _handle_menu_settings_callback(self, update, context) -> None:
        """Handle menu_settings callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show settings section
            await self._show_settings_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu settings callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش تنظیمات")

    async def _handle_menu_help_callback(self, update, context) -> None:
        """Handle menu_help callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show help section
            await self._show_help_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu help callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش راهنما")

    async def _handle_menu_qa_callback(self, update, context) -> None:
        """Handle menu_qa callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show Q&A section
            await self._show_qa_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu Q&A callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش پرسش و پاسخ")

    async def _handle_menu_auto_tracking_callback(self, update, context) -> None:
        """Handle menu_auto_tracking callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show auto tracking section
            await self._show_auto_tracking_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu auto tracking callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش ردیابی خودکار")

    async def _handle_menu_referral_callback(self, update, context) -> None:
        """Handle menu_referral callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show referral section
            await self._show_referral_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu referral callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش دعوت دوستان")

    async def _handle_menu_competition_callback(self, update, context) -> None:
        """Handle menu_competition callback"""
        try:
            query = update.callback_query
            await query.answer()

            # Show competition section
            await self._show_competition_section(query)

        except Exception as e:
            self.logger.error(f"❌ Menu competition callback failed: {e}")
            if update.callback_query:
                await update.callback_query.answer("❌ خطا در بازگشت به بخش رقابت")

    async def _show_study_section(self, query) -> None:
        """Show study section"""
        text = """
🚀 **شروع مطالعه** - مرکز یادگیری هوشمند

اینجا می‌تونی:
• جلسه مطالعه جدید شروع کنی
• از محتوای آموزشی استفاده کنی
• آزمون‌های آنلاین بدهی
• پیشرفتت رو پیگیری کنی
• از AI Coach کمک بگیری

**آماده‌ای برای شروع سفر یادگیری؟** 📚✨
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [
                InlineKeyboardButton("📚 شروع جلسه مطالعه", callback_data="study_start_session"),
                InlineKeyboardButton("📖 محتوای آموزشی", callback_data="study_content"),
            ],
            [
                InlineKeyboardButton("📝 آزمون آنلاین", callback_data="study_quiz"),
                InlineKeyboardButton("🤖 AI Coach", callback_data="coach"),
            ],
            [
                InlineKeyboardButton("📊 پیشرفت من", callback_data="study_progress"),
                InlineKeyboardButton("🎯 اهداف", callback_data="study_goals"),
            ],
            [InlineKeyboardButton("🏠 خانه", callback_data="go_home")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_reports_section(self, query) -> None:
        """Show reports section"""
        text = """
🌕 **گزارش کار** - پیگیری مطالعه

اینجا می‌تونی:
• گزارش مطالعه روزانه ثبت کنی
• پیشرفتت رو ببینی
• آمار مطالعه‌ات رو چک کنی
• هدف‌هایت رو تنظیم کنی

**آماده‌ای برای شروع؟** 🚀
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [
                InlineKeyboardButton("📅 گزارش امروز", callback_data="report_today"),
                InlineKeyboardButton("📈 گزارش هفتگی", callback_data="report_weekly"),
            ],
            [
                InlineKeyboardButton("📊 گزارش ماهانه", callback_data="report_monthly"),
                InlineKeyboardButton("📋 آمار کامل", callback_data="report_statistics"),
            ],
            [
                InlineKeyboardButton("➕ ثبت جلسه مطالعه", callback_data="report_log_study"),
                InlineKeyboardButton("🎯 تنظیم اهداف", callback_data="report_goals"),
            ],
            [InlineKeyboardButton("🏠 خانه", callback_data="report_home")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_auto_tracking_section(self, query) -> None:
        """Show auto tracking section"""
        text = """
🤖 **ردیابی خودکار مطالعه**

🎯 **قابلیت‌های هوشمند:**
• 🔍 تشخیص خودکار جلسات مطالعه
• 📈 تحلیل الگوهای مطالعه
• 💡 توصیه‌های شخصی‌سازی شده
• 🎯 تنظیم خودکار اهداف
• 📊 گزارش‌های هوشمند

💡 **نکته:** ردیابی خودکار به شما کمک می‌کند تا بدون نیاز به ثبت دستی، پیشرفت خود را پیگیری کنید.

**آماده‌ای برای شروع؟** 🚀
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("▶️ شروع ردیابی", callback_data="report_start_auto_tracking")],
            [InlineKeyboardButton("📊 وضعیت ردیابی", callback_data="report_auto_tracking")],
            [
                InlineKeyboardButton(
                    "💡 توصیه‌های هوشمند", callback_data="report_smart_recommendations"
                )
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_profile_section(self, query) -> None:
        """Show profile section - delegate to profile handler"""
        try:
            # Delegate to profile handler
            from src.handlers.profile.profile_handler_v3 import profile_handler_v3

            await profile_handler_v3.profile_callback(query, None)
        except Exception as e:
            self.logger.error(f"❌ Failed to show profile section: {e}")
            await query.edit_message_text("❌ خطا در نمایش پروفایل")

    async def _show_referral_section(self, query) -> None:
        """Show referral section"""
        text = """
🎯 **دعوت دوستان** - سیستم دعوت و پاداش

اینجا می‌تونی:
• کد دعوت خودت رو دریافت کنی
• دوستانت رو دعوت کنی
• امتیاز و توکن کسب کنی
• در قرعه‌کشی‌ها شرکت کنی
• آمار دعوت‌هات رو ببینی

**بیا دوستانت رو دعوت کنیم!** 🚀
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("🎫 کد دعوت من", callback_data="referral_my_code")],
            [InlineKeyboardButton("📊 آمار دعوت‌ها", callback_data="referral_stats")],
            [InlineKeyboardButton("🏆 جدول رتبه‌بندی", callback_data="referral_leaderboard")],
            [InlineKeyboardButton("🪙 موجودی توکن‌ها", callback_data="referral_tokens")],
            [InlineKeyboardButton("🎲 قرعه‌کشی‌ها", callback_data="referral_lottery")],
            [InlineKeyboardButton("🏠 خانه", callback_data="go_home")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_auto_tracking_section(self, query) -> None:
        """Show auto tracking section"""
        text = """
🤖 **ردیابی خودکار مطالعه**

🎯 **قابلیت‌های هوشمند:**
• 🔍 تشخیص خودکار جلسات مطالعه
• 📈 تحلیل الگوهای مطالعه
• 💡 توصیه‌های شخصی‌سازی شده
• 🎯 تنظیم خودکار اهداف
• 📊 گزارش‌های هوشمند

💡 **نکته:** ردیابی خودکار به شما کمک می‌کند تا بدون نیاز به ثبت دستی، پیشرفت خود را پیگیری کنید.

**آماده‌ای برای شروع؟** 🚀
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("▶️ شروع ردیابی", callback_data="report_start_auto_tracking")],
            [InlineKeyboardButton("📊 وضعیت ردیابی", callback_data="report_auto_tracking")],
            [
                InlineKeyboardButton(
                    "💡 توصیه‌های هوشمند", callback_data="report_smart_recommendations"
                )
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_motivation_section(self, query) -> None:
        """Show motivation section"""
        text = """
🌟 **انگیزه** - سوخت سفر کیهانی‌ات

اینجا می‌تونی:
• نقل‌قول‌های انگیزشی ببینی
• مأموریت‌های روزانه دریافت کنی
• چالش‌های انگیزشی انجام بدی
• انگیزه‌ت رو بالا نگه داری

**بیا انگیزه‌ت رو شارژ کنیم!** ⚡
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("💬 نقل‌قول روزانه", callback_data="motivation_quote")],
            [InlineKeyboardButton("🎯 مأموریت روزانه", callback_data="motivation_mission")],
            [InlineKeyboardButton("🏆 چالش‌ها", callback_data="motivation_challenges")],
            [InlineKeyboardButton("🏠 خانه", callback_data="go_home")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_auto_tracking_section(self, query) -> None:
        """Show auto tracking section"""
        text = """
🤖 **ردیابی خودکار مطالعه**

🎯 **قابلیت‌های هوشمند:**
• 🔍 تشخیص خودکار جلسات مطالعه
• 📈 تحلیل الگوهای مطالعه
• 💡 توصیه‌های شخصی‌سازی شده
• 🎯 تنظیم خودکار اهداف
• 📊 گزارش‌های هوشمند

💡 **نکته:** ردیابی خودکار به شما کمک می‌کند تا بدون نیاز به ثبت دستی، پیشرفت خود را پیگیری کنید.

**آماده‌ای برای شروع؟** 🚀
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("▶️ شروع ردیابی", callback_data="report_start_auto_tracking")],
            [InlineKeyboardButton("📊 وضعیت ردیابی", callback_data="report_auto_tracking")],
            [
                InlineKeyboardButton(
                    "💡 توصیه‌های هوشمند", callback_data="report_smart_recommendations"
                )
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_competition_section(self, query) -> None:
        """Show competition section"""
        text = """
☄️ **رقابت** - جنگ ستاره‌ای کنکور

اینجا می‌تونی:
• با دوستانت رقابت کنی
• در جدول امتیازات شرکت کنی
• چالش‌های گروهی انجام بدی
• رتبه‌ت رو ببینی

**آماده‌ای برای جنگ؟** ⚔️
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("🏆 جدول امتیازات", callback_data="competition_leaderboard")],
            [InlineKeyboardButton("👥 رقبا", callback_data="competition_rivals")],
            [InlineKeyboardButton("🎮 چالش‌ها", callback_data="competition_challenges")],
            [InlineKeyboardButton("🏠 خانه", callback_data="go_home")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_auto_tracking_section(self, query) -> None:
        """Show auto tracking section"""
        text = """
🤖 **ردیابی خودکار مطالعه**

🎯 **قابلیت‌های هوشمند:**
• 🔍 تشخیص خودکار جلسات مطالعه
• 📈 تحلیل الگوهای مطالعه
• 💡 توصیه‌های شخصی‌سازی شده
• 🎯 تنظیم خودکار اهداف
• 📊 گزارش‌های هوشمند

💡 **نکته:** ردیابی خودکار به شما کمک می‌کند تا بدون نیاز به ثبت دستی، پیشرفت خود را پیگیری کنید.

**آماده‌ای برای شروع؟** 🚀
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("▶️ شروع ردیابی", callback_data="report_start_auto_tracking")],
            [InlineKeyboardButton("📊 وضعیت ردیابی", callback_data="report_auto_tracking")],
            [
                InlineKeyboardButton(
                    "💡 توصیه‌های هوشمند", callback_data="report_smart_recommendations"
                )
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_store_section(self, query) -> None:
        """Show store section"""
        text = """
🛍️ **فروشگاه** - بازار کیهانی

اینجا می‌تونی:
• دوره‌های آموزشی ببینی
• کتاب‌ها و منابع خریداری کنی
• پکیج‌های ویژه دریافت کنی
• تخفیف‌های ویژه ببینی

**بیا خرید کنیم!** 🛒
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("📚 دوره‌ها", callback_data="store_courses")],
            [InlineKeyboardButton("📖 کتاب‌ها", callback_data="store_books")],
            [InlineKeyboardButton("🎁 پکیج‌ها", callback_data="store_packages")],
            [InlineKeyboardButton("🏠 خانه", callback_data="go_home")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_auto_tracking_section(self, query) -> None:
        """Show auto tracking section"""
        text = """
🤖 **ردیابی خودکار مطالعه**

🎯 **قابلیت‌های هوشمند:**
• 🔍 تشخیص خودکار جلسات مطالعه
• 📈 تحلیل الگوهای مطالعه
• 💡 توصیه‌های شخصی‌سازی شده
• 🎯 تنظیم خودکار اهداف
• 📊 گزارش‌های هوشمند

💡 **نکته:** ردیابی خودکار به شما کمک می‌کند تا بدون نیاز به ثبت دستی، پیشرفت خود را پیگیری کنید.

**آماده‌ای برای شروع؟** 🚀
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("▶️ شروع ردیابی", callback_data="report_start_auto_tracking")],
            [InlineKeyboardButton("📊 وضعیت ردیابی", callback_data="report_auto_tracking")],
            [
                InlineKeyboardButton(
                    "💡 توصیه‌های هوشمند", callback_data="report_smart_recommendations"
                )
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_compass_section(self, query) -> None:
        """Show compass section"""
        text = """
🧭 **قطب‌نما** - راهنمای کیهانی

اینجا می‌تونی:
• رتبه‌ت رو تخمین بزنی
• دانشگاه‌های مناسب رو ببینی
• مسیر تحصیلی‌ت رو برنامه‌ریزی کنی
• مشاوره تحصیلی دریافت کنی

**بیا مسیرت رو پیدا کنیم!** 🗺️
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("🎯 تخمین رتبه", callback_data="compass_rank")],
            [InlineKeyboardButton("🏫 دانشگاه‌ها", callback_data="compass_universities")],
            [InlineKeyboardButton("📋 برنامه‌ریزی", callback_data="compass_planning")],
            [InlineKeyboardButton("🏠 خانه", callback_data="go_home")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_auto_tracking_section(self, query) -> None:
        """Show auto tracking section"""
        text = """
🤖 **ردیابی خودکار مطالعه**

🎯 **قابلیت‌های هوشمند:**
• 🔍 تشخیص خودکار جلسات مطالعه
• 📈 تحلیل الگوهای مطالعه
• 💡 توصیه‌های شخصی‌سازی شده
• 🎯 تنظیم خودکار اهداف
• 📊 گزارش‌های هوشمند

💡 **نکته:** ردیابی خودکار به شما کمک می‌کند تا بدون نیاز به ثبت دستی، پیشرفت خود را پیگیری کنید.

**آماده‌ای برای شروع؟** 🚀
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("▶️ شروع ردیابی", callback_data="report_start_auto_tracking")],
            [InlineKeyboardButton("📊 وضعیت ردیابی", callback_data="report_auto_tracking")],
            [
                InlineKeyboardButton(
                    "💡 توصیه‌های هوشمند", callback_data="report_smart_recommendations"
                )
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_settings_section(self, query) -> None:
        """Show settings section"""
        text = """
⚙️ **تنظیمات** - کنترل مرکزی

اینجا می‌تونی:
• تنظیمات شخصی‌ت رو تغییر بدی
• اعلان‌ها رو مدیریت کنی
• حریم خصوصی‌ت رو تنظیم کنی
• حساب کاربری‌ت رو مدیریت کنی

**بیا تنظیماتت رو شخصی‌سازی کنیم!** 🔧
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("🔔 اعلان‌ها", callback_data="settings_notifications")],
            [InlineKeyboardButton("🔒 حریم خصوصی", callback_data="settings_privacy")],
            [InlineKeyboardButton("👤 حساب کاربری", callback_data="settings_account")],
            [InlineKeyboardButton("🏠 خانه", callback_data="go_home")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_auto_tracking_section(self, query) -> None:
        """Show auto tracking section"""
        text = """
🤖 **ردیابی خودکار مطالعه**

🎯 **قابلیت‌های هوشمند:**
• 🔍 تشخیص خودکار جلسات مطالعه
• 📈 تحلیل الگوهای مطالعه
• 💡 توصیه‌های شخصی‌سازی شده
• 🎯 تنظیم خودکار اهداف
• 📊 گزارش‌های هوشمند

💡 **نکته:** ردیابی خودکار به شما کمک می‌کند تا بدون نیاز به ثبت دستی، پیشرفت خود را پیگیری کنید.

**آماده‌ای برای شروع؟** 🚀
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("▶️ شروع ردیابی", callback_data="report_start_auto_tracking")],
            [InlineKeyboardButton("📊 وضعیت ردیابی", callback_data="report_auto_tracking")],
            [
                InlineKeyboardButton(
                    "💡 توصیه‌های هوشمند", callback_data="report_smart_recommendations"
                )
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_qa_section(self, query) -> None:
        """Show Q&A section"""
        text = """
🤖 **پرسش و پاسخ هوشمند** - دستیار شخصی شما

اینجا می‌تونی:
• سوالات درسی و کنکوری بپرسی
• مشاوره تحصیلی دریافت کنی
• راهنمایی انگیزشی بگیری
• پاسخ‌های شخصی‌سازی شده دریافت کنی

**هوش مصنوعی من هر روز بهتر و بهتر شما رو می‌شناسه!** 🧠✨
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("❓ پرسیدن سوال", callback_data="qa_ask")],
            [InlineKeyboardButton("📚 دسته‌بندی‌ها", callback_data="qa_categories")],
            [InlineKeyboardButton("🔥 سوالات محبوب", callback_data="qa_popular")],
            [InlineKeyboardButton("📊 آمار من", callback_data="qa_stats")],
            [InlineKeyboardButton("🏠 خانه", callback_data="go_home")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_auto_tracking_section(self, query) -> None:
        """Show auto tracking section"""
        text = """
🤖 **ردیابی خودکار مطالعه**

🎯 **قابلیت‌های هوشمند:**
• 🔍 تشخیص خودکار جلسات مطالعه
• 📈 تحلیل الگوهای مطالعه
• 💡 توصیه‌های شخصی‌سازی شده
• 🎯 تنظیم خودکار اهداف
• 📊 گزارش‌های هوشمند

💡 **نکته:** ردیابی خودکار به شما کمک می‌کند تا بدون نیاز به ثبت دستی، پیشرفت خود را پیگیری کنید.

**آماده‌ای برای شروع؟** 🚀
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("▶️ شروع ردیابی", callback_data="report_start_auto_tracking")],
            [InlineKeyboardButton("📊 وضعیت ردیابی", callback_data="report_auto_tracking")],
            [
                InlineKeyboardButton(
                    "💡 توصیه‌های هوشمند", callback_data="report_smart_recommendations"
                )
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_help_section(self, query) -> None:
        """Show help section"""
        text = """
❓ **راهنما** - مرکز کمک

اینجا می‌تونی:
• راهنمای استفاده از ربات رو ببینی
• سوالات متداول رو چک کنی
• با پشتیبانی تماس بگیری
• پیشنهاداتت رو ارسال کنی

**چطور می‌تونم کمکت کنم؟** 🤝
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("📖 راهنمای کامل", callback_data="help_guide")],
            [InlineKeyboardButton("❓ سوالات متداول", callback_data="help_faq")],
            [InlineKeyboardButton("💬 پشتیبانی", callback_data="help_support")],
            [InlineKeyboardButton("🏠 خانه", callback_data="go_home")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def _show_auto_tracking_section(self, query) -> None:
        """Show auto tracking section"""
        text = """
🤖 **ردیابی خودکار مطالعه**

🎯 **قابلیت‌های هوشمند:**
• 🔍 تشخیص خودکار جلسات مطالعه
• 📈 تحلیل الگوهای مطالعه
• 💡 توصیه‌های شخصی‌سازی شده
• 🎯 تنظیم خودکار اهداف
• 📊 گزارش‌های هوشمند

💡 **نکته:** ردیابی خودکار به شما کمک می‌کند تا بدون نیاز به ثبت دستی، پیشرفت خود را پیگیری کنید.

**آماده‌ای برای شروع؟** 🚀
"""

        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = [
            [InlineKeyboardButton("▶️ شروع ردیابی", callback_data="report_start_auto_tracking")],
            [InlineKeyboardButton("📊 وضعیت ردیابی", callback_data="report_auto_tracking")],
            [
                InlineKeyboardButton(
                    "💡 توصیه‌های هوشمند", callback_data="report_smart_recommendations"
                )
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# Global handler instance
main_menu_handler = MainMenuHandler()
