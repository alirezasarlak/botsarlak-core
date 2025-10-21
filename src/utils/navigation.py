"""
🌌 SarlakBot v3.0 - Navigation Utilities
Dynamic keyboard and navigation system for Gen-Z cosmic journey
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Optional, Any
from src.utils.logging import get_logger

logger = get_logger(__name__)

class NavigationKeyboard:
    """
    🌌 Dynamic Navigation Keyboard System
    Creates context-aware keyboards for different sections
    """
    
    @staticmethod
    def create_main_menu_keyboard() -> InlineKeyboardMarkup:
        """Create main universe map keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🎯 دعوت دوستان", callback_data="referral_main")
            ],
            [
                InlineKeyboardButton("🌕 گزارش کار", callback_data="menu_reports"),
                InlineKeyboardButton("🪐 پروفایل", callback_data="menu_profile")
            ],
            [
                InlineKeyboardButton("🏆 لیگ‌ها", callback_data="menu_competition"),
                InlineKeyboardButton("🤖 ردیابی خودکار", callback_data="menu_auto_tracking")
            ],
            [
                InlineKeyboardButton("🌟 انگیزه", callback_data="menu_motivation"),
                InlineKeyboardButton("🛍️ فروشگاه", callback_data="menu_store")
            ],
            [
                InlineKeyboardButton("🧭 قطب‌نما", callback_data="menu_compass"),
                InlineKeyboardButton("⚙️ تنظیمات", callback_data="menu_settings")
            ],
            [
                InlineKeyboardButton("❓ راهنما", callback_data="menu_help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_back_home_keyboard(back_callback: str = "back_to_main") -> InlineKeyboardMarkup:
        """Create back and home navigation keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data=back_callback),
                InlineKeyboardButton("🏠 خانه", callback_data="go_home")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_section_keyboard(section: str, options: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Create dynamic keyboard for specific sections"""
        keyboard = []
        
        # Add section-specific buttons
        for option in options:
            if option.get("type") == "single":
                keyboard.append([InlineKeyboardButton(
                    option["text"], 
                    callback_data=option["callback"]
                )])
            elif option.get("type") == "row":
                row = []
                for btn in option["buttons"]:
                    row.append(InlineKeyboardButton(
                        btn["text"], 
                        callback_data=btn["callback"]
                    ))
                keyboard.append(row)
        
        # Add navigation buttons
        keyboard.append([
            InlineKeyboardButton("🔙 بازگشت", callback_data=f"back_to_{section}"),
            InlineKeyboardButton("🏠 خانه", callback_data="go_home")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_yes_no_keyboard(yes_callback: str, no_callback: str, back_callback: str = "back_to_main") -> InlineKeyboardMarkup:
        """Create yes/no confirmation keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("✅ بله", callback_data=yes_callback),
                InlineKeyboardButton("❌ خیر", callback_data=no_callback)
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data=back_callback),
                InlineKeyboardButton("🏠 خانه", callback_data="go_home")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_pagination_keyboard(
        items: List[Dict[str, Any]], 
        page: int = 0, 
        items_per_page: int = 5,
        callback_prefix: str = "item"
    ) -> InlineKeyboardMarkup:
        """Create paginated keyboard for lists"""
        keyboard = []
        
        # Calculate pagination
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_items = items[start_idx:end_idx]
        
        # Add items
        for item in page_items:
            keyboard.append([InlineKeyboardButton(
                item["text"], 
                callback_data=f"{callback_prefix}_{item['id']}"
            )])
        
        # Add pagination controls
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"page_{page-1}"))
        
        if end_idx < len(items):
            nav_buttons.append(InlineKeyboardButton("➡️ بعدی", callback_data=f"page_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Add navigation
        keyboard.append([
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_list"),
            InlineKeyboardButton("🏠 خانه", callback_data="go_home")
        ])
        
        return InlineKeyboardMarkup(keyboard)

class NavigationHandler:
    """
    🌌 Navigation Handler
    Handles navigation callbacks and state management
    """
    
    def __init__(self):
        self.logger = logger
        self.current_section = {}
    
    async def handle_navigation_callback(self, update, context, callback_data: str) -> bool:
        """
        Handle navigation callbacks
        Returns True if handled, False if not
        """
        try:
            if callback_data == "go_home":
                await self._go_home(update, context)
                return True
            
            elif callback_data.startswith("back_to_"):
                section = callback_data.replace("back_to_", "")
                await self._go_back(update, context, section)
                return True
            
            elif callback_data.startswith("menu_"):
                section = callback_data.replace("menu_", "")
                await self._go_to_section(update, context, section)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Navigation callback failed: {e}")
            return False
    
    async def _go_home(self, update, context) -> None:
        """Go to main menu"""
        query = update.callback_query
        await query.answer()
        
        welcome_text = """
🌌 **نقشه کیهانی آکادمی سرلک** ✨

خوش اومدی به مرکز کنترل سفر کیهانی‌ات! 🚀
از اینجا می‌تونی به تمام بخش‌ها دسترسی داشته باشی:

**سیاره‌های سفرت:**
🌕 **گزارش کار** - پیگیری مطالعه و پیشرفت
🪐 **پروفایل** - پروفایل شخصی و آمار
🤖 **پرسش و پاسخ** - دستیار هوشمند شخصی‌سازی شده
🌟 **انگیزه** - نقل‌قول‌ها و مأموریت‌های روزانه
☄️ **رقابت** - جدول امتیازات و چالش‌ها
🛍️ **فروشگاه** - خرید دوره‌ها و کتاب‌ها
🧭 **قطب‌نما** - تخمین رتبه و راهنمای دانشگاه
"""
        
        keyboard = NavigationKeyboard.create_main_menu_keyboard()
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        self.logger.info(f"User {update.effective_user.id} navigated to home")
    
    async def _go_back(self, update, context, section: str) -> None:
        """Go back to previous section"""
        query = update.callback_query
        await query.answer()
        
        # For now, just go to home. Later this will be more sophisticated
        await self._go_home(update, context)
        
        self.logger.info(f"User {update.effective_user.id} went back from {section}")
    
    async def _go_to_section(self, update, context, section: str) -> None:
        """Go to specific section"""
        query = update.callback_query
        await query.answer()
        
        # Section-specific handling
        if section == "reports":
            await self._show_reports_section(update, context)
        elif section == "profile":
            await self._show_profile_section(update, context)
        elif section == "motivation":
            await self._show_motivation_section(update, context)
        elif section == "competition":
            await self._show_competition_section(update, context)
        elif section == "store":
            await self._show_store_section(update, context)
        elif section == "compass":
            await self._show_compass_section(update, context)
        elif section == "settings":
            await self._show_settings_section(update, context)
        elif section == "help":
            await self._show_help_section(update, context)
        else:
            await query.edit_message_text(
                "🚧 این بخش هنوز آماده نیست!\n\nبه زودی اضافه می‌شه! ✨",
                reply_markup=NavigationKeyboard.create_back_home_keyboard(),
                parse_mode='Markdown'
            )
        
        self.logger.info(f"User {update.effective_user.id} navigated to {section}")
    
    async def _show_reports_section(self, update, context) -> None:
        """Show reports section"""
        query = update.callback_query
        
        text = """
🌕 **گزارش کار** - پیگیری مطالعه

اینجا می‌تونی:
• گزارش مطالعه روزانه ثبت کنی
• پیشرفتت رو ببینی
• آمار مطالعه‌ات رو چک کنی
• هدف‌هایت رو تنظیم کنی

**آماده‌ای برای شروع؟** 🚀
"""
        
        options = [
            {"type": "single", "text": "📝 ثبت گزارش جدید", "callback": "report_new"},
            {"type": "single", "text": "📊 آمار مطالعه", "callback": "report_stats"},
            {"type": "single", "text": "🎯 تنظیم اهداف", "callback": "report_goals"}
        ]
        
        keyboard = NavigationKeyboard.create_section_keyboard("reports", options)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def _show_profile_section(self, update, context) -> None:
        """Show profile section"""
        query = update.callback_query
        
        text = """
🪐 **پروفایل شخصی** - مرکز اطلاعاتت

اینجا می‌تونی:
• اطلاعات شخصی‌ت رو ببینی
• آمار کلی‌ت رو چک کنی
• تنظیمات پروفایل رو تغییر بدی
• پیشرفتت رو دنبال کنی

**بیا ببینیم چه خبره!** ✨
"""
        
        options = [
            {"type": "single", "text": "👤 اطلاعات شخصی", "callback": "profile_info"},
            {"type": "single", "text": "📈 آمار کلی", "callback": "profile_stats"},
            {"type": "single", "text": "⚙️ تنظیمات", "callback": "profile_settings"}
        ]
        
        keyboard = NavigationKeyboard.create_section_keyboard("profile", options)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def _show_motivation_section(self, update, context) -> None:
        """Show motivation section"""
        query = update.callback_query
        
        text = """
🌟 **انگیزه** - سوخت سفر کیهانی‌ات

اینجا می‌تونی:
• نقل‌قول‌های انگیزشی ببینی
• مأموریت‌های روزانه دریافت کنی
• چالش‌های انگیزشی انجام بدی
• انگیزه‌ت رو بالا نگه داری

**بیا انگیزه‌ت رو شارژ کنیم!** ⚡
"""
        
        options = [
            {"type": "single", "text": "💬 نقل‌قول روزانه", "callback": "motivation_quote"},
            {"type": "single", "text": "🎯 مأموریت روزانه", "callback": "motivation_mission"},
            {"type": "single", "text": "🏆 چالش‌ها", "callback": "motivation_challenges"}
        ]
        
        keyboard = NavigationKeyboard.create_section_keyboard("motivation", options)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def _show_competition_section(self, update, context) -> None:
        """Show competition section"""
        query = update.callback_query
        
        text = """
☄️ **رقابت** - جنگ ستاره‌ای کنکور

اینجا می‌تونی:
• با دوستانت رقابت کنی
• در جدول امتیازات شرکت کنی
• چالش‌های گروهی انجام بدی
• رتبه‌ت رو ببینی

**آماده‌ای برای جنگ؟** ⚔️
"""
        
        options = [
            {"type": "single", "text": "🏆 جدول امتیازات", "callback": "competition_leaderboard"},
            {"type": "single", "text": "👥 رقبا", "callback": "competition_rivals"},
            {"type": "single", "text": "🎮 چالش‌ها", "callback": "competition_challenges"}
        ]
        
        keyboard = NavigationKeyboard.create_section_keyboard("competition", options)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def _show_store_section(self, update, context) -> None:
        """Show store section"""
        query = update.callback_query
        
        text = """
🛍️ **فروشگاه** - بازار کیهانی

اینجا می‌تونی:
• دوره‌های آموزشی ببینی
• کتاب‌ها و منابع خریداری کنی
• پکیج‌های ویژه دریافت کنی
• تخفیف‌های ویژه ببینی

**بیا خرید کنیم!** 🛒
"""
        
        options = [
            {"type": "single", "text": "📚 دوره‌ها", "callback": "store_courses"},
            {"type": "single", "text": "📖 کتاب‌ها", "callback": "store_books"},
            {"type": "single", "text": "🎁 پکیج‌ها", "callback": "store_packages"}
        ]
        
        keyboard = NavigationKeyboard.create_section_keyboard("store", options)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def _show_compass_section(self, update, context) -> None:
        """Show compass section"""
        query = update.callback_query
        
        text = """
🧭 **قطب‌نما** - راهنمای کیهانی

اینجا می‌تونی:
• رتبه‌ت رو تخمین بزنی
• دانشگاه‌های مناسب رو ببینی
• مسیر تحصیلی‌ت رو برنامه‌ریزی کنی
• مشاوره تحصیلی دریافت کنی

**بیا مسیرت رو پیدا کنیم!** 🗺️
"""
        
        options = [
            {"type": "single", "text": "🎯 تخمین رتبه", "callback": "compass_rank"},
            {"type": "single", "text": "🏫 دانشگاه‌ها", "callback": "compass_universities"},
            {"type": "single", "text": "📋 برنامه‌ریزی", "callback": "compass_planning"}
        ]
        
        keyboard = NavigationKeyboard.create_section_keyboard("compass", options)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def _show_settings_section(self, update, context) -> None:
        """Show settings section"""
        query = update.callback_query
        
        text = """
⚙️ **تنظیمات** - کنترل مرکزی

اینجا می‌تونی:
• تنظیمات شخصی‌ت رو تغییر بدی
• اعلان‌ها رو مدیریت کنی
• حریم خصوصی‌ت رو تنظیم کنی
• حساب کاربری‌ت رو مدیریت کنی

**بیا تنظیماتت رو شخصی‌سازی کنیم!** 🔧
"""
        
        options = [
            {"type": "single", "text": "🔔 اعلان‌ها", "callback": "settings_notifications"},
            {"type": "single", "text": "🔒 حریم خصوصی", "callback": "settings_privacy"},
            {"type": "single", "text": "👤 حساب کاربری", "callback": "settings_account"}
        ]
        
        keyboard = NavigationKeyboard.create_section_keyboard("settings", options)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    
    async def _show_help_section(self, update, context) -> None:
        """Show help section"""
        query = update.callback_query
        
        text = """
❓ **راهنما** - مرکز کمک

اینجا می‌تونی:
• راهنمای استفاده از ربات رو ببینی
• سوالات متداول رو چک کنی
• با پشتیبانی تماس بگیری
• پیشنهاداتت رو ارسال کنی

**چطور می‌تونم کمکت کنم؟** 🤝
"""
        
        options = [
            {"type": "single", "text": "📖 راهنمای کامل", "callback": "help_guide"},
            {"type": "single", "text": "❓ سوالات متداول", "callback": "help_faq"},
            {"type": "single", "text": "💬 پشتیبانی", "callback": "help_support"}
        ]
        
        keyboard = NavigationKeyboard.create_section_keyboard("help", options)
        
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

# Global navigation handler instance
navigation_handler = NavigationHandler()

def create_back_button(back_callback: str = "back_to_main") -> InlineKeyboardMarkup:
    """Create a simple back button"""
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data=back_callback)]
    ]
    return InlineKeyboardMarkup(keyboard)




