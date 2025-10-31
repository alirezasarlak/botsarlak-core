"""
🔥 تست فعال‌سازی خودکار CodeRabbit در پروژه botsarlak-core
این فایل صرفاً برای بررسی اتوماتیک عملکرد CodeRabbit و ارتباط با Cursor ساخته شده.
"""

from datetime import datetime
from typing import Optional


def say_hello(name: Optional[str] = "دانش‌آموز آکادمی سرلک") -> str:
    """
    تابع خوش‌آمدگویی ساده برای بررسی عملکرد CodeRabbit.
    - پارامتر: name (نام کاربر)
    - خروجی: پیام شخصی‌سازی‌شده
    """
    current_time = datetime.now().strftime("%H:%M:%S")
    return f"سلام {name} 👋 خوش اومدی به آکادمی سرلک! (ساعت: {current_time})"


def calculate_progress(study_hours: float, total_hours: float) -> float:
    """
    درصد پیشرفت مطالعه را محاسبه می‌کند.
    """
    if total_hours == 0:
        return 0.0
    return round((study_hours / total_hours) * 100, 2)


def main():
    """
    بخش اجرایی تست CodeRabbit:
    - بررسی عملکرد say_hello
    - بررسی عملکرد calculate_progress
    """
    print(say_hello("علی"))
    print(f"درصد پیشرفت امروزت: {calculate_progress(3.5, 8)}٪ ✅")


if __name__ == "__main__":
    main()
