"""
🌌 SarlakBot v3.0 - Admin Panel Texts (Persian)
Professional admin interface with cosmic theme
"""

# ==================== ADMIN WELCOME ====================

ADMIN_WELCOME = """
👑 **پنل مدیریت SarlakBot v3.0**

خوش اومدی ادمین! 🌟  
از اینجا می‌تونی کل سیستم رو مدیریت کنی ✨

**آخرین بروزرسانی:** {last_update}
**نسخه:** 3.0.0
**وضعیت:** 🟢 فعال
"""

# ==================== MAIN ADMIN MENU ====================

ADMIN_MAIN_MENU = """
🎯 **منوی اصلی مدیریت**

انتخاب کن که کدوم بخش رو مدیریت کنی:
"""

ADMIN_MENU_BUTTONS = {
    "👥 مدیریت کاربران": "admin_users",
    "📊 آمار و گزارش‌ها": "admin_stats", 
    "🔧 تنظیمات سیستم": "admin_settings",
    "📢 ارسال پیام": "admin_broadcast",
    "🗄️ مدیریت دیتابیس": "admin_database",
    "📝 لاگ‌ها": "admin_logs",
    "🔄 بروزرسانی": "admin_update",
    "❓ راهنما": "admin_help"
}

# ==================== USER MANAGEMENT ====================

USER_MANAGEMENT_MENU = """
👥 **مدیریت کاربران**

چه کاری می‌خوای انجام بدی؟
"""

USER_MANAGEMENT_BUTTONS = {
    "📋 لیست کاربران": "admin_users_list",
    "🔍 جستجوی کاربر": "admin_users_search",
    "👤 جزئیات کاربر": "admin_users_details",
    "🚫 مسدود کردن": "admin_users_ban",
    "✅ آزاد کردن": "admin_users_unban",
    "📊 آمار کاربران": "admin_users_stats",
    "🔙 بازگشت": "admin_main"
}

# ==================== USER SEARCH ====================

USER_SEARCH_MESSAGE = """
🔍 **جستجوی کاربر**

یکی از روش‌های زیر رو انتخاب کن:
"""

USER_SEARCH_BUTTONS = {
    "🆔 جستجو با ID": "admin_search_by_id",
    "👤 جستجو با نام کاربری": "admin_search_by_username",
    "📱 جستجو با شماره": "admin_search_by_phone",
    "🔙 بازگشت": "admin_users"
}

# ==================== USER DETAILS ====================

USER_DETAILS_TEMPLATE = """
👤 **جزئیات کاربر**

**🆔 شناسه:** `{user_id}`
**👤 نام کاربری:** @{username}
**📛 نام واقعی:** {real_name}
**🎯 نام مستعار:** {nickname}
**📱 شماره تلفن:** {phone}
**🎓 رشته:** {study_track}
**📚 مقطع:** {grade_band} - {grade_year}
**📅 تاریخ عضویت:** {join_date}
**🔄 آخرین فعالیت:** {last_activity}
**📊 وضعیت:** {status}
**🏆 امتیاز:** {xp_points}
**📈 سطح:** {level}
**🎯 پیشرفت:** {progress}%
"""

# ==================== STATISTICS ====================

STATS_MENU = """
📊 **آمار و گزارش‌ها**

انتخاب کن که کدوم آمار رو ببینی:
"""

STATS_BUTTONS = {
    "👥 آمار کاربران": "admin_stats_users",
    "📈 آمار فعالیت": "admin_stats_activity",
    "🎯 آمار پیشرفت": "admin_stats_progress",
    "📱 آمار دستگاه‌ها": "admin_stats_devices",
    "🌍 آمار جغرافیایی": "admin_stats_geo",
    "📊 گزارش روزانه": "admin_stats_daily",
    "🔙 بازگشت": "admin_main"
}

# ==================== BROADCAST MESSAGE ====================

BROADCAST_MENU = """
📢 **ارسال پیام همگانی**

چه نوع پیامی می‌خوای ارسال کنی؟
"""

BROADCAST_BUTTONS = {
    "📝 پیام متنی": "admin_broadcast_text",
    "🖼️ پیام با تصویر": "admin_broadcast_image",
    "📋 پیام با دکمه": "admin_broadcast_button",
    "🎯 پیام هدفمند": "admin_broadcast_targeted",
    "🔙 بازگشت": "admin_main"
}

BROADCAST_TEXT_INPUT = """
📝 **پیام متنی**

پیامت رو بنویس:
"""

BROADCAST_CONFIRM = """
📢 **تأیید ارسال**

**پیام:**
{message}

**تعداد گیرندگان:** {recipient_count}
**نوع ارسال:** {broadcast_type}

آیا مطمئنی که می‌خوای ارسال کنی؟
"""

# ==================== DATABASE MANAGEMENT ====================

DATABASE_MENU = """
🗄️ **مدیریت دیتابیس**

چه کاری می‌خوای انجام بدی؟
"""

DATABASE_BUTTONS = {
    "📊 وضعیت دیتابیس": "admin_db_status",
    "🔍 بررسی جداول": "admin_db_tables",
    "🧹 پاک‌سازی": "admin_db_cleanup",
    "💾 پشتیبان‌گیری": "admin_db_backup",
    "🔄 بازگردانی": "admin_db_restore",
    "📈 بهینه‌سازی": "admin_db_optimize",
    "🔙 بازگشت": "admin_main"
}

# ==================== SYSTEM SETTINGS ====================

SETTINGS_MENU = """
🔧 **تنظیمات سیستم**

کدوم تنظیمات رو می‌خوای تغییر بدی؟
"""

SETTINGS_BUTTONS = {
    "🎛️ تنظیمات عمومی": "admin_settings_general",
    "🔐 تنظیمات امنیتی": "admin_settings_security",
    "📢 تنظیمات اعلان‌ها": "admin_settings_notifications",
    "🎯 تنظیمات ویژگی‌ها": "admin_settings_features",
    "🌐 تنظیمات شبکه": "admin_settings_network",
    "🔙 بازگشت": "admin_main"
}

# ==================== LOGS ====================

LOGS_MENU = """
📝 **مدیریت لاگ‌ها**

چه نوع لاگی می‌خوای ببینی؟
"""

LOGS_BUTTONS = {
    "📊 لاگ‌های سیستم": "admin_logs_system",
    "👥 لاگ‌های کاربران": "admin_logs_users",
    "❌ لاگ‌های خطا": "admin_logs_errors",
    "🔍 جستجو در لاگ‌ها": "admin_logs_search",
    "📁 دانلود لاگ‌ها": "admin_logs_download",
    "🔙 بازگشت": "admin_main"
}

# ==================== SUCCESS MESSAGES ====================

SUCCESS_MESSAGES = {
    "user_banned": "✅ کاربر با موفقیت مسدود شد",
    "user_unbanned": "✅ کاربر با موفقیت آزاد شد",
    "message_sent": "✅ پیام با موفقیت ارسال شد",
    "backup_created": "✅ پشتیبان‌گیری با موفقیت انجام شد",
    "settings_updated": "✅ تنظیمات با موفقیت بروزرسانی شد",
    "database_optimized": "✅ دیتابیس با موفقیت بهینه‌سازی شد"
}

# ==================== ERROR MESSAGES ====================

ERROR_MESSAGES = {
    "user_not_found": "❌ کاربر پیدا نشد",
    "invalid_user_id": "❌ شناسه کاربر نامعتبر است",
    "permission_denied": "❌ دسترسی مجاز نیست",
    "database_error": "❌ خطا در دیتابیس",
    "message_failed": "❌ ارسال پیام ناموفق بود",
    "backup_failed": "❌ پشتیبان‌گیری ناموفق بود"
}

# ==================== CONFIRMATION MESSAGES ====================

CONFIRMATION_MESSAGES = {
    "ban_user": "⚠️ آیا مطمئنی که می‌خوای این کاربر رو مسدود کنی؟",
    "unban_user": "⚠️ آیا مطمئنی که می‌خوای این کاربر رو آزاد کنی؟",
    "delete_data": "⚠️ آیا مطمئنی که می‌خوای این داده رو حذف کنی؟",
    "send_broadcast": "⚠️ آیا مطمئنی که می‌خوای این پیام رو ارسال کنی؟"
}

# ==================== HELPER FUNCTIONS ====================

def format_user_details(user_data: dict) -> str:
    """Format user details for display"""
    return USER_DETAILS_TEMPLATE.format(
        user_id=user_data.get('user_id', 'نامشخص'),
        username=user_data.get('username', 'نامشخص'),
        real_name=user_data.get('real_name', 'نامشخص'),
        nickname=user_data.get('nickname', 'نامشخص'),
        phone=user_data.get('phone', 'نامشخص'),
        study_track=user_data.get('study_track', 'نامشخص'),
        grade_band=user_data.get('grade_band', 'نامشخص'),
        grade_year=user_data.get('grade_year', 'نامشخص'),
        join_date=user_data.get('join_date', 'نامشخص'),
        last_activity=user_data.get('last_activity', 'نامشخص'),
        status=user_data.get('status', 'نامشخص'),
        xp_points=user_data.get('xp_points', 0),
        level=user_data.get('level', 1),
        progress=user_data.get('progress', 0)
    )

def format_admin_welcome(last_update: str) -> str:
    """Format admin welcome message"""
    return ADMIN_WELCOME.format(last_update=last_update)

def get_success_message(message_type: str) -> str:
    """Get success message by type"""
    return SUCCESS_MESSAGES.get(message_type, "✅ عملیات با موفقیت انجام شد")

def get_error_message(error_type: str) -> str:
    """Get error message by type"""
    return ERROR_MESSAGES.get(error_type, "❌ خطای نامشخص")

def get_confirmation_message(confirmation_type: str) -> str:
    """Get confirmation message by type"""
    return CONFIRMATION_MESSAGES.get(confirmation_type, "⚠️ آیا مطمئنی؟")




