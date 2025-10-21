import re
from typing import Dict, List

STATE_START_MAJOR = 10
STATE_START_NICKNAME = 11
STATE_START_PHONE = 12

STATE_PROFILE_MENU = 20
STATE_PROFILE_NICKNAME = 21

STATE_REPORT_SUBJECT = 30
STATE_REPORT_TOPIC = 31
STATE_REPORT_TESTS = 32
STATE_REPORT_NOTES = 33

STATE_FLASHCARD_MENU = 40
STATE_FLASHCARD_SUBJECT = 41
STATE_FLASHCARD_QUESTION = 42
STATE_FLASHCARD_ANSWER = 43
STATE_FLASHCARD_REVIEW = 44
STATE_FLASHCARD_EVALUATE = 45

STATE_LEAGUE_MENU = 50
STATE_MISSIONS_MENU = 60
STATE_REFERRALS_MENU = 70
STATE_ADMIN_MENU = 90

MAJOR_SUBJECTS: Dict[str, List[str]] = {
    "تجربی": ["زیست", "ریاضی", "فیزیک", "شیمی", "ادبیات", "دینی", "عربی", "زبان"],
    "ریاضی": ["ریاضی", "فیزیک", "شیمی", "ادبیات", "دینی", "عربی", "زبان"],
    "انسانی": [
        "ادبیات",
        "عربی",
        "فلسفه",
        "منطق",
        "دینی",
        "اقتصاد",
        "تاریخ",
        "جغرافیا",
        "روان‌شناسی",
    ],
    "هنر": [
        "طراحی",
        "تاریخ هنر",
        "خلاقیت تصویری",
        "ترسیم فنی",
        "ادبیات",
        "دینی",
        "زبان",
    ],
}


def _zwsp():
    return r"[\\u200c\\s]*"


def _esc(s: str) -> str:
    e = re.escape(s)
    return e.replace("\\ ", _zwsp())


def btn_rx(label: str, emoji: str = "", alts: tuple = ()):
    parts = []
    L = _esc(label)
    if emoji:
        E = _esc(emoji)
        parts += [rf"{E}{_zwsp()}{L}", rf"{L}{_zwsp()}{E}"]
    parts.append(L)
    for a in alts:
        A = _esc(a)
        if emoji:
            parts += [rf"{E}{_zwsp()}{A}", rf"{A}{_zwsp()}{E}"]
        parts.append(A)
    return r"^(" + "|".join(parts) + r")$"


def back_home_rx():
    return btn_rx("بازگشت", "🔙")[:-1] + "|" + btn_rx("خانه", "🏠")[1:]
