"""
🌌 SarlakBot v3.0 - Onboarding Texts (Persian)
Gen-Z cosmic journey messaging with emotional depth
"""

# ==================== INTRO MESSAGES ====================

INTRO_MESSAGE = """
🌌 خوش اومدی به دنیای آکادمی سرلک!  

من یه هوش مصنوعی‌ام که با کمک تیم سرلک هر روز کامل‌تر می‌شم.  
قراره با هم یه سفر خفن به سمت موفقیت کنکور داشته باشیم 🚀  

بهم فرصت بده تا بهتر بشناسمت و مسیرت رو مخصوص خودت بسازم 🌱
"""

INTRO_BUTTONS = {
    "📣 کانال تلگرام": "telegram_channel",
    "▶️ یوتیوب": "youtube",
    "📸 اینستاگرام": "instagram", 
    "🌐 سایت": "website",
    "🚀 شروع سفر": "go_start"
}

# ==================== MEMBERSHIP CHECK ====================

MEMBERSHIP_MESSAGE = """
اولین مأموریتت آسونه 😎  

عضو کانال آکادمی شو تا دروازه‌ی سفر برات باز شه ✨  
اونجا هر روز نکته، برنامه و سورپرایز داریم 🎁
"""

MEMBERSHIP_BUTTONS = {
    "عضویت در کانال 📣": "join_channel",
    "عضو شدم ✅": "recheck_membership"
}

# ==================== NAME COLLECTION ====================

NAME_MESSAGE = """
خب رفیق سفرم... اسمت چیه؟ 🌟  

(فقط خودت و من می‌بینیمش، مطمئن باش)
"""

NAME_ERROR_MESSAGE = """
اسم مناسب نیست 🚫  

یه اسم محترمانه‌تر انتخاب کن.
"""

# ==================== NICKNAME COLLECTION ====================

NICKNAME_MESSAGE = """
حالا یه اسم باحال انتخاب کن که بقیه تو رقابت‌ها با اون بشناسن 😎  

باید خاص، محترمانه و کوتاه باشه ✨  
یادت باشه فقط ۳ بار می‌تونی تغییرش بدی!
"""

NICKNAME_ERRORS = {
    "taken": "این اسم قبلاً گرفته شده 🔁",
    "invalid": "اسم مناسب نیست 🚫 یه اسم محترمانه‌تر انتخاب کن.",
    "too_short": "اسم خیلی کوتاهه 📏 حداقل ۲ کاراکتر باشه.",
    "too_long": "اسم خیلی طولانیه 📏 حداکثر ۲۰ کاراکتر باشه.",
    "no_changes": "دیگه نمی‌تونی اسمت رو تغییر بدی 🚫"
}

# ==================== STUDY TRACK SELECTION ====================

STUDY_TRACK_MESSAGE = """
رشته‌ت چیه تا مسیر مخصوص خودت رو برات فعال کنم؟ 🎯
"""

STUDY_TRACK_BUTTONS = {
    "تجربی": "track_experimental",
    "ریاضی": "track_mathematics", 
    "انسانی": "track_humanities",
    "زبان": "track_language"
}

# ==================== GRADE BAND SELECTION ====================

GRADE_BAND_MESSAGE = """
مقطع تحصیلیت چیه؟ 🌱
"""

GRADE_BAND_BUTTONS = {
    "متوسطه اول": "band_middle",
    "متوسطه دوم": "band_high"
}

# ==================== GRADE YEAR SELECTION ====================

GRADE_YEAR_MIDDLE_MESSAGE = """
پایه تحصیلیت چیه؟ 📚
"""

GRADE_YEAR_HIGH_MESSAGE = """
پایه تحصیلیت چیه؟ 🎓
"""

GRADE_YEAR_BUTTONS = {
    "middle": {
        "هفتم": "year_7",
        "هشتم": "year_8", 
        "نهم": "year_9"
    },
    "high": {
        "دهم": "year_10",
        "یازدهم": "year_11",
        "دوازدهم": "year_12"
    }
}

# ==================== PHONE COLLECTION ====================

PHONE_MESSAGE = """
می‌خوای شمارتو بدی تا برای قرعه‌کشی‌هامون یا ارتباط مستقیم استفاده کنیم؟ 📱  

می‌تونی رد کنی و بعداً از پروفایل اضافه‌ش کنی.
"""

PHONE_BUTTONS = {
    "ارسال شماره 📱": "send_phone",
    "بعداً کامل می‌کنم ⏭️": "skip_phone"
}

# ==================== FINAL WELCOME ====================

WELCOME_MESSAGE = """
🎉 خوش اومدی {nickname}!  

از همین الان من همراهتم تو مسیر کنکور 🚀  
هر روز که ازم استفاده کنی، بیشتر می‌شناسمت و دقیق‌تر راهنماییت می‌کنم 💫  

بزن بریم به اولین بخش سفرمون 🌍
"""

# ==================== ERROR MESSAGES ====================

ERROR_MESSAGES = {
    "database_error": "مشکلی پیش اومده 🔧 لطفاً دوباره تلاش کن.",
    "validation_error": "اطلاعات وارد شده صحیح نیست 📝 دوباره تلاش کن.",
    "timeout_error": "زمان تمام شد ⏰ دوباره شروع کن.",
    "unknown_error": "یه مشکل غیرمنتظره پیش اومده 🤔 لطفاً دوباره تلاش کن."
}

# ==================== SUCCESS MESSAGES ====================

SUCCESS_MESSAGES = {
    "name_saved": "اسمت ذخیره شد ✅",
    "nickname_saved": "اسم باحالت ذخیره شد ✅",
    "track_saved": "رشته‌ت انتخاب شد ✅",
    "grade_saved": "مقطع تحصیلیت ثبت شد ✅",
    "phone_saved": "شماره‌ت ذخیره شد ✅",
    "onboarding_complete": "سفرت شروع شد! 🚀"
}

# ==================== HELPER FUNCTIONS ====================

def get_grade_year_buttons(grade_band: str) -> dict:
    """Get grade year buttons based on grade band"""
    return GRADE_YEAR_BUTTONS.get(grade_band, {})

def format_welcome_message(nickname: str) -> str:
    """Format welcome message with nickname"""
    return WELCOME_MESSAGE.format(nickname=nickname)

def get_error_message(error_type: str) -> str:
    """Get error message by type"""
    return ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["unknown_error"])

def get_success_message(success_type: str) -> str:
    """Get success message by type"""
    return SUCCESS_MESSAGES.get(success_type, "✅ انجام شد!")

# ==================== ONBOARDING_TEXTS DICTIONARY ====================

ONBOARDING_TEXTS = {
    "intro": INTRO_MESSAGE,
    "intro_buttons": INTRO_BUTTONS,
    "membership_check": MEMBERSHIP_MESSAGE,
    "membership_buttons": MEMBERSHIP_BUTTONS,
    "ask_real_name": NAME_MESSAGE,
    "ask_nickname": NICKNAME_MESSAGE,
    "nickname_taken_error": NICKNAME_ERRORS["taken"],
    "nickname_invalid_error": NICKNAME_ERRORS["invalid"],
    "ask_study_track": STUDY_TRACK_MESSAGE,
    "study_track_buttons": {
        "تجربی": "تجربی",
        "ریاضی": "ریاضی",
        "انسانی": "انسانی",
        "زبان": "زبان"
    },
    "ask_grade_band": GRADE_BAND_MESSAGE,
    "grade_band_buttons": {
        "متوسطه اول": "متوسطه اول",
        "متوسطه دوم": "متوسطه دوم"
    },
    "ask_grade_year_motevasete_aval": GRADE_YEAR_MIDDLE_MESSAGE,
    "grade_year_buttons_motevasete_aval": {
        "هفتم": "هفتم",
        "هشتم": "هشتم",
        "نهم": "نهم"
    },
    "ask_grade_year_motevasete_dovom": GRADE_YEAR_HIGH_MESSAGE,
    "grade_year_buttons_motevasete_dovom": {
        "دهم": "دهم",
        "یازدهم": "یازدهم",
        "دوازدهم": "دوازدهم"
    },
    "ask_phone": PHONE_MESSAGE,
    "phone_buttons": {
        "send_phone": "ارسال شماره 📱",
        "skip_phone": "بعداً کامل می‌کنم ⏭️"
    },
    "final_welcome": WELCOME_MESSAGE,
    "main_menu_greeting": "خوش اومدی {nickname}! آماده‌ای برای مرحله‌ی بعد؟ 🚀"
}
