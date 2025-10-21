"""
🌌 SarlakBot v3.2.0 - Internationalization System
Comprehensive multi-language support
"""

from enum import Enum
from typing import Optional

from src.utils.logging import get_logger

logger = get_logger(__name__)


class Language(Enum):
    """Supported languages"""

    PERSIAN = "fa"
    ENGLISH = "en"


class I18nSystem:
    """
    🌌 Internationalization System
    Comprehensive multi-language support with fallback
    """

    def __init__(self):
        self.logger = logger
        self.default_language = Language.PERSIAN
        self._translations = self._load_translations()

    def _load_translations(self) -> dict[str, dict[str, str]]:
        """Load all translations"""
        return {
            Language.PERSIAN.value: {
                # Onboarding
                "welcome": "🌟 خوش آمدید به آکادمی سرلک!",
                "select_language": "🌍 لطفاً زبان خود را انتخاب کنید:",
                "enter_name": "👤 نام خود را وارد کنید:",
                "enter_nickname": "🏷️ نام مستعار خود را وارد کنید:",
                "select_grade": "📚 مقطع تحصیلی خود را انتخاب کنید:",
                "select_track": "🎯 رشته تحصیلی خود را انتخاب کنید:",
                "select_year": "📅 سال هدف کنکور خود را انتخاب کنید:",
                "confirm_profile": "✅ اطلاعات پروفایل خود را تأیید کنید:",
                "profile_completed": "🎉 پروفایل شما با موفقیت تکمیل شد!",
                # Profile
                "profile_title": "👤 پروفایل شما",
                "edit_profile": "✏️ ویرایش پروفایل",
                "profile_stats": "📊 آمار",
                "main_menu": "🏠 منوی اصلی",
                # Errors
                "error_general": "❌ خطا در پردازش درخواست",
                "error_validation": "❌ ورودی نامعتبر",
                "error_network": "❌ خطا در اتصال",
                "error_database": "❌ خطا در پایگاه داده",
                "error_timeout": "❌ زمان انتظار به پایان رسید",
                # Success
                "success_saved": "✅ با موفقیت ذخیره شد",
                "success_updated": "✅ با موفقیت به‌روزرسانی شد",
                "success_deleted": "✅ با موفقیت حذف شد",
                # Buttons
                "btn_confirm": "✅ تأیید",
                "btn_cancel": "❌ لغو",
                "btn_edit": "✏️ ویرایش",
                "btn_delete": "🗑️ حذف",
                "btn_back": "🔙 بازگشت",
                "btn_next": "➡️ بعدی",
                "btn_previous": "⬅️ قبلی",
                "btn_retry": "🔄 تلاش مجدد",
                # Validation
                "validation_required": "این فیلد الزامی است",
                "validation_min_length": "حداقل {min} کاراکتر",
                "validation_max_length": "حداکثر {max} کاراکتر",
                "validation_invalid_format": "فرمت نامعتبر",
                "validation_persian_only": "فقط حروف فارسی",
                "validation_english_only": "فقط حروف انگلیسی",
                "validation_alphanumeric": "فقط حروف و اعداد",
                # System
                "system_maintenance": "🔧 سیستم در حال نگهداری",
                "system_error": "❌ خطای سیستم",
                "system_offline": "🔌 سیستم آفلاین",
                "system_online": "🟢 سیستم آنلاین",
            },
            Language.ENGLISH.value: {
                # Onboarding
                "welcome": "🌟 Welcome to Sarlak Academy!",
                "select_language": "🌍 Please select your language:",
                "enter_name": "👤 Enter your name:",
                "enter_nickname": "🏷️ Enter your nickname:",
                "select_grade": "📚 Select your grade level:",
                "select_track": "🎯 Select your study track:",
                "select_year": "📅 Select your target exam year:",
                "confirm_profile": "✅ Confirm your profile information:",
                "profile_completed": "🎉 Your profile has been completed successfully!",
                # Profile
                "profile_title": "👤 Your Profile",
                "edit_profile": "✏️ Edit Profile",
                "profile_stats": "📊 Statistics",
                "main_menu": "🏠 Main Menu",
                # Errors
                "error_general": "❌ Error processing request",
                "error_validation": "❌ Invalid input",
                "error_network": "❌ Connection error",
                "error_database": "❌ Database error",
                "error_timeout": "❌ Timeout occurred",
                # Success
                "success_saved": "✅ Successfully saved",
                "success_updated": "✅ Successfully updated",
                "success_deleted": "✅ Successfully deleted",
                # Buttons
                "btn_confirm": "✅ Confirm",
                "btn_cancel": "❌ Cancel",
                "btn_edit": "✏️ Edit",
                "btn_delete": "🗑️ Delete",
                "btn_back": "🔙 Back",
                "btn_next": "➡️ Next",
                "btn_previous": "⬅️ Previous",
                "btn_retry": "🔄 Retry",
                # Validation
                "validation_required": "This field is required",
                "validation_min_length": "Minimum {min} characters",
                "validation_max_length": "Maximum {max} characters",
                "validation_invalid_format": "Invalid format",
                "validation_persian_only": "Persian letters only",
                "validation_english_only": "English letters only",
                "validation_alphanumeric": "Letters and numbers only",
                # System
                "system_maintenance": "🔧 System under maintenance",
                "system_error": "❌ System error",
                "system_offline": "🔌 System offline",
                "system_online": "🟢 System online",
            },
        }

    def get_text(self, key: str, language: Language, **kwargs) -> str:
        """
        Get translated text

        Args:
            key: Translation key
            language: Target language
            **kwargs: Format parameters

        Returns:
            Translated text
        """
        try:
            # Get translation for the language
            translation = self._translations.get(language.value, {}).get(key)

            # Fallback to default language if not found
            if not translation:
                translation = self._translations.get(self.default_language.value, {}).get(key)

            # Fallback to key if still not found
            if not translation:
                self.logger.warning(
                    f"Translation not found for key: {key}, language: {language.value}"
                )
                return key

            # Format with parameters if provided
            if kwargs:
                try:
                    return translation.format(**kwargs)
                except KeyError as e:
                    self.logger.warning(f"Missing format parameter {e} for key: {key}")
                    return translation

            return translation

        except Exception as e:
            self.logger.error(f"Error getting translation for key {key}: {e}")
            return key

    def get_language_texts(self, language: Language) -> dict[str, str]:
        """
        Get all texts for a language

        Args:
            language: Target language

        Returns:
            Dictionary of all texts for the language
        """
        try:
            return self._translations.get(language.value, {})
        except Exception as e:
            self.logger.error(f"Error getting language texts for {language.value}: {e}")
            return {}

    def validate_language(self, language_code: str) -> Optional[Language]:
        """
        Validate language code

        Args:
            language_code: Language code to validate

        Returns:
            Language enum or None if invalid
        """
        try:
            for lang in Language:
                if lang.value == language_code:
                    return lang
            return None
        except Exception as e:
            self.logger.error(f"Error validating language code {language_code}: {e}")
            return None

    def get_supported_languages(self) -> list:
        """
        Get list of supported languages

        Returns:
            List of supported language codes
        """
        return [lang.value for lang in Language]

    def add_translation(self, key: str, language: Language, text: str) -> bool:
        """
        Add or update translation

        Args:
            key: Translation key
            language: Target language
            text: Translation text

        Returns:
            True if successful
        """
        try:
            if language.value not in self._translations:
                self._translations[language.value] = {}

            self._translations[language.value][key] = text
            return True

        except Exception as e:
            self.logger.error(f"Error adding translation for key {key}: {e}")
            return False


# Global i18n system instance
i18n_system = I18nSystem()
