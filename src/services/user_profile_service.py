"""
🌌 SarlakBot v3.2.0 - User Profile Service
Clean, production-ready profile management with state persistence
"""

import html
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Union

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


class Language(Enum):
    """Supported languages"""

    PERSIAN = "fa"
    ENGLISH = "en"


class StudyTrack(Enum):
    """Study tracks"""

    MATH = "ریاضی و فیزیک"
    EXPERIMENTAL = "تجربی"
    HUMANITIES = "انسانی"
    ART = "هنر"
    LANGUAGE = "زبان"
    TECHNICAL = "فنی و حرفه‌ای"


class GradeLevel(Enum):
    """Grade levels"""

    GRADE_10 = "دهم"
    GRADE_11 = "یازدهم"
    GRADE_12 = "دوازدهم"
    GRADUATE = "فارغ‌التحصیل"
    STUDENT = "دانشجو"


@dataclass
class OnboardingState:
    """Onboarding state container"""

    user_id: int
    language: Optional[Language] = None
    display_name: Optional[str] = None
    nickname: Optional[str] = None
    study_track: Optional[StudyTrack] = None
    grade_level: Optional[GradeLevel] = None
    target_year: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ProfileData:
    """Complete profile data"""

    user_id: int
    language: Language
    display_name: str
    nickname: str
    study_track: StudyTrack
    grade_level: GradeLevel
    target_year: int
    is_completed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserProfileService:
    """
    🌌 User Profile Service
    Clean, production-ready profile management with state persistence
    """

    def __init__(self):
        self.logger = logger
        self._validation_patterns = {
            "display_name": re.compile(
                r"^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z\s]{2,50}$"
            ),
            "nickname": re.compile(r"^[a-zA-Z0-9_]{2,30}$"),
            "phone": re.compile(r"^09\d{9}$"),
        }

    async def get_onboarding_state(self, user_id: int) -> Optional[OnboardingState]:
        """Get current onboarding state for user"""
        try:
            query = """
                SELECT * FROM onboarding_states
                WHERE user_id = $1
            """

            result = await db_manager.fetch_one(query, user_id)

            if result:
                return OnboardingState(
                    user_id=result["user_id"],
                    language=Language(result["language"]) if result["language"] else None,
                    display_name=result["display_name"],
                    nickname=result["nickname"],
                    study_track=(
                        StudyTrack(result["study_track"]) if result["study_track"] else None
                    ),
                    grade_level=(
                        GradeLevel(result["grade_level"]) if result["grade_level"] else None
                    ),
                    target_year=result["target_year"],
                    created_at=result["created_at"],
                    updated_at=result["updated_at"],
                )

            return None

        except Exception as e:
            self.logger.error(f"Failed to get onboarding state for user {user_id}: {e}")
            return None

    async def save_onboarding_state(self, state: OnboardingState) -> bool:
        """Save onboarding state to database"""
        try:
            query = """
                INSERT INTO onboarding_states (
                    user_id, language, display_name, nickname, study_track,
                    grade_level, target_year, created_at, updated_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, NOW(), NOW()
                )
                ON CONFLICT (user_id) DO UPDATE SET
                    language = EXCLUDED.language,
                    display_name = EXCLUDED.display_name,
                    nickname = EXCLUDED.nickname,
                    study_track = EXCLUDED.study_track,
                    grade_level = EXCLUDED.grade_level,
                    target_year = EXCLUDED.target_year,
                    updated_at = NOW()
            """

            await db_manager.execute(
                query,
                state.user_id,
                state.language.value if state.language else None,
                state.display_name,
                state.nickname,
                state.study_track.value if state.study_track else None,
                state.grade_level.value if state.grade_level else None,
                state.target_year,
            )

            self.logger.info(f"Onboarding state saved for user {state.user_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save onboarding state for user {state.user_id}: {e}")
            return False

    async def complete_profile(self, user_id: int, profile_data: ProfileData) -> bool:
        """Complete user profile and save to users table"""
        try:
            # Save to users table
            query = """
                UPDATE users SET
                    language_code = $2,
                    real_name = $3,
                    nickname = $4,
                    study_track = $5,
                    grade_band = $6,
                    grade_year = $7,
                    onboarding_completed = TRUE,
                    updated_at = NOW()
                WHERE user_id = $1
            """

            await db_manager.execute(
                query,
                user_id,
                profile_data.language.value,
                profile_data.display_name,
                profile_data.nickname,
                profile_data.study_track.value,
                profile_data.grade_level.value,
                profile_data.target_year,
            )

            # Create profile in user_profiles table
            await self._create_user_profile(profile_data)

            # Clean up onboarding state
            await self._cleanup_onboarding_state(user_id)

            self.logger.info(f"Profile completed for user {user_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to complete profile for user {user_id}: {e}")
            return False

    async def get_user_profile(self, user_id: int) -> Optional[ProfileData]:
        """Get complete user profile"""
        try:
            query = """
                SELECT * FROM users
                WHERE user_id = $1 AND onboarding_completed = TRUE
            """

            result = await db_manager.fetch_one(query, user_id)

            if result:
                return ProfileData(
                    user_id=result["user_id"],
                    language=Language(result["language_code"]),
                    display_name=result["real_name"],
                    nickname=result["nickname"],
                    study_track=StudyTrack(result["study_track"]),
                    grade_level=GradeLevel(result["grade_band"]),
                    target_year=result["grade_year"],
                    is_completed=True,
                    created_at=result["created_at"],
                    updated_at=result["updated_at"],
                )

            return None

        except Exception as e:
            self.logger.error(f"Failed to get user profile for user {user_id}: {e}")
            return None

    def validate_display_name(self, name: str) -> tuple[bool, str]:
        """Validate display name"""
        try:
            if not name or not name.strip():
                return False, "نام نمی‌تواند خالی باشد"

            name = name.strip()

            if len(name) < 2 or len(name) > 50:
                return False, "نام باید بین 2 تا 50 کاراکتر باشد"

            if not self._validation_patterns["display_name"].match(name):
                return False, "نام فقط می‌تواند شامل حروف فارسی و انگلیسی باشد"

            return True, "معتبر"

        except Exception as e:
            self.logger.error(f"Error validating display name: {e}")
            return False, "خطا در اعتبارسنجی نام"

    def validate_nickname(self, nickname: str) -> tuple[bool, str]:
        """Validate nickname"""
        try:
            if not nickname or not nickname.strip():
                return False, "نام مستعار نمی‌تواند خالی باشد"

            nickname = nickname.strip()

            if len(nickname) < 2 or len(nickname) > 30:
                return False, "نام مستعار باید بین 2 تا 30 کاراکتر باشد"

            if not self._validation_patterns["nickname"].match(nickname):
                return False, "نام مستعار فقط می‌تواند شامل حروف، اعداد و _ باشد"

            return True, "معتبر"

        except Exception as e:
            self.logger.error(f"Error validating nickname: {e}")
            return False, "خطا در اعتبارسنجی نام مستعار"

    def sanitize_input(self, text: str) -> str:
        """Sanitize user input"""
        try:
            # HTML escape
            text = html.escape(text)

            # Remove extra whitespace
            text = " ".join(text.split())

            # Remove potentially dangerous characters
            text = re.sub(r'[<>"\']', "", text)

            return text.strip()

        except Exception as e:
            self.logger.error(f"Error sanitizing input: {e}")
            return ""

    def get_language_texts(self, language: Language) -> dict[str, str]:
        """Get localized texts for language"""
        texts = {
            Language.PERSIAN: {
                "welcome": "🌟 خوش آمدید به آکادمی سرلک!",
                "select_language": "🌍 لطفاً زبان خود را انتخاب کنید:",
                "enter_name": "👤 لطفاً نام نمایشی خود را وارد کنید:",
                "enter_nickname": "🏷️ لطفاً نام مستعار خود را وارد کنید:",
                "select_grade": "📚 لطفاً مقطع تحصیلی خود را انتخاب کنید:",
                "select_track": "🎯 لطفاً رشته تحصیلی خود را انتخاب کنید:",
                "select_year": "📅 لطفاً سال هدف کنکور خود را انتخاب کنید:",
                "confirm_profile": "✅ لطفاً اطلاعات خود را بررسی کنید:",
                "profile_completed": "🎉 پروفایل شما با موفقیت تکمیل شد!",
                "invalid_input": "❌ ورودی نامعتبر. لطفاً دوباره تلاش کنید.",
                "cancel_onboarding": "❌ فرآیند ثبت‌نام لغو شد.",
                "edit_profile": "✏️ ویرایش پروفایل",
                "back_to_menu": "🔙 بازگشت به منو",
            },
            Language.ENGLISH: {
                "welcome": "🌟 Welcome to Sarlak Academy!",
                "select_language": "🌍 Please select your language:",
                "enter_name": "👤 Please enter your display name:",
                "enter_nickname": "🏷️ Please enter your nickname:",
                "select_grade": "📚 Please select your grade level:",
                "select_track": "🎯 Please select your study track:",
                "select_year": "📅 Please select your target year:",
                "confirm_profile": "✅ Please review your information:",
                "profile_completed": "🎉 Your profile has been completed successfully!",
                "invalid_input": "❌ Invalid input. Please try again.",
                "cancel_onboarding": "❌ Onboarding process cancelled.",
                "edit_profile": "✏️ Edit Profile",
                "back_to_menu": "🔙 Back to Menu",
            },
        }

        return texts.get(language, texts[Language.PERSIAN])

    async def _create_user_profile(self, profile_data: ProfileData) -> None:
        """Create user profile in user_profiles table"""
        try:
            query = """
                INSERT INTO user_profiles (
                    user_id, display_name, nickname, study_track, grade_level,
                    grade_year, privacy_level, is_public, show_statistics,
                    show_achievements, show_streak
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11
                )
            """

            await db_manager.execute(
                query,
                profile_data.user_id,
                profile_data.display_name,
                profile_data.nickname,
                profile_data.study_track.value,
                profile_data.grade_level.value,
                profile_data.target_year,
                "friends_only",
                False,
                True,
                True,
                True,
            )

        except Exception as e:
            self.logger.error(f"Failed to create user profile: {e}")

    async def _cleanup_onboarding_state(self, user_id: int) -> None:
        """Clean up onboarding state after completion"""
        try:
            query = "DELETE FROM onboarding_states WHERE user_id = $1"
            await db_manager.execute(query, user_id)

        except Exception as e:
            self.logger.error(f"Failed to cleanup onboarding state for user {user_id}: {e}")


# Global service instance
user_profile_service = UserProfileService()
