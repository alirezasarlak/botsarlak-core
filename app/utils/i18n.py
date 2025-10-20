TEXTS = {
    "welcome": "👋 سلام! به ربات آکادمی سرلک خوش اومدی.",
    "pick_major": "🪐 رشته‌ات رو انتخاب کن:",
    "enter_nickname": "✍️ یه نام مستعار بنویس:",
    "enter_phone": "📞 شماره موبایل رو وارد کن (09xxxxxxxxx):",
    "registered": "✅ ثبت‌نام کامل شد! از منوی اصلی شروع کن.",
    "invalid": "⚠️ ورودی نامعتبر بود. دوباره تلاش کن.",
    "cancelled": "❌ عملیات لغو شد.",
    "report_subject": "📚 درس رو انتخاب کن:",
    "report_topic": "📝 موضوع/منبع؟",
    "report_tests": "🔢 تعداد تست/تمرین؟ (عدد)",
    "report_notes": "🗒️ یادداشت (اختیاری):",
    "report_summary": "✅ خلاصه امروز: {dur} دقیقه | {tests} تست | امتیاز +{pts}",
    "flash_intro": "🧠 فلش‌کارت — اضافه/مرور",
    "no_cards": "هیچ فلش‌کارتی برای مرور نیست.",
    "added": "✅ اضافه شد!",
    "done": "تمام!",
    "admin_denied": "⛔️ دسترسی ادمین نداری.",
    "admin_menu": "🛠 پنل ادمین",
    "league_title": "🏆 لیگ — ۱۰ نفر برتر",
    "mission_intro": "🎯 مأموریت‌های امروز",
    "referral_intro": "🎁 لینک دعوت: {link}",
    "badge_earned": "🏅 نشان جدید گرفتی: {badge}",
}

def t(key, **kwargs):
    s = TEXTS.get(key, key)
    return s.format(**kwargs) if kwargs else s
