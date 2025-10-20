from telegram import ReplyKeyboardMarkup

def main_menu():
    kb = [
        ["📝 گزارش کار", "👤 پروفایل"],
        ["📖 فلش‌کارت‌ها", "🏆 لیگ"],
        ["🎯 مأموریت‌ها", "🎁 دعوت"],
        ["🛠 پنل ادمین"],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def major_menu(majors: list[str]):
    return ReplyKeyboardMarkup([[m] for m in majors], resize_keyboard=True)

def subject_menu(subjects: list[str]):
    return ReplyKeyboardMarkup([[s] for s in subjects], resize_keyboard=True)

def flash_menu():
    return ReplyKeyboardMarkup([["➕ اضافه کردن", "🔁 مرور"], ["🏠 خانه"]], resize_keyboard=True)

def profile_menu():
    return ReplyKeyboardMarkup([["✏️ تغییر نام مستعار"], ["🏠 خانه"]], resize_keyboard=True)
