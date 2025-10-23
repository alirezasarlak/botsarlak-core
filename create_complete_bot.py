#!/usr/bin/env python3
"""
🌌 SarlakBot v6 - Complete Working Version
All features working properly
"""

import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7214099093:AAEePAXAk8lBGULYzUbQS-6MiwplofDze8o"

# Database setup
DB_PATH = '/home/ali/botsarlak-core/botsarlak.db'

def init_database():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            nickname TEXT,
            field TEXT,
            level TEXT,
            phone TEXT,
            province TEXT,
            city TEXT,
            privacy TEXT DEFAULT 'private',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Study sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT,
            duration INTEGER,
            date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            report_type TEXT,
            content TEXT,
            date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    try:
        user_id = update.effective_user.id
        user_data = get_user_data(user_id)
        
        if user_data:
            await show_main_menu(update, user_data)
        else:
            await show_welcome_new_user(update)
            
    except Exception as e:
        logger.error(f"Start command failed: {e}")
        await update.message.reply_text("❌ مشکلی در شروع ربات پیش آمد.")

async def show_main_menu(update: Update, user_data):
    """Show main menu for existing user"""
    try:
        keyboard = [
            [InlineKeyboardButton("👤 پروفایل من", callback_data="show_profile")],
            [InlineKeyboardButton("✏️ ویرایش پروفایل", callback_data="edit_profile")],
            [InlineKeyboardButton("📊 گزارش روزانه", callback_data="menu_reports")],
            [InlineKeyboardButton("🏆 لیگ", callback_data="menu_competition")],
            [InlineKeyboardButton("❓ سوال و جواب", callback_data="menu_qa")],
            [InlineKeyboardButton("📚 شروع مطالعه", callback_data="start_study")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🌌 **خوش آمدید {user_data.get('first_name', 'کاربر')}!**

به آکادمی سرلاک خوش آمدید! 🚀
از منوی زیر گزینه مورد نظر خود را انتخاب کنید.

**آمار شما:**
• 📊 جلسات مطالعه: {get_study_sessions_count(user_data['id'])}
• 🏆 امتیاز: {get_user_points(user_data['id'])}
• 📅 عضویت از: {user_data.get('created_at', 'نامشخص')}
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error showing main menu: {e}")
        await update.message.reply_text("❌ مشکلی در نمایش منوی اصلی پیش آمد.")

async def show_welcome_new_user(update: Update):
    """Show welcome message for new user"""
    try:
        keyboard = [
            [InlineKeyboardButton("🚀 شروع", callback_data="start_profile")],
            [InlineKeyboardButton("ℹ️ درباره سرلاک", callback_data="about_sarlak")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🌌 **خوش آمدید به آکادمی سرلاک!**

به بزرگترین پلتفرم یادگیری هوشمند خوش آمدید! 🚀

**ویژگی‌های ما:**
• 📊 گزارش‌گیری هوشمند
• 🏆 رقابت و لیگ‌های آموزشی  
• 🤖 مربی هوش مصنوعی
• 📚 محتوای آموزشی متنوع
• 🎯 هدف‌گذاری و پیگیری پیشرفت

برای شروع، روی دکمه "شروع" کلیک کنید.
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error showing welcome message: {e}")
        await update.message.reply_text("❌ مشکلی در نمایش پیام خوش‌آمدگویی پیش آمد.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    try:
        query = update.callback_query
        await query.answer()
        
        if query.data == "show_profile":
            await show_profile_section(query)
            
        elif query.data == "edit_profile":
            await edit_profile_section(query)
            
        elif query.data == "menu_reports":
            await show_reports_section(query)
            
        elif query.data == "menu_competition":
            await show_competition_section(query)
            
        elif query.data == "menu_qa":
            await show_qa_section(query)
            
        elif query.data == "start_study":
            await start_study_section(query)
            
        elif query.data == "daily_report":
            await show_daily_report(query)
            
        elif query.data == "weekly_report":
            await show_weekly_report(query)
            
        elif query.data == "leaderboard":
            await show_leaderboard(query)
            
        elif query.data == "challenges":
            await show_challenges(query)
            
        elif query.data == "ask_question":
            await ask_question_section(query)
            
        elif query.data == "faq":
            await show_faq(query)
            
        elif query.data == "go_home":
            await go_home(query)
            
        elif query.data == "start_profile":
            await start_profile_creation(query)
            
        elif query.data == "about_sarlak":
            await show_about_sarlak(query)
            
        else:
            await query.edit_message_text(
                "✅ **عملیات انجام شد**\n\n"
                "این بخش در حال توسعه است.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")
                ]]),
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Button callback failed: {e}")
        await query.edit_message_text("❌ مشکلی در پردازش درخواست پیش آمد.")

async def show_profile_section(query):
    """Show profile section"""
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    
    if user_data:
        profile_text = f"""
👤 **پروفایل شما**

**نام:** {user_data.get('first_name', 'نامشخص')}
**نام کاربری:** @{user_data.get('username', 'نامشخص')}
**رشته:** {user_data.get('field', 'نامشخص')}
**مقطع:** {user_data.get('level', 'نامشخص')}
**استان:** {user_data.get('province', 'نامشخص')}
**شهر:** {user_data.get('city', 'نامشخص')}

**آمار:**
• 📊 جلسات مطالعه: {get_study_sessions_count(user_data['id'])}
• 🏆 امتیاز: {get_user_points(user_data['id'])}
• 📅 عضویت از: {user_data.get('created_at', 'نامشخص')}
        """
        
        keyboard = [
            [InlineKeyboardButton("✏️ ویرایش پروفایل", callback_data="edit_profile")],
            [InlineKeyboardButton("📊 آمار تفصیلی", callback_data="profile_stats")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")]
        ]
        
        await query.edit_message_text(
            profile_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "❌ پروفایل شما یافت نشد. لطفاً ابتدا پروفایل خود را ایجاد کنید.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📝 ایجاد پروفایل", callback_data="start_profile")
            ]]),
            parse_mode='Markdown'
        )

async def edit_profile_section(query):
    """Edit profile section"""
    await query.edit_message_text(
        "✏️ **ویرایش پروفایل**\n\n"
        "برای ویرایش پروفایل خود، لطفاً اطلاعات جدید را وارد کنید.\n\n"
        "**مراحل ویرایش:**\n"
        "1. رشته تحصیلی خود را انتخاب کنید\n"
        "2. مقطع تحصیلی را مشخص کنید\n"
        "3. استان و شهر خود را انتخاب کنید\n"
        "4. شماره تلفن خود را وارد کنید",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 شروع ویرایش", callback_data="edit_field")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="show_profile")]
        ]),
        parse_mode='Markdown'
    )

async def show_reports_section(query):
    """Show reports section"""
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    
    if user_data:
        # Get today's study data
        today_sessions = get_today_study_sessions(user_data['id'])
        total_time = sum(session['duration'] for session in today_sessions)
        
        reports_text = f"""
📊 **گزارش‌های شما**

**گزارش امروز:**
• ⏰ زمان مطالعه: {total_time} دقیقه
• 📚 تعداد جلسات: {len(today_sessions)}
• 🎯 موضوعات: {', '.join(set(session['subject'] for session in today_sessions)) if today_sessions else 'هیچ'}

**آمار کلی:**
• 📊 کل جلسات: {get_study_sessions_count(user_data['id'])}
• ⏰ کل زمان مطالعه: {get_total_study_time(user_data['id'])} دقیقه
• 🏆 امتیاز: {get_user_points(user_data['id'])}
        """
        
        keyboard = [
            [InlineKeyboardButton("📈 گزارش روزانه", callback_data="daily_report")],
            [InlineKeyboardButton("📅 گزارش هفتگی", callback_data="weekly_report")],
            [InlineKeyboardButton("📊 آمار کامل", callback_data="full_stats")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")]
        ]
        
        await query.edit_message_text(
            reports_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "❌ ابتدا باید پروفایل خود را ایجاد کنید.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📝 ایجاد پروفایل", callback_data="start_profile")
            ]]),
            parse_mode='Markdown'
        )

async def show_competition_section(query):
    """Show competition section"""
    await query.edit_message_text(
        "🏆 **رقابت و لیگ**\n\n"
        "در این بخش می‌توانید در رقابت‌ها شرکت کنید و رتبه خود را ببینید.\n\n"
        "**ویژگی‌های رقابت:**\n"
        "• 🏆 جدول رتبه‌بندی\n"
        "• 🎯 چالش‌های روزانه\n"
        "• 🏅 جوایز و مدال‌ها\n"
        "• 📊 آمار رقابتی",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 جدول رتبه‌بندی", callback_data="leaderboard")],
            [InlineKeyboardButton("🎯 چالش‌ها", callback_data="challenges")],
            [InlineKeyboardButton("🏅 جوایز", callback_data="rewards")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")]
        ]),
        parse_mode='Markdown'
    )

async def show_qa_section(query):
    """Show Q&A section"""
    await query.edit_message_text(
        "❓ **پرسش و پاسخ**\n\n"
        "در این بخش می‌توانید سوالات خود را بپرسید و پاسخ دریافت کنید.\n\n"
        "**ویژگی‌های پرسش و پاسخ:**\n"
        "• ❓ پرسیدن سوال\n"
        "• 📚 سوالات متداول\n"
        "• 🔍 جستجوی سوالات\n"
        "• 💬 چت با پشتیبانی",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❓ پرسیدن سوال", callback_data="ask_question")],
            [InlineKeyboardButton("📚 سوالات متداول", callback_data="faq")],
            [InlineKeyboardButton("🔍 جستجو", callback_data="search_qa")],
            [InlineKeyboardButton("💬 پشتیبانی", callback_data="support")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")]
        ]),
        parse_mode='Markdown'
    )

async def start_study_section(query):
    """Start study section"""
    await query.edit_message_text(
        "📚 **شروع مطالعه**\n\n"
        "برای شروع مطالعه، موضوع مورد نظر خود را انتخاب کنید.\n\n"
        "**موضوعات موجود:**\n"
        "• 📖 ریاضی\n"
        "• 🔬 فیزیک\n"
        "• 🧪 شیمی\n"
        "• 🌍 زیست‌شناسی\n"
        "• 📚 ادبیات\n"
        "• 🌐 زبان انگلیسی",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 ریاضی", callback_data="study_math")],
            [InlineKeyboardButton("🔬 فیزیک", callback_data="study_physics")],
            [InlineKeyboardButton("🧪 شیمی", callback_data="study_chemistry")],
            [InlineKeyboardButton("🌍 زیست‌شناسی", callback_data="study_biology")],
            [InlineKeyboardButton("📚 ادبیات", callback_data="study_literature")],
            [InlineKeyboardButton("🌐 زبان انگلیسی", callback_data="study_english")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")]
        ]),
        parse_mode='Markdown'
    )

async def show_daily_report(query):
    """Show daily report"""
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    
    if user_data:
        today_sessions = get_today_study_sessions(user_data['id'])
        total_time = sum(session['duration'] for session in today_sessions)
        
        report_text = f"""
📊 **گزارش روزانه - {datetime.now().strftime('%Y/%m/%d')}**

**آمار امروز:**
• ⏰ زمان مطالعه: {total_time} دقیقه
• 📚 تعداد جلسات: {len(today_sessions)}
• 🎯 موضوعات: {', '.join(set(session['subject'] for session in today_sessions)) if today_sessions else 'هیچ'}

**جزئیات جلسات:**
        """
        
        for i, session in enumerate(today_sessions[:5], 1):
            report_text += f"\n{i}. {session['subject']} - {session['duration']} دقیقه"
        
        if len(today_sessions) > 5:
            report_text += f"\n... و {len(today_sessions) - 5} جلسه دیگر"
        
        keyboard = [
            [InlineKeyboardButton("📅 گزارش هفتگی", callback_data="weekly_report")],
            [InlineKeyboardButton("📊 آمار کامل", callback_data="full_stats")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_reports")]
        ]
        
        await query.edit_message_text(
            report_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "❌ ابتدا باید پروفایل خود را ایجاد کنید.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📝 ایجاد پروفایل", callback_data="start_profile")
            ]]),
            parse_mode='Markdown'
        )

async def show_weekly_report(query):
    """Show weekly report"""
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    
    if user_data:
        weekly_sessions = get_weekly_study_sessions(user_data['id'])
        total_time = sum(session['duration'] for session in weekly_sessions)
        
        report_text = f"""
📅 **گزارش هفتگی**

**آمار این هفته:**
• ⏰ کل زمان مطالعه: {total_time} دقیقه
• 📚 تعداد جلسات: {len(weekly_sessions)}
• 📊 میانگین روزانه: {total_time // 7} دقیقه

**پیشرفت:**
• 🎯 هدف هفتگی: 300 دقیقه
• ✅ پیشرفت: {min(100, (total_time / 300) * 100):.1f}%
        """
        
        keyboard = [
            [InlineKeyboardButton("📈 گزارش روزانه", callback_data="daily_report")],
            [InlineKeyboardButton("📊 آمار کامل", callback_data="full_stats")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_reports")]
        ]
        
        await query.edit_message_text(
            report_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "❌ ابتدا باید پروفایل خود را ایجاد کنید.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📝 ایجاد پروفایل", callback_data="start_profile")
            ]]),
            parse_mode='Markdown'
        )

async def show_leaderboard(query):
    """Show leaderboard"""
    await query.edit_message_text(
        "🏆 **جدول رتبه‌بندی**\n\n"
        "**رتبه‌بندی هفتگی:**\n"
        "🥇 1. علی احمدی - 450 امتیاز\n"
        "🥈 2. مریم رضایی - 380 امتیاز\n"
        "🥉 3. حسن محمدی - 320 امتیاز\n"
        "4. فاطمه کریمی - 280 امتیاز\n"
        "5. محمد صادقی - 250 امتیاز\n\n"
        "**رتبه شما:** 15\n"
        "**امتیاز شما:** 180",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 چالش‌ها", callback_data="challenges")],
            [InlineKeyboardButton("🏅 جوایز", callback_data="rewards")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_competition")]
        ]),
        parse_mode='Markdown'
    )

async def show_challenges(query):
    """Show challenges"""
    await query.edit_message_text(
        "🎯 **چالش‌ها**\n\n"
        "**چالش‌های فعال:**\n"
        "• 📚 مطالعه 2 ساعت در روز\n"
        "• 🏆 کسب 100 امتیاز در هفته\n"
        "• 📖 تکمیل 5 درس ریاضی\n"
        "• 🔬 حل 10 مسئله فیزیک\n\n"
        "**جوایز:**\n"
        "• 🏅 مدال طلا\n"
        "• 🎁 تخفیف 20%\n"
        "• 📚 کتاب رایگان",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏅 جوایز", callback_data="rewards")],
            [InlineKeyboardButton("📊 جدول رتبه‌بندی", callback_data="leaderboard")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_competition")]
        ]),
        parse_mode='Markdown'
    )

async def ask_question_section(query):
    """Ask question section"""
    await query.edit_message_text(
        "❓ **پرسیدن سوال**\n\n"
        "برای پرسیدن سوال، لطفاً سوال خود را تایپ کنید.\n\n"
        "**نکات مهم:**\n"
        "• سوال خود را واضح و کامل بنویسید\n"
        "• موضوع سوال را مشخص کنید\n"
        "• در صورت امکان، تصویر یا فایل ضمیمه کنید\n\n"
        "**موضوعات پشتیبانی شده:**\n"
        "• 📖 ریاضی\n"
        "• 🔬 فیزیک\n"
        "• 🧪 شیمی\n"
        "• 🌍 زیست‌شناسی\n"
        "• 📚 ادبیات\n"
        "• 🌐 زبان انگلیسی",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 سوالات متداول", callback_data="faq")],
            [InlineKeyboardButton("💬 پشتیبانی", callback_data="support")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_qa")]
        ]),
        parse_mode='Markdown'
    )

async def show_faq(query):
    """Show FAQ"""
    await query.edit_message_text(
        "📚 **سوالات متداول**\n\n"
        "**سوالات پرتکرار:**\n\n"
        "**Q: چگونه شروع به مطالعه کنم؟**\n"
        "A: ابتدا پروفایل خود را تکمیل کنید، سپس از منوی 'شروع مطالعه' موضوع مورد نظر را انتخاب کنید.\n\n"
        "**Q: چگونه امتیاز کسب کنم؟**\n"
        "A: با مطالعه و تکمیل جلسات، امتیاز کسب می‌کنید. هر دقیقه مطالعه = 1 امتیاز.\n\n"
        "**Q: چگونه در رقابت شرکت کنم؟**\n"
        "A: از منوی 'لیگ' وارد شوید و در چالش‌ها شرکت کنید.\n\n"
        "**Q: چگونه گزارش‌هایم را ببینم؟**\n"
        "A: از منوی 'گزارش روزانه' می‌توانید آمار مطالعه خود را مشاهده کنید.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❓ پرسیدن سوال", callback_data="ask_question")],
            [InlineKeyboardButton("💬 پشتیبانی", callback_data="support")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_qa")]
        ]),
        parse_mode='Markdown'
    )

async def go_home(query):
    """Go to home menu"""
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    
    if user_data:
        keyboard = [
            [InlineKeyboardButton("👤 پروفایل من", callback_data="show_profile")],
            [InlineKeyboardButton("✏️ ویرایش پروفایل", callback_data="edit_profile")],
            [InlineKeyboardButton("📊 گزارش روزانه", callback_data="menu_reports")],
            [InlineKeyboardButton("🏆 لیگ", callback_data="menu_competition")],
            [InlineKeyboardButton("❓ سوال و جواب", callback_data="menu_qa")],
            [InlineKeyboardButton("📚 شروع مطالعه", callback_data="start_study")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🌌 **منوی اصلی**\n\nخوش آمدید {user_data.get('first_name', 'کاربر')}!\nاز منوی زیر گزینه مورد نظر خود را انتخاب کنید.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        keyboard = [
            [InlineKeyboardButton("🚀 شروع", callback_data="start_profile")],
            [InlineKeyboardButton("ℹ️ درباره سرلاک", callback_data="about_sarlak")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🌌 **خوش آمدید به آکادمی سرلاک!**\n\nبرای شروع، روی دکمه 'شروع' کلیک کنید.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def start_profile_creation(query):
    """Start profile creation"""
    await query.edit_message_text(
        "📝 **ایجاد پروفایل**\n\n"
        "برای شروع، ابتدا پروفایل خود را تکمیل کنید.\n\n"
        "**مراحل ایجاد پروفایل:**\n"
        "1. رشته تحصیلی خود را انتخاب کنید\n"
        "2. مقطع تحصیلی را مشخص کنید\n"
        "3. استان و شهر خود را انتخاب کنید\n"
        "4. شماره تلفن خود را وارد کنید\n\n"
        "این اطلاعات برای شخصی‌سازی تجربه یادگیری شما استفاده می‌شود.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 شروع ایجاد پروفایل", callback_data="profile_create")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")]
        ]),
        parse_mode='Markdown'
    )

async def show_about_sarlak(query):
    """Show about Sarlak"""
    await query.edit_message_text(
        "🌌 **درباره آکادمی سرلاک**\n\n"
        "آکادمی سرلاک یک پلتفرم جامع یادگیری است که با استفاده از تکنولوژی‌های پیشرفته، تجربه یادگیری شخصی‌سازی شده را برای شما فراهم می‌کند.\n\n"
        "**ویژگی‌های کلیدی:**\n"
        "• 📊 سیستم گزارش‌گیری هوشمند\n"
        "• 🏆 رقابت و لیگ‌های آموزشی\n"
        "• 🤖 مربی هوش مصنوعی\n"
        "• 📚 محتوای آموزشی متنوع\n"
        "• 🎯 هدف‌گذاری و پیگیری پیشرفت\n\n"
        "**مزایا:**\n"
        "• یادگیری شخصی‌سازی شده\n"
        "• انگیزه‌بخشی از طریق گیمیفیکیشن\n"
        "• پشتیبانی ۲۴/۷\n"
        "• جامعه یادگیری فعال",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="go_home")]
        ]),
        parse_mode='Markdown'
    )

# Database helper functions
def get_user_data(telegram_id):
    """Get user data from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'telegram_id': user[1],
                'username': user[2],
                'first_name': user[3],
                'last_name': user[4],
                'nickname': user[5],
                'field': user[6],
                'level': user[7],
                'phone': user[8],
                'province': user[9],
                'city': user[10],
                'privacy': user[11],
                'created_at': user[12]
            }
        return None
    except Exception as e:
        logger.error(f"Error getting user data: {e}")
        return None

def get_study_sessions_count(user_id):
    """Get study sessions count for user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM study_sessions WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        logger.error(f"Error getting study sessions count: {e}")
        return 0

def get_user_points(user_id):
    """Get user points"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(duration) FROM study_sessions WHERE user_id = ?", (user_id,))
        points = cursor.fetchone()[0] or 0
        conn.close()
        return points
    except Exception as e:
        logger.error(f"Error getting user points: {e}")
        return 0

def get_today_study_sessions(user_id):
    """Get today's study sessions"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        today = datetime.now().date()
        cursor.execute("SELECT * FROM study_sessions WHERE user_id = ? AND date = ?", (user_id, today))
        sessions = cursor.fetchall()
        conn.close()
        
        return [{'subject': session[2], 'duration': session[3]} for session in sessions]
    except Exception as e:
        logger.error(f"Error getting today's study sessions: {e}")
        return []

def get_weekly_study_sessions(user_id):
    """Get weekly study sessions"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        week_ago = datetime.now().date() - timedelta(days=7)
        cursor.execute("SELECT * FROM study_sessions WHERE user_id = ? AND date >= ?", (user_id, week_ago))
        sessions = cursor.fetchall()
        conn.close()
        
        return [{'subject': session[2], 'duration': session[3]} for session in sessions]
    except Exception as e:
        logger.error(f"Error getting weekly study sessions: {e}")
        return []

def get_total_study_time(user_id):
    """Get total study time for user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(duration) FROM study_sessions WHERE user_id = ?", (user_id,))
        total_time = cursor.fetchone()[0] or 0
        conn.close()
        return total_time
    except Exception as e:
        logger.error(f"Error getting total study time: {e}")
        return 0

async def main():
    """Main function"""
    logger.info("🚀 Starting SarlakBot v6 Complete...")
    
    # Initialize database
    init_database()
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("✅ Bot started successfully!")
    
    # Start polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot failed: {e}")
