"""
🌌 SarlakBot v3.2.0 - Input Validation System
Comprehensive input validation and sanitization
"""

import html
import re

from src.utils.logging import get_logger

logger = get_logger(__name__)


class InputValidator:
    """
    🌌 Input Validator
    Comprehensive input validation and sanitization
    """

    def __init__(self):
        self.logger = logger
        self._validation_patterns = {
            "display_name": re.compile(
                r"^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z\s]{2,50}$"
            ),
            "nickname": re.compile(r"^[a-zA-Z0-9_]{2,30}$"),
            "phone": re.compile(r"^09\d{9}$"),
            "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
            "persian_text": re.compile(
                r"^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s]+$"
            ),
            "english_text": re.compile(r"^[a-zA-Z\s]+$"),
        }

    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input to prevent XSS and injection attacks

        Args:
            text: Input text to sanitize

        Returns:
            Sanitized text
        """
        try:
            if not text:
                return ""

            # Remove leading/trailing whitespace
            text = text.strip()

            # HTML escape to prevent XSS
            text = html.escape(text)

            # Remove potential SQL injection patterns
            text = re.sub(r'[;\'"\\]', "", text)

            # Remove SQL keywords
            sql_keywords = [
                "DROP",
                "DELETE",
                "INSERT",
                "UPDATE",
                "SELECT",
                "UNION",
                "ALTER",
                "CREATE",
            ]
            for keyword in sql_keywords:
                text = re.sub(re.escape(keyword), "", text, flags=re.IGNORECASE)

            # Limit length
            text = text[:1000]

            return text

        except Exception as e:
            self.logger.error(f"Error sanitizing input: {e}")
            return ""

    def validate_display_name(self, name: str) -> tuple[bool, str]:
        """
        Validate display name

        Args:
            name: Name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not name:
                return False, "نام نمی‌تواند خالی باشد"

            if len(name) < 2:
                return False, "نام باید حداقل 2 کاراکتر باشد"

            if len(name) > 50:
                return False, "نام نمی‌تواند بیش از 50 کاراکتر باشد"

            if not self._validation_patterns["display_name"].match(name):
                return False, "نام فقط می‌تواند شامل حروف فارسی و انگلیسی باشد"

            return True, ""

        except Exception as e:
            self.logger.error(f"Error validating display name: {e}")
            return False, "خطا در اعتبارسنجی نام"

    def validate_nickname(self, nickname: str) -> tuple[bool, str]:
        """
        Validate nickname

        Args:
            nickname: Nickname to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not nickname:
                return False, "نام مستعار نمی‌تواند خالی باشد"

            if len(nickname) < 2:
                return False, "نام مستعار باید حداقل 2 کاراکتر باشد"

            if len(nickname) > 30:
                return False, "نام مستعار نمی‌تواند بیش از 30 کاراکتر باشد"

            if not self._validation_patterns["nickname"].match(nickname):
                return False, "نام مستعار فقط می‌تواند شامل حروف، اعداد و _ باشد"

            return True, ""

        except Exception as e:
            self.logger.error(f"Error validating nickname: {e}")
            return False, "خطا در اعتبارسنجی نام مستعار"

    def validate_phone(self, phone: str) -> tuple[bool, str]:
        """
        Validate phone number

        Args:
            phone: Phone number to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not phone:
                return False, "شماره تلفن نمی‌تواند خالی باشد"

            if not self._validation_patterns["phone"].match(phone):
                return False, "شماره تلفن باید با 09 شروع شود و 11 رقم باشد"

            return True, ""

        except Exception as e:
            self.logger.error(f"Error validating phone: {e}")
            return False, "خطا در اعتبارسنجی شماره تلفن"

    def validate_text_length(
        self, text: str, min_length: int = 1, max_length: int = 1000
    ) -> tuple[bool, str]:
        """
        Validate text length

        Args:
            text: Text to validate
            min_length: Minimum length
            max_length: Maximum length

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not text:
                return False, "متن نمی‌تواند خالی باشد"

            if len(text) < min_length:
                return False, f"متن باید حداقل {min_length} کاراکتر باشد"

            if len(text) > max_length:
                return False, f"متن نمی‌تواند بیش از {max_length} کاراکتر باشد"

            return True, ""

        except Exception as e:
            self.logger.error(f"Error validating text length: {e}")
            return False, "خطا در اعتبارسنجی طول متن"

    def validate_persian_text(self, text: str) -> tuple[bool, str]:
        """
        Validate Persian text

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not text:
                return False, "متن نمی‌تواند خالی باشد"

            if not self._validation_patterns["persian_text"].match(text):
                return False, "متن باید شامل حروف فارسی باشد"

            return True, ""

        except Exception as e:
            self.logger.error(f"Error validating Persian text: {e}")
            return False, "خطا در اعتبارسنجی متن فارسی"

    def validate_english_text(self, text: str) -> tuple[bool, str]:
        """
        Validate English text

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not text:
                return False, "متن نمی‌تواند خالی باشد"

            if not self._validation_patterns["english_text"].match(text):
                return False, "متن باید شامل حروف انگلیسی باشد"

            return True, ""

        except Exception as e:
            self.logger.error(f"Error validating English text: {e}")
            return False, "خطا در اعتبارسنجی متن انگلیسی"

    def validate_callback_data(self, callback_data: str) -> tuple[bool, str]:
        """
        Validate callback data

        Args:
            callback_data: Callback data to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not callback_data:
                return False, "داده‌های callback نمی‌تواند خالی باشد"

            if len(callback_data) > 64:
                return False, "داده‌های callback نمی‌تواند بیش از 64 کاراکتر باشد"

            # Check for valid callback data format
            if not re.match(r"^[a-zA-Z0-9_]+$", callback_data):
                return False, "داده‌های callback باید شامل حروف، اعداد و _ باشد"

            return True, ""

        except Exception as e:
            self.logger.error(f"Error validating callback data: {e}")
            return False, "خطا در اعتبارسنجی داده‌های callback"


# Global input validator instance
input_validator = InputValidator()
