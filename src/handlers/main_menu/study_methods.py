"""
🌌 SarlakBot v3.2.0 - Study Methods
Study-related methods for main menu handler
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.utils.logging import get_logger

logger = get_logger(__name__)


class StudyMethods:
    """Study-related methods for main menu handler"""

    @staticmethod
    async def show_study_session_start(query) -> None:
        """Show study session start"""
        text = """
📚 **شروع جلسه مطالعه**

🎯 **مراحل شروع:**
1️⃣ انتخاب موضوع مطالعه
2️⃣ تعیین مدت زمان
3️⃣ انتخاب روش مطالعه
4️⃣ شروع جلسه

**آماده‌ای برای شروع؟** 🚀
"""

        keyboard = [
            [
                InlineKeyboardButton("📖 ریاضی", callback_data="study_subject_math"),
                InlineKeyboardButton("🔬 فیزیک", callback_data="study_subject_physics"),
            ],
            [
                InlineKeyboardButton("🧪 شیمی", callback_data="study_subject_chemistry"),
                InlineKeyboardButton("🌍 زیست", callback_data="study_subject_biology"),
            ],
            [
                InlineKeyboardButton("📚 ادبیات", callback_data="study_subject_literature"),
                InlineKeyboardButton("🌐 زبان", callback_data="study_subject_english"),
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_study")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    @staticmethod
    async def show_study_content(query) -> None:
        """Show study content"""
        text = """
📖 **محتوای آموزشی**

🎯 **دسته‌بندی محتوا:**
• 📚 کتاب‌های درسی
• 🎥 ویدیوهای آموزشی
• 📝 جزوات و خلاصه‌ها
• 🔍 تست‌های موضوعی
• 💡 نکات مهم

**چه محتوایی می‌خوای؟** 📚
"""

        keyboard = [
            [
                InlineKeyboardButton("📚 کتاب‌های درسی", callback_data="content_books"),
                InlineKeyboardButton("🎥 ویدیوها", callback_data="content_videos"),
            ],
            [
                InlineKeyboardButton("📝 جزوات", callback_data="content_notes"),
                InlineKeyboardButton("🔍 تست‌ها", callback_data="content_tests"),
            ],
            [
                InlineKeyboardButton("💡 نکات", callback_data="content_tips"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="menu_study"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    @staticmethod
    async def show_study_quiz(query) -> None:
        """Show study quiz"""
        text = """
📝 **آزمون آنلاین**

🎯 **انواع آزمون:**
• ⚡ آزمون سریع (10 سوال)
• 📊 آزمون کامل (50 سوال)
• 🎯 آزمون موضوعی
• 🏆 آزمون رقابتی
• 📈 آزمون پیشرفت

**چه نوع آزمونی می‌خوای؟** 🎯
"""

        keyboard = [
            [
                InlineKeyboardButton("⚡ آزمون سریع", callback_data="quiz_quick"),
                InlineKeyboardButton("📊 آزمون کامل", callback_data="quiz_full"),
            ],
            [
                InlineKeyboardButton("🎯 آزمون موضوعی", callback_data="quiz_topic"),
                InlineKeyboardButton("🏆 آزمون رقابتی", callback_data="quiz_competitive"),
            ],
            [
                InlineKeyboardButton("📈 آزمون پیشرفت", callback_data="quiz_progress"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="menu_study"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    @staticmethod
    async def show_study_progress(query) -> None:
        """Show study progress"""
        text = """
📊 **پیشرفت مطالعه**

📈 **آمار شما:**
• ⏱️ زمان کل مطالعه: 0 ساعت
• 📚 تعداد جلسات: 0 جلسه
• 🎯 اهداف تکمیل شده: 0/5
• 🔥 Streak فعلی: 0 روز
• 🏆 سطح فعلی: مبتدی

**آمار تفصیلی:** 📊
"""

        keyboard = [
            [
                InlineKeyboardButton("📈 نمودار پیشرفت", callback_data="progress_chart"),
                InlineKeyboardButton("📊 آمار تفصیلی", callback_data="progress_detailed"),
            ],
            [
                InlineKeyboardButton("🏆 دستاوردها", callback_data="progress_achievements"),
                InlineKeyboardButton("🎯 اهداف", callback_data="progress_goals"),
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_study")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    @staticmethod
    async def show_study_goals(query) -> None:
        """Show study goals"""
        text = """
🎯 **اهداف مطالعه**

📋 **اهداف فعلی:**
• ⏰ مطالعه روزانه: تعریف نشده
• 📅 مطالعه هفتگی: تعریف نشده
• 🎯 امتیاز ماهانه: تعریف نشده
• 🏆 رتبه هدف: تعریف نشده

**اهداف خود را تنظیم کنید:** 🎯
"""

        keyboard = [
            [
                InlineKeyboardButton("⏰ هدف روزانه", callback_data="goal_daily"),
                InlineKeyboardButton("📅 هدف هفتگی", callback_data="goal_weekly"),
            ],
            [
                InlineKeyboardButton("🎯 هدف ماهانه", callback_data="goal_monthly"),
                InlineKeyboardButton("🏆 هدف رتبه", callback_data="goal_rank"),
            ],
            [
                InlineKeyboardButton("📊 پیشرفت اهداف", callback_data="goals_progress"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="menu_study"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# Global instance
study_methods = StudyMethods()
