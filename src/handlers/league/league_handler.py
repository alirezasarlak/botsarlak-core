"""
🌌 SarlakBot v3.1.0 - League Handler
Complete league and competition system handler
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.config import config
from src.services.league_service import league_service, LeagueType, LeagueTier
from src.core.menu_manager import menu_manager
from src.core.security_audit import security_auditor, ActionType, SecurityLevel, AuditLog
from src.utils.logging import get_logger

logger = get_logger(__name__)


class LeagueHandler:
    """
    🌌 League Handler
    Complete league and competition system
    """
    
    def __init__(self):
        self.logger = logger
    
    async def register(self, application) -> None:
        """Register league handlers"""
        try:
            from telegram.ext import CommandHandler, CallbackQueryHandler
            
            # Register commands
            application.add_handler(CommandHandler("league", self.league_command))
            application.add_handler(CommandHandler("competition", self.competition_command))
            application.add_handler(CommandHandler("leaderboard", self.leaderboard_command))
            
            # Register callbacks
            application.add_handler(CallbackQueryHandler(self.league_callback, pattern="^league_"))
            application.add_handler(CallbackQueryHandler(self.menu_competition_callback, pattern="^menu_competition"))
            
            self.logger.info("✅ League Handler registered")
            
        except Exception as e:
            self.logger.error(f"Failed to register League Handler: {e}")
            raise
    
    async def league_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /league command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Log league access
            await security_auditor.log_audit_event(
                AuditLog(
                    user_id=user_id,
                    action=ActionType.ROUTE_ACCESS,
                    resource="league_command",
                    details={"command": "league"},
                    security_level=SecurityLevel.INFO
                )
            )
            
            # Show main league menu
            await self._show_main_league_menu(update, context)
            
        except Exception as e:
            self.logger.error(f"League command failed: {e}")
            await update.message.reply_text("❌ خطا در نمایش لیگ‌ها. لطفاً دوباره تلاش کنید.")
    
    async def competition_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /competition command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Show competition menu
            await self._show_main_league_menu(update, context)
            
        except Exception as e:
            self.logger.error(f"Competition command failed: {e}")
            await update.message.reply_text("❌ خطا در نمایش رقابت‌ها. لطفاً دوباره تلاش کنید.")
    
    async def leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /leaderboard command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Show global leaderboard
            await self._show_global_leaderboard(update, context)
            
        except Exception as e:
            self.logger.error(f"Leaderboard command failed: {e}")
            await update.message.reply_text("❌ خطا در نمایش جدول امتیازات. لطفاً دوباره تلاش کنید.")
    
    async def menu_competition_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle menu_competition callback"""
        try:
            query = update.callback_query
            await query.answer()
            
            await self._show_main_league_menu(update, context)
            
        except Exception as e:
            self.logger.error(f"Menu competition callback failed: {e}")
            await query.edit_message_text("❌ خطا در نمایش منوی رقابت.")
    
    async def league_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle league callbacks"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            callback_data = query.data
            
            # Log league interaction
            await security_auditor.log_audit_event(
                AuditLog(
                    user_id=user_id,
                    action=ActionType.ROUTE_ACCESS,
                    resource="league_callback",
                    details={"callback": callback_data},
                    security_level=SecurityLevel.INFO
                )
            )
            
            # Handle different league actions
            if callback_data == "league_active":
                await self._show_active_leagues(update, context)
            elif callback_data == "league_my_leagues":
                await self._show_user_leagues(update, context)
            elif callback_data == "league_leaderboard":
                await self._show_global_leaderboard(update, context)
            elif callback_data == "league_private":
                await self._show_private_leagues_menu(update, context)
            elif callback_data == "league_create_private":
                await self._show_create_private_league(update, context)
            elif callback_data == "league_join_private":
                await self._show_join_private_league(update, context)
            elif callback_data.startswith("league_join_"):
                league_id = int(callback_data.split("_")[2])
                await self._join_league(update, context, league_id)
            elif callback_data.startswith("league_view_"):
                league_id = int(callback_data.split("_")[2])
                await self._show_league_details(update, context, league_id)
            elif callback_data.startswith("league_standings_"):
                league_id = int(callback_data.split("_")[2])
                await self._show_league_standings(update, context, league_id)
            elif callback_data == "league_back":
                await self._show_main_league_menu(update, context)
            elif callback_data == "league_home":
                await self._go_home(update, context)
            
        except Exception as e:
            self.logger.error(f"League callback failed: {e}")
            await query.edit_message_text("❌ خطا در پردازش درخواست لیگ.")
    
    async def _show_main_league_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show main league menu"""
        try:
            text = """
🏆 **لیگ‌ها و رقابت‌ها**

🎯 **گزینه‌های موجود:**
• 🏅 لیگ‌های فعال
• 👤 لیگ‌های من
• 🏆 جدول امتیازات
• 🔒 لیگ‌های خصوصی

🌟 **هدف:** رقابت سالم و انگیزه برای مطالعه بیشتر

💡 **نکته:** در لیگ‌های مختلف شرکت کنید و رتبه خود را بهبود دهید!
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🏅 لیگ‌های فعال", callback_data="league_active"),
                    InlineKeyboardButton("👤 لیگ‌های من", callback_data="league_my_leagues")
                ],
                [
                    InlineKeyboardButton("🏆 جدول امتیازات", callback_data="league_leaderboard"),
                    InlineKeyboardButton("🔒 لیگ‌های خصوصی", callback_data="league_private")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="league_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="league_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text, reply_markup=reply_markup, parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    text, reply_markup=reply_markup, parse_mode='Markdown'
                )
                
        except Exception as e:
            self.logger.error(f"Error showing main league menu: {e}")
            raise
    
    async def _show_active_leagues(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show active leagues"""
        try:
            user_id = update.effective_user.id
            
            # Get active leagues
            leagues = await league_service.get_active_leagues()
            
            if not leagues:
                text = """
🏅 **لیگ‌های فعال**

❌ **در حال حاضر هیچ لیگ فعالی وجود ندارد**

💡 **نکته:** به زودی لیگ‌های جدید راه‌اندازی می‌شوند.
                """
                keyboard = [
                    [
                        InlineKeyboardButton("🔙 بازگشت", callback_data="league_back"),
                        InlineKeyboardButton("🏠 خانه", callback_data="league_home")
                    ]
                ]
            else:
                text = """
🏅 **لیگ‌های فعال**

📋 **لیست لیگ‌های قابل شرکت:**
                """
                
                keyboard = []
                
                for league in leagues[:5]:  # Show first 5 leagues
                    # Check if user can join
                    can_join = await self._can_user_join_league(user_id, league.league_id)
                    
                    if can_join:
                        button_text = f"✅ {league.name}"
                        callback_data = f"league_join_{league.league_id}"
                    else:
                        button_text = f"👁️ {league.name}"
                        callback_data = f"league_view_{league.league_id}"
                    
                    keyboard.append([
                        InlineKeyboardButton(button_text, callback_data=callback_data)
                    ])
                
                keyboard.extend([
                    [
                        InlineKeyboardButton("🔙 بازگشت", callback_data="league_back"),
                        InlineKeyboardButton("🏠 خانه", callback_data="league_home")
                    ]
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing active leagues: {e}")
            raise
    
    async def _show_user_leagues(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user's leagues"""
        try:
            user_id = update.effective_user.id
            
            # Get user's leagues
            user_leagues = await league_service.get_user_leagues(user_id)
            
            if not user_leagues:
                text = """
👤 **لیگ‌های من**

❌ **شما در هیچ لیگی شرکت نکرده‌اید**

💡 **نکته:** برای شرکت در لیگ‌ها، از دکمه "لیگ‌های فعال" استفاده کنید.
                """
                keyboard = [
                    [
                        InlineKeyboardButton("🏅 لیگ‌های فعال", callback_data="league_active"),
                        InlineKeyboardButton("🔙 بازگشت", callback_data="league_back")
                    ],
                    [
                        InlineKeyboardButton("🏠 خانه", callback_data="league_home")
                    ]
                ]
            else:
                text = """
👤 **لیگ‌های من**

📋 **لیست لیگ‌هایی که در آن‌ها شرکت کرده‌اید:**
                """
                
                keyboard = []
                
                for league in user_leagues[:5]:  # Show first 5 leagues
                    status = "🟢" if league['is_active'] else "🔴"
                    button_text = f"{status} رتبه {league['rank']} - {league['name']}"
                    
                    keyboard.append([
                        InlineKeyboardButton(button_text, callback_data=f"league_view_{league['league_id']}")
                    ])
                
                keyboard.extend([
                    [
                        InlineKeyboardButton("🏅 لیگ‌های فعال", callback_data="league_active"),
                        InlineKeyboardButton("🔙 بازگشت", callback_data="league_back")
                    ],
                    [
                        InlineKeyboardButton("🏠 خانه", callback_data="league_home")
                    ]
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing user leagues: {e}")
            raise
    
    async def _show_global_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show global leaderboard"""
        try:
            text = """
🏆 **جدول امتیازات جهانی**

🌟 **برترین کاربران:**
            """
            
            # Get top users (this would need to be implemented in league_service)
            # For now, show placeholder
            text += """
🥇 **رتبه 1:** کاربر برتر - <｜place▁holder▁no▁397｜> امتیاز
🥈 **رتبه 2:** کاربر دوم - 2500 امتیاز  
🥉 **رتبه 3:** کاربر سوم - 2000 امتیاز
🏅 **رتبه 4:** کاربر چهارم - 1800 امتیاز
🏅 **رتبه 5:** کاربر پنجم - 1600 امتیاز

💡 **نکته:** برای رسیدن به رتبه‌های بالاتر، بیشتر مطالعه کنید!
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🏅 لیگ‌های فعال", callback_data="league_active"),
                    InlineKeyboardButton("👤 لیگ‌های من", callback_data="league_my_leagues")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="league_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="league_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing global leaderboard: {e}")
            raise
    
    async def _show_private_leagues_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show private leagues menu"""
        try:
            text = """
🔒 **لیگ‌های خصوصی**

🎯 **گزینه‌های موجود:**
• ➕ ایجاد لیگ خصوصی
• 🔑 عضویت در لیگ خصوصی
• 👥 لیگ‌های خصوصی من

💡 **نکته:** لیگ‌های خصوصی برای رقابت با دوستان و آشنایان طراحی شده‌اند.
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("➕ ایجاد لیگ خصوصی", callback_data="league_create_private"),
                    InlineKeyboardButton("🔑 عضویت در لیگ خصوصی", callback_data="league_join_private")
                ],
                [
                    InlineKeyboardButton("👥 لیگ‌های خصوصی من", callback_data="league_my_private")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="league_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="league_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing private leagues menu: {e}")
            raise
    
    async def _join_league(self, update: Update, context: ContextTypes.DEFAULT_TYPE, league_id: int) -> None:
        """Join a league"""
        try:
            user_id = update.effective_user.id
            
            # Join the league
            success = await league_service.join_league(user_id, league_id)
            
            if success:
                text = """
✅ **عضویت در لیگ موفقیت‌آمیز بود!**

🎉 **تبریک!** شما با موفقیت در لیگ عضو شدید.

💡 **نکته:** حالا می‌توانید با مطالعه و تست‌زنی، امتیاز کسب کنید و رتبه خود را بهبود دهید.
                """
            else:
                text = """
❌ **خطا در عضویت در لیگ**

🚫 **دلایل احتمالی:**
• لیگ پر شده است
• شرایط ورود را ندارید
• قبلاً در این لیگ عضو شده‌اید

💡 **نکته:** لطفاً لیگ دیگری را انتخاب کنید.
                """
            
            keyboard = [
                [
                    InlineKeyboardButton("🏅 لیگ‌های فعال", callback_data="league_active"),
                    InlineKeyboardButton("👤 لیگ‌های من", callback_data="league_my_leagues")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="league_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="league_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error joining league: {e}")
            raise
    
    async def _show_league_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE, league_id: int) -> None:
        """Show league details"""
        try:
            user_id = update.effective_user.id
            
            # Get league details and user position
            leagues = await league_service.get_active_leagues()
            league = next((l for l in leagues if l.league_id == league_id), None)
            
            if not league:
                text = """
❌ **لیگ یافت نشد**

💡 **نکته:** این لیگ ممکن است به پایان رسیده یا حذف شده باشد.
                """
            else:
                # Get user position if they're in the league
                user_position = await league_service.get_user_league_position(user_id, league_id)
                
                text = f"""
🏆 **{league.name}**

📊 **اطلاعات لیگ:**
• 🏅 سطح: {league.tier.value.title()}
• 📅 نوع: {league.league_type.value.title()}
• 📆 شروع: {league.start_date.strftime('%Y/%m/%d')}
• 📆 پایان: {league.end_date.strftime('%Y/%m/%d')}
• 👥 شرکت‌کنندگان: {league.current_participants}/{league.max_participants}

🎯 **جوایز:**
• 🥇 رتبه اول: {league.rewards.get('top_1', {}).get('points', 0)} امتیاز
• 🥈 رتبه دوم: {league.rewards.get('top_3', {}).get('points', 0)} امتیاز
• 🥉 رتبه سوم: {league.rewards.get('top_10', {}).get('points', 0)} امتیاز
                """
                
                if user_position:
                    text += f"""

👤 **وضعیت شما:**
• 🏆 رتبه: {user_position['rank']}
• ⭐ امتیاز: {user_position['points']}
• 📊 درصدی: {user_position['percentile']}%
• ⏱️ زمان مطالعه: {user_position['study_time']} دقیقه
                    """
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 جدول امتیازات", callback_data=f"league_standings_{league_id}"),
                    InlineKeyboardButton("✅ عضویت", callback_data=f"league_join_{league_id}")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="league_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="league_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing league details: {e}")
            raise
    
    async def _show_league_standings(self, update: Update, context: ContextTypes.DEFAULT_TYPE, league_id: int) -> None:
        """Show league standings"""
        try:
            # Get league standings
            standings = await league_service.get_league_standings(league_id, 10)
            
            if not standings:
                text = """
📊 **جدول امتیازات**

❌ **هیچ شرکت‌کننده‌ای یافت نشد**
                """
            else:
                text = """
📊 **جدول امتیازات**

🏆 **رتبه‌بندی:**
                """
                
                for i, participant in enumerate(standings[:10], 1):
                    medal = ""
                    if i == 1:
                        medal = "🥇"
                    elif i == 2:
                        medal = "🥈"
                    elif i == 3:
                        medal = "🥉"
                    else:
                        medal = f"{i}."
                    
                    text += f"""
{medal} **{participant['name']}**
   ⭐ {participant['points']} امتیاز | ⏱️ {participant['study_time']} دقیقه | 🧪 {participant['tests_completed']} تست
                    """
            
            keyboard = [
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="league_back"),
                    InlineKeyboardButton("🏠 خانه", callback_data="league_home")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error showing league standings: {e}")
            raise
    
    async def _can_user_join_league(self, user_id: int, league_id: int) -> bool:
        """Check if user can join a league"""
        try:
            # This would need to be implemented in league_service
            # For now, return True as placeholder
            return True
        except Exception as e:
            self.logger.error(f"Error checking if user can join league: {e}")
            return False
    
    async def _go_home(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Go to main menu"""
        try:
            from src.utils.navigation import NavigationKeyboard
            
            text = """
🌌 **منوی اصلی**

خوش برگشتی به کیهان یادگیری! 🚀
            """
            
            keyboard = NavigationKeyboard.create_main_menu_keyboard()
            await update.callback_query.edit_message_text(
                text, reply_markup=keyboard, parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error going home: {e}")
            raise
