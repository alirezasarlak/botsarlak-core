"""
🌌 SarlakBot v3.1.0 - Profile Handler
Enhanced profile management with gamification
"""

import asyncio
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.config import config
from src.services.profile_service import profile_service, ProfileData
from src.core.menu_manager import menu_manager
from src.core.security_audit import security_auditor, ActionType, SecurityLevel, AuditLog
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ProfileHandlerV3:
    """
    🌌 Profile Handler V3
    Enhanced profile management with gamification
    """
    
    def __init__(self):
        self.logger = logger
        self.error_count = 0
        self.max_errors = 10
    
    async def register(self, application) -> None:
        """Register profile handlers"""
        try:
            from telegram.ext import CommandHandler, CallbackQueryHandler
            
            # Register commands
            application.add_handler(CommandHandler("profile", self.profile_command))
            application.add_handler(CommandHandler("myprofile", self.profile_command))
            
            # Register callbacks - only profile_ patterns (no menu_profile conflict)
            application.add_handler(CallbackQueryHandler(self.profile_callback, pattern="^profile_"))
            
            self.logger.info("✅ Profile Handler V3 registered")
            
        except Exception as e:
            self.logger.error(f"Failed to register Profile Handler V3: {e}")
            raise
    
    async def _handle_error(self, query, error: Exception, context: str = "Unknown") -> None:
        """Centralized error handling"""
        try:
            self.error_count += 1
            self.logger.error(f"Error in {context}: {error}")
            
            # If too many errors, show generic message
            if self.error_count > self.max_errors:
                error_message = "❌ خطای موقتی در سیستم. لطفاً بعداً تلاش کنید."
            else:
                error_message = f"❌ خطا در {context}: {str(error)[:100]}"
            
            # Try to answer the query
            try:
                await query.edit_message_text(error_message)
            except:
                # If can't edit, send new message
                await query.message.reply_text(error_message)
                
        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")
    
    async def _validate_user_id(self, user_id: int) -> bool:
        """Validate user ID"""
        try:
            if not user_id or user_id <= 0:
                return False
            
            # Check if user exists in database
            from src.database.connection import db_manager
            result = await db_manager.fetch_one(
                "SELECT user_id FROM users WHERE user_id = $1", user_id
            )
            return result is not None
            
        except Exception as e:
            self.logger.error(f"Error validating user ID {user_id}: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources and reset error count"""
        try:
            self.error_count = 0
            self.logger.info("ProfileHandler cleanup completed")
        except Exception as e:
            self.logger.error(f"Error in cleanup: {e}")
    
    def get_memory_usage(self) -> dict:
        """Get memory usage statistics"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            return {
                "rss": memory_info.rss / 1024 / 1024,  # MB
                "vms": memory_info.vms / 1024 / 1024,  # MB
                "error_count": self.error_count,
                "max_errors": self.max_errors
            }
        except Exception as e:
            self.logger.error(f"Error getting memory usage: {e}")
            return {"error": str(e)}
    
    def _validate_input(self, text: str, field_type: str) -> tuple[bool, str]:
        """Validate user input based on field type"""
        try:
            if not text or not text.strip():
                return False, "مقدار نمی‌تواند خالی باشد"
            
            text = text.strip()
            
            if field_type == "display_name":
                if len(text) < 2 or len(text) > 50:
                    return False, "نام نمایشی باید بین 2 تا 50 کاراکتر باشد"
                if not all(c.isalnum() or c.isspace() or c in "آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی" for c in text):
                    return False, "نام نمایشی فقط می‌تواند شامل حروف و اعداد باشد"
                    
            elif field_type == "nickname":
                if len(text) < 2 or len(text) > 30:
                    return False, "نام مستعار باید بین 2 تا 30 کاراکتر باشد"
                if not all(c.isalnum() or c == "_" for c in text):
                    return False, "نام مستعار فقط می‌تواند شامل حروف، اعداد و _ باشد"
                    
            elif field_type == "phone":
                if not text.startswith("09") or len(text) != 11:
                    return False, "شماره تلفن باید با 09 شروع شده و 11 رقم باشد"
                if not text.isdigit():
                    return False, "شماره تلفن فقط می‌تواند شامل اعداد باشد"
                    
            elif field_type == "bio":
                if len(text) > 500:
                    return False, "بیوگرافی نمی‌تواند بیش از 500 کاراکتر باشد"
            
            return True, "معتبر"
            
        except Exception as e:
            self.logger.error(f"Error validating input: {e}")
            return False, "خطا در اعتبارسنجی"
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /profile command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Log profile access
            await security_auditor.log_audit_event(
                AuditLog(
                    user_id=user_id,
                    action=ActionType.ROUTE_ACCESS,
                    resource="profile_command",
                    details={"command": "profile"},
                    security_level=SecurityLevel.INFO
                )
            )
            
            # Get profile summary
            profile_summary = await profile_service.get_profile_summary(user_id)
            
            if not profile_summary:
                # Create initial profile
                await self._create_initial_profile(user_id, user)
                profile_summary = await profile_service.get_profile_summary(user_id)
            
            # Generate profile card
            profile_card = await self._generate_profile_card(profile_summary, user_id)
            
            # Send profile
            await update.message.reply_text(
                profile_card["text"],
                reply_markup=profile_card["keyboard"],
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Profile command failed: {e}")
            await update.message.reply_text("❌ خطا در نمایش پروفایل. لطفاً دوباره تلاش کنید.")
    
    async def profile_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle profile callbacks"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            callback_data = query.data
            
            # Validate user ID
            if not await self._validate_user_id(user_id):
                await query.edit_message_text("❌ کاربر یافت نشد")
                return
            
            # Log profile interaction
            await security_auditor.log_audit_event(
                AuditLog(
                    user_id=user_id,
                    action=ActionType.ROUTE_ACCESS,
                    resource="profile_callback",
                    details={"callback": callback_data},
                    security_level=SecurityLevel.INFO
                )
            )
            
            if callback_data == "profile_view":
                await self._show_profile_details(query, user_id)
            elif callback_data == "profile_edit":
                await self._show_edit_profile(query, user_id)
            elif callback_data == "profile_stats":
                await self._show_profile_statistics(query, user_id)
            elif callback_data == "profile_achievements":
                await self._show_achievements(query, user_id)
            elif callback_data == "profile_badges":
                await self._show_badges(query, user_id)
            elif callback_data == "profile_privacy":
                await self._show_privacy_settings(query, user_id)
            elif callback_data == "profile_stats":
                await self._show_detailed_stats(query, user_id)
            elif callback_data == "profile_back":
                await self._show_main_profile(query, user_id)
            elif callback_data == "profile_edit_personal":
                await self._show_edit_personal_info(query, user_id)
            elif callback_data == "profile_edit_goals":
                await self._show_edit_goals(query, user_id)
            elif callback_data == "goal_daily_study":
                await self._handle_daily_study_goal(query, user_id)
            elif callback_data == "goal_weekly_study":
                await self._handle_weekly_study_goal(query, user_id)
            elif callback_data == "goal_monthly_points":
                await self._handle_monthly_points_goal(query, user_id)
            elif callback_data == "goal_rank":
                await self._handle_rank_goal(query, user_id)
            elif callback_data == "goal_subjects":
                await self._handle_subjects_goal(query, user_id)
            elif callback_data == "privacy_public":
                await self._set_privacy_level(query, user_id, "public")
            elif callback_data == "privacy_friends":
                await self._set_privacy_level(query, user_id, "friends_only")
            elif callback_data == "privacy_private":
                await self._set_privacy_level(query, user_id, "private")
            elif callback_data.startswith("set_goal_daily_"):
                await self._save_goal_setting(query, user_id, "daily_study", callback_data)
            elif callback_data.startswith("set_goal_weekly_"):
                await self._save_goal_setting(query, user_id, "weekly_study", callback_data)
            elif callback_data.startswith("set_goal_monthly_"):
                await self._save_goal_setting(query, user_id, "monthly_points", callback_data)
            elif callback_data.startswith("set_goal_rank_"):
                await self._save_goal_setting(query, user_id, "rank", callback_data)
            elif callback_data.startswith("set_goal_subjects_"):
                await self._save_goal_setting(query, user_id, "subjects", callback_data)
            elif callback_data == "edit_display_name":
                await self._handle_edit_display_name(query, user_id)
            elif callback_data == "edit_nickname":
                await self._handle_edit_nickname(query, user_id)
            elif callback_data == "edit_phone":
                await self._handle_edit_phone(query, user_id)
            elif callback_data == "edit_study_track":
                await self._handle_edit_study_track(query, user_id)
            elif callback_data == "edit_grade":
                await self._handle_edit_grade(query, user_id)
            elif callback_data == "edit_bio":
                await self._handle_edit_bio(query, user_id)
            elif callback_data.startswith("set_track_"):
                await self._save_personal_info(query, user_id, "study_track", callback_data)
            elif callback_data.startswith("set_grade_"):
                await self._save_personal_info(query, user_id, "grade", callback_data)
            else:
                await query.edit_message_text("❌ عملیات نامشخص")
            
        except Exception as e:
            await self._handle_error(query, e, "profile_callback")
    
    async def _create_initial_profile(self, user_id: int, user) -> None:
        """Create initial profile for user"""
        try:
            # Get user data from users table
            from src.database.connection import db_manager
            
            query = """
                SELECT * FROM users 
                WHERE user_id = $1
            """
            
            user_data = await db_manager.fetch_one(query, user_id)
            
            if user_data:
                # Create profile data from existing user data
                profile_data = ProfileData(
                    user_id=user_id,
                    display_name=user_data.get('real_name') or user_data.get('first_name') or "کاربر",
                    nickname=user_data.get('nickname') or user_data.get('username') or f"user_{user_id}",
                    bio="",
                    phone_number=user_data.get('phone'),
                    study_track=user_data.get('study_track'),
                    grade_level=user_data.get('grade_band'),
                    grade_year=user_data.get('grade_year'),
                    privacy_level="friends_only",
                    is_public=False,
                    show_statistics=True,
                    show_achievements=True,
                    show_streak=True
                )
                
                # Create profile
                await profile_service.create_profile(user_id, profile_data)
                
                self.logger.info(f"Initial profile created for user {user_id}")
            else:
                # Create basic profile data
                profile_data = ProfileData(
                    user_id=user_id,
                    display_name=user.first_name or "کاربر",
                    nickname=user.username or f"user_{user_id}",
                    bio="",
                    privacy_level="friends_only",
                    is_public=False,
                    show_statistics=True,
                    show_achievements=True,
                    show_streak=True
                )
                
                # Create profile
                await profile_service.create_profile(user_id, profile_data)
                
                self.logger.info(f"Basic profile created for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to create initial profile for user {user_id}: {e}")
    
    async def _generate_profile_card(self, profile_summary: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Generate profile card"""
        try:
            profile = profile_summary.get("profile")
            statistics = profile_summary.get("statistics")
            level = profile_summary.get("level")
            achievements = profile_summary.get("achievements", [])
            badges = profile_summary.get("badges", [])
            
            # If no profile data, get from users table
            if not profile:
                from src.database.connection import db_manager
                
                query = """
                    SELECT * FROM users 
                    WHERE user_id = $1
                """
                
                user_data = await db_manager.fetch_one(query, user_id)
                
                if user_data:
                    display_name = user_data.get('real_name') or user_data.get('first_name') or "کاربر"
                    nickname = user_data.get('nickname') or user_data.get('username') or f"user_{user_id}"
                    study_track = user_data.get('study_track') or "تعریف نشده"
                    grade_year = user_data.get('grade_year') or "تعریف نشده"
                else:
                    display_name = "کاربر"
                    nickname = f"user_{user_id}"
                    study_track = "تعریف نشده"
                    grade_year = "تعریف نشده"
            else:
                display_name = profile.display_name if profile else "کاربر"
                nickname = profile.nickname if profile else f"user_{user_id}"
                study_track = profile.study_track if profile else "تعریف نشده"
                grade_year = profile.grade_year if profile else "تعریف نشده"
            
            # Statistics
            total_time = statistics.total_study_time if statistics else 0
            current_streak = statistics.current_streak if statistics else 0
            total_sessions = statistics.total_sessions if statistics else 0
            
            # Level info
            current_level = level.current_level if level else 1
            total_points = level.total_points if level else 0
            level_title = level.level_title if level else "مبتدی"
            
            # Format study time
            hours = total_time // 60
            minutes = total_time % 60
            study_time_text = f"{hours} ساعت {minutes} دقیقه" if hours > 0 else f"{minutes} دقیقه"
            
            # Generate profile text
            profile_text = f"""
🪐 **پروفایل {display_name}**

👤 **اطلاعات شخصی:**
• نام: {display_name}
• نام مستعار: @{nickname}
• رشته: {study_track}
• پایه: {grade_year}
• سطح: {current_level} ({level_title})
• امتیاز: {total_points:,}

📊 **آمار مطالعه:**
• ⏱️ زمان کل: {study_time_text}
• 🔥 Streak فعلی: {current_streak} روز
• 📚 جلسات: {total_sessions} جلسه

🏆 **دستاوردها:**
• نشان‌ها: {len(badges)} عدد
• دستاوردها: {len(achievements)} عدد
"""
            
            # Generate keyboard
            keyboard = [
                [
                    InlineKeyboardButton("📈 آمار کامل", callback_data="profile_stats"),
                    InlineKeyboardButton("🏆 دستاوردها", callback_data="profile_achievements")
                ],
                [
                    InlineKeyboardButton("✏️ ویرایش پروفایل", callback_data="profile_edit"),
                    InlineKeyboardButton("🔒 حریم خصوصی", callback_data="profile_privacy")
                ],
                [
                    InlineKeyboardButton("🔙 بازگشت", callback_data="menu_main")
                ]
            ]
            
            return {
                "text": profile_text,
                "keyboard": InlineKeyboardMarkup(keyboard)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate profile card: {e}")
            return {
                "text": "❌ خطا در تولید پروفایل",
                "keyboard": InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="menu_main")
                ]])
            }
    
    async def _show_profile_details(self, query, user_id: int) -> None:
        """Show detailed profile information"""
        try:
            profile_summary = await profile_service.get_profile_summary(user_id)
            
            if not profile_summary:
                await query.edit_message_text("❌ پروفایل یافت نشد")
                return
            
            profile = profile_summary.get("profile")
            
            # Generate detailed profile text
            profile_text = f"""
🪐 **جزئیات پروفایل**

👤 **اطلاعات شخصی:**
• نام: {profile.display_name or 'تعریف نشده'}
• نام مستعار: @{profile.nickname or 'تعریف نشده'}
• بیو: {profile.bio or 'تعریف نشده'}
• شماره تلفن: {profile.phone_number or 'تعریف نشده'}
• مسیر مطالعه: {profile.study_track or 'تعریف نشده'}
• مقطع تحصیلی: {profile.grade_level or 'تعریف نشده'}

🔒 **تنظیمات حریم خصوصی:**
• سطح حریم خصوصی: {profile.privacy_level}
• نمایش عمومی: {'بله' if profile.is_public else 'خیر'}
• نمایش آمار: {'بله' if profile.show_statistics else 'خیر'}
• نمایش دستاوردها: {'بله' if profile.show_achievements else 'خیر'}
• نمایش Streak: {'بله' if profile.show_streak else 'خیر'}
"""
            
            keyboard = [
                [InlineKeyboardButton("✏️ ویرایش", callback_data="profile_edit")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_back")]
            ]
            
            await query.edit_message_text(
                profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show profile details: {e}")
            await query.edit_message_text("❌ خطا در نمایش جزئیات پروفایل")
    
    async def _show_profile_statistics(self, query, user_id: int) -> None:
        """Show profile statistics"""
        try:
            profile_summary = await profile_service.get_profile_summary(user_id)
            
            if not profile_summary:
                await query.edit_message_text("❌ آمار یافت نشد")
                return
            
            statistics = profile_summary.get("statistics")
            level = profile_summary.get("level")
            
            if not statistics:
                await query.edit_message_text("❌ آمار یافت نشد")
                return
            
            # Format statistics
            total_hours = statistics.total_study_time // 60
            total_minutes = statistics.total_study_time % 60
            daily_hours = statistics.daily_study_time // 60
            daily_minutes = statistics.daily_study_time % 60
            
            # Generate statistics text
            stats_text = f"""
📊 **آمار کامل مطالعه**

⏱️ **زمان مطالعه:**
• کل زمان: {total_hours} ساعت {total_minutes} دقیقه
• امروز: {daily_hours} ساعت {daily_minutes} دقیقه
• این هفته: {statistics.weekly_study_time} دقیقه
• این ماه: {statistics.monthly_study_time} دقیقه

🔥 **Streak ها:**
• Streak فعلی: {statistics.current_streak} روز
• طولانی‌ترین Streak: {statistics.longest_streak} روز

📚 **جلسات مطالعه:**
• کل جلسات: {statistics.total_sessions} جلسه
• روزهای مطالعه: {statistics.study_days} روز
• آخرین مطالعه: {statistics.last_study_date or 'هیچ'}

🎯 **اهداف:**
• اهداف تکمیل شده: {statistics.completed_goals}
• کل اهداف: {statistics.total_goals}

🏆 **سطح و امتیاز:**
• سطح فعلی: {level.current_level if level else 1}
• امتیاز کل: {level.total_points if level else 0:,}
• امتیاز این سطح: {level.level_points if level else 0}
• تا سطح بعدی: {level.next_level_points if level else 100}
"""
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_back")]
            ]
            
            await query.edit_message_text(
                stats_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show profile statistics: {e}")
            await query.edit_message_text("❌ خطا در نمایش آمار")
    
    async def _show_achievements(self, query, user_id: int) -> None:
        """Show user achievements"""
        try:
            achievements = await profile_service.get_achievements(user_id)
            
            if not achievements:
                await query.edit_message_text("🏆 هنوز دستاوردی کسب نکرده‌اید!")
                return
            
            # Generate achievements text
            achievements_text = "🏆 **دستاوردهای شما:**\n\n"
            
            for i, achievement in enumerate(achievements[:10], 1):  # Show first 10
                icon = achievement.get('badge_icon', '🏆')
                name = achievement.get('achievement_name', 'دستاورد')
                points = achievement.get('points_awarded', 0)
                unlocked_at = achievement.get('unlocked_at', 'نامشخص')
                
                achievements_text += f"{i}. {icon} **{name}**\n"
                achievements_text += f"   امتیاز: {points}\n"
                achievements_text += f"   تاریخ: {unlocked_at}\n\n"
            
            if len(achievements) > 10:
                achievements_text += f"... و {len(achievements) - 10} دستاورد دیگر"
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_back")]
            ]
            
            await query.edit_message_text(
                achievements_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show achievements: {e}")
            await query.edit_message_text("❌ خطا در نمایش دستاوردها")
    
    async def _show_badges(self, query, user_id: int) -> None:
        """Show user badges"""
        try:
            badges = await profile_service.get_badges(user_id)
            
            if not badges:
                await query.edit_message_text("🏅 هنوز نشان‌ی کسب نکرده‌اید!")
                return
            
            # Generate badges text
            badges_text = "🏅 **نشان‌های شما:**\n\n"
            
            for i, badge in enumerate(badges[:10], 1):  # Show first 10
                icon = badge.get('badge_icon', '🏅')
                name = badge.get('badge_name', 'نشان')
                earned_at = badge.get('earned_at', 'نامشخص')
                
                badges_text += f"{i}. {icon} **{name}**\n"
                badges_text += f"   تاریخ: {earned_at}\n\n"
            
            if len(badges) > 10:
                badges_text += f"... و {len(badges) - 10} نشان دیگر"
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_back")]
            ]
            
            await query.edit_message_text(
                badges_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show badges: {e}")
            await query.edit_message_text("❌ خطا در نمایش نشان‌ها")
    
    async def _show_edit_profile(self, query, user_id: int) -> None:
        """Show edit profile options"""
        try:
            edit_text = """
✏️ **ویرایش پروفایل**

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:

• 📝 ویرایش اطلاعات شخصی
• 🖼️ تغییر آواتار
• 🎯 تنظیم اهداف
• 🔒 تنظیمات حریم خصوصی
"""
            
            keyboard = [
                [InlineKeyboardButton("📝 اطلاعات شخصی", callback_data="profile_edit_personal")],
                [InlineKeyboardButton("🎯 اهداف", callback_data="profile_edit_goals")],
                [InlineKeyboardButton("🎯 دعوت دوستان", callback_data="referral_main")],
                [InlineKeyboardButton("🔒 حریم خصوصی", callback_data="profile_privacy")],
                [InlineKeyboardButton("📊 آمار کامل", callback_data="profile_stats")],
                [InlineKeyboardButton("🏆 نشان‌ها", callback_data="profile_badges")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_back")]
            ]
            
            await query.edit_message_text(
                edit_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show edit profile: {e}")
            await query.edit_message_text("❌ خطا در نمایش ویرایش پروفایل")
    
    async def _show_privacy_settings(self, query, user_id: int) -> None:
        """Show privacy settings"""
        try:
            profile = await profile_service.get_profile(user_id)
            
            if not profile:
                await query.edit_message_text("❌ پروفایل یافت نشد")
                return
            
            privacy_text = f"""
🔒 **تنظیمات حریم خصوصی**

**سطح حریم خصوصی فعلی:** {profile.privacy_level}

**گزینه‌های موجود:**
• 🔓 عمومی - همه می‌توانند پروفایل شما را ببینند
• 👥 فقط دوستان - فقط دوستان شما می‌توانند ببینند
• 🔒 خصوصی - فقط خودتان می‌توانید ببینید

**تنظیمات نمایش:**
• نمایش آمار: {'✅' if profile.show_statistics else '❌'}
• نمایش دستاوردها: {'✅' if profile.show_achievements else '❌'}
• نمایش Streak: {'✅' if profile.show_streak else '❌'}
"""
            
            keyboard = [
                [InlineKeyboardButton("🔓 عمومی", callback_data="privacy_public")],
                [InlineKeyboardButton("👥 فقط دوستان", callback_data="privacy_friends")],
                [InlineKeyboardButton("🔒 خصوصی", callback_data="privacy_private")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_back")]
            ]
            
            await query.edit_message_text(
                privacy_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show privacy settings: {e}")
            await query.edit_message_text("❌ خطا در نمایش تنظیمات حریم خصوصی")
    
    async def _show_main_profile(self, query, user_id: int) -> None:
        """Show main profile view"""
        try:
            # Get profile summary
            profile_summary = await profile_service.get_profile_summary(user_id)
            
            # Generate profile card
            profile_card = await self._generate_profile_card(profile_summary, user_id)
            
            # Update message
            await query.edit_message_text(
                profile_card["text"],
                reply_markup=profile_card["keyboard"],
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show main profile: {e}")
            await query.edit_message_text("❌ خطا در نمایش پروفایل اصلی")
    
    async def _show_edit_personal_info(self, query, user_id: int) -> None:
        """Show edit personal information options"""
        try:
            edit_text = """
✏️ **ویرایش اطلاعات شخصی**

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:

• 📝 تغییر نام نمایشی
• 🏷️ تغییر نام مستعار
• 📱 تغییر شماره تلفن
• 🎯 تغییر رشته تحصیلی
• 📚 تغییر مقطع تحصیلی
• 📄 تغییر بیوگرافی
"""
            
            keyboard = [
                [InlineKeyboardButton("📝 نام نمایشی", callback_data="edit_display_name")],
                [InlineKeyboardButton("🏷️ نام مستعار", callback_data="edit_nickname")],
                [InlineKeyboardButton("📱 شماره تلفن", callback_data="edit_phone")],
                [InlineKeyboardButton("🎯 رشته تحصیلی", callback_data="edit_study_track")],
                [InlineKeyboardButton("📚 مقطع تحصیلی", callback_data="edit_grade")],
                [InlineKeyboardButton("📄 بیوگرافی", callback_data="edit_bio")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit")]
            ]
            
            await query.edit_message_text(
                edit_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show edit personal info: {e}")
            await query.edit_message_text("❌ خطا در نمایش ویرایش اطلاعات")
    
    async def _show_edit_goals(self, query, user_id: int) -> None:
        """Show edit goals options"""
        try:
            goals_text = """
🎯 **تنظیم اهداف تحصیلی**

اینجا می‌تونی اهدافت رو تنظیم کنی:

• ⏰ هدف مطالعه روزانه
• 📅 هدف مطالعه هفتگی
• 🎯 هدف امتیاز ماهانه
• 🏆 هدف رتبه کنکور
• 📚 هدف تکمیل دروس
"""
            
            keyboard = [
                [InlineKeyboardButton("⏰ مطالعه روزانه", callback_data="goal_daily_study")],
                [InlineKeyboardButton("📅 مطالعه هفتگی", callback_data="goal_weekly_study")],
                [InlineKeyboardButton("🎯 امتیاز ماهانه", callback_data="goal_monthly_points")],
                [InlineKeyboardButton("🏆 رتبه کنکور", callback_data="goal_rank")],
                [InlineKeyboardButton("📚 تکمیل دروس", callback_data="goal_subjects")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit")]
            ]
            
            await query.edit_message_text(
                goals_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show edit goals: {e}")
            await query.edit_message_text("❌ خطا در نمایش تنظیم اهداف")
    
    async def _set_privacy_level(self, query, user_id: int, privacy_level: str) -> None:
        """Set user privacy level"""
        try:
            # Update privacy level in database
            await profile_service.update_privacy_level(user_id, privacy_level)
            
            # Show success message
            success_text = f"""
✅ **تنظیمات حریم خصوصی به‌روزرسانی شد**

**سطح جدید:** {privacy_level}

تغییرات شما ذخیره شد و از این لحظه اعمال می‌شود.
"""
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت به پروفایل", callback_data="profile_back")]
            ]
            
            await query.edit_message_text(
                success_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            self.logger.info(f"Privacy level updated for user {user_id}: {privacy_level}")
            
        except Exception as e:
            self.logger.error(f"Failed to set privacy level: {e}")
            await query.edit_message_text("❌ خطا در تنظیم حریم خصوصی")
    
    async def _handle_daily_study_goal(self, query, user_id: int) -> None:
        """Handle daily study goal setting"""
        try:
            goal_text = """
⏰ **هدف مطالعه روزانه**

لطفاً تعداد ساعت مطالعه روزانه مورد نظرت رو انتخاب کن:

• 2 ساعت
• 4 ساعت  
• 6 ساعت
• 8 ساعت
• 10 ساعت
• 12 ساعت
"""
            
            keyboard = [
                [InlineKeyboardButton("2 ساعت", callback_data="set_goal_daily_2")],
                [InlineKeyboardButton("4 ساعت", callback_data="set_goal_daily_4")],
                [InlineKeyboardButton("6 ساعت", callback_data="set_goal_daily_6")],
                [InlineKeyboardButton("8 ساعت", callback_data="set_goal_daily_8")],
                [InlineKeyboardButton("10 ساعت", callback_data="set_goal_daily_10")],
                [InlineKeyboardButton("12 ساعت", callback_data="set_goal_daily_12")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit_goals")]
            ]
            
            await query.edit_message_text(
                goal_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle daily study goal: {e}")
            await query.edit_message_text("❌ خطا در تنظیم هدف مطالعه روزانه")
    
    async def _handle_weekly_study_goal(self, query, user_id: int) -> None:
        """Handle weekly study goal setting"""
        try:
            goal_text = """
📅 **هدف مطالعه هفتگی**

لطفاً تعداد ساعت مطالعه هفتگی مورد نظرت رو انتخاب کن:

• 14 ساعت (2 ساعت/روز)
• 28 ساعت (4 ساعت/روز)
• 42 ساعت (6 ساعت/روز)
• 56 ساعت (8 ساعت/روز)
• 70 ساعت (10 ساعت/روز)
• 84 ساعت (12 ساعت/روز)
"""
            
            keyboard = [
                [InlineKeyboardButton("14 ساعت", callback_data="set_goal_weekly_14")],
                [InlineKeyboardButton("28 ساعت", callback_data="set_goal_weekly_28")],
                [InlineKeyboardButton("42 ساعت", callback_data="set_goal_weekly_42")],
                [InlineKeyboardButton("56 ساعت", callback_data="set_goal_weekly_56")],
                [InlineKeyboardButton("70 ساعت", callback_data="set_goal_weekly_70")],
                [InlineKeyboardButton("84 ساعت", callback_data="set_goal_weekly_84")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit_goals")]
            ]
            
            await query.edit_message_text(
                goal_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle weekly study goal: {e}")
            await query.edit_message_text("❌ خطا در تنظیم هدف مطالعه هفتگی")
    
    async def _handle_monthly_points_goal(self, query, user_id: int) -> None:
        """Handle monthly points goal setting"""
        try:
            goal_text = """
🎯 **هدف امتیاز ماهانه**

لطفاً هدف امتیاز ماهانه مورد نظرت رو انتخاب کن:

• 500 امتیاز
• 1000 امتیاز
• 1500 امتیاز
• 2000 امتیاز
• 2500 امتیاز
• 3000 امتیاز
"""
            
            keyboard = [
                [InlineKeyboardButton("500 امتیاز", callback_data="set_goal_monthly_500")],
                [InlineKeyboardButton("1000 امتیاز", callback_data="set_goal_monthly_1000")],
                [InlineKeyboardButton("1500 امتیاز", callback_data="set_goal_monthly_1500")],
                [InlineKeyboardButton("2000 امتیاز", callback_data="set_goal_monthly_2000")],
                [InlineKeyboardButton("2500 امتیاز", callback_data="set_goal_monthly_2500")],
                [InlineKeyboardButton("3000 امتیاز", callback_data="set_goal_monthly_3000")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit_goals")]
            ]
            
            await query.edit_message_text(
                goal_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle monthly points goal: {e}")
            await query.edit_message_text("❌ خطا در تنظیم هدف امتیاز ماهانه")
    
    async def _handle_rank_goal(self, query, user_id: int) -> None:
        """Handle rank goal setting"""
        try:
            goal_text = """
🏆 **هدف رتبه کنکور**

لطفاً هدف رتبه کنکور مورد نظرت رو انتخاب کن:

• رتبه زیر 1000
• رتبه زیر 5000
• رتبه زیر 10000
• رتبه زیر 20000
• رتبه زیر 50000
• رتبه زیر 100000
"""
            
            keyboard = [
                [InlineKeyboardButton("زیر 1000", callback_data="set_goal_rank_1000")],
                [InlineKeyboardButton("زیر 5000", callback_data="set_goal_rank_5000")],
                [InlineKeyboardButton("زیر 10000", callback_data="set_goal_rank_10000")],
                [InlineKeyboardButton("زیر 20000", callback_data="set_goal_rank_20000")],
                [InlineKeyboardButton("زیر 50000", callback_data="set_goal_rank_50000")],
                [InlineKeyboardButton("زیر 100000", callback_data="set_goal_rank_100000")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit_goals")]
            ]
            
            await query.edit_message_text(
                goal_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle rank goal: {e}")
            await query.edit_message_text("❌ خطا در تنظیم هدف رتبه کنکور")
    
    async def _handle_subjects_goal(self, query, user_id: int) -> None:
        """Handle subjects completion goal setting"""
        try:
            goal_text = """
📚 **هدف تکمیل دروس**

لطفاً هدف تکمیل دروس مورد نظرت رو انتخاب کن:

• 25% دروس
• 50% دروس
• 75% دروس
• 90% دروس
• 100% دروس
• تکمیل همه دروس + مرور
"""
            
            keyboard = [
                [InlineKeyboardButton("25% دروس", callback_data="set_goal_subjects_25")],
                [InlineKeyboardButton("50% دروس", callback_data="set_goal_subjects_50")],
                [InlineKeyboardButton("75% دروس", callback_data="set_goal_subjects_75")],
                [InlineKeyboardButton("90% دروس", callback_data="set_goal_subjects_90")],
                [InlineKeyboardButton("100% دروس", callback_data="set_goal_subjects_100")],
                [InlineKeyboardButton("تکمیل + مرور", callback_data="set_goal_subjects_review")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit_goals")]
            ]
            
            await query.edit_message_text(
                goal_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle subjects goal: {e}")
            await query.edit_message_text("❌ خطا در تنظیم هدف تکمیل دروس")
    
    async def _save_goal_setting(self, query, user_id: int, goal_type: str, callback_data: str) -> None:
        """Save goal setting to database"""
        try:
            from src.database.connection import db_manager
            
            # Extract value from callback_data
            value = callback_data.split('_')[-1]
            
            # Map goal types to database columns
            goal_mapping = {
                "daily_study": "daily_study_goal",
                "weekly_study": "weekly_study_goal", 
                "monthly_points": "monthly_points_goal",
                "rank": "rank_goal",
                "subjects": "subjects_goal"
            }
            
            if goal_type not in goal_mapping:
                await query.edit_message_text("❌ نوع هدف نامشخص")
                return
            
            column_name = goal_mapping[goal_type]
            
            # Convert value to appropriate type
            if goal_type in ["daily_study", "weekly_study", "monthly_points", "rank"]:
                try:
                    value = int(value)
                except ValueError:
                    await query.edit_message_text("❌ مقدار نامعتبر")
                    return
            elif goal_type == "subjects":
                if value == "review":
                    value = "100% + مرور"
                else:
                    value = f"{value}%"
            
            # Save to database
            await db_manager.execute(f"""
                INSERT INTO user_goals (user_id, {column_name}, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET {column_name} = $2, updated_at = NOW()
            """, user_id, value)
            
            # Success message
            goal_names = {
                "daily_study": "مطالعه روزانه",
                "weekly_study": "مطالعه هفتگی",
                "monthly_points": "امتیاز ماهانه", 
                "rank": "رتبه کنکور",
                "subjects": "تکمیل دروس"
            }
            
            success_text = f"""
✅ **هدف {goal_names[goal_type]} تنظیم شد!**

مقدار: {value}

🎯 حالا می‌تونی پیشرفتت رو نسبت به این هدف پیگیری کنی.
"""
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت به اهداف", callback_data="profile_edit_goals")],
                [InlineKeyboardButton("🏠 خانه", callback_data="profile_back")]
            ]
            
            await query.edit_message_text(
                success_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            self.logger.info(f"Goal {goal_type} set for user {user_id}: {value}")
            
        except Exception as e:
            self.logger.error(f"Failed to save goal setting: {e}")
            await query.edit_message_text("❌ خطا در ذخیره هدف")
    
    async def _handle_edit_display_name(self, query, user_id: int) -> None:
        """Handle edit display name"""
        try:
            edit_text = """
📝 **ویرایش نام نمایشی**

لطفاً نام نمایشی جدیدت رو وارد کن:

⚠️ **نکات مهم:**
• نام نمایشی باید بین 2 تا 50 کاراکتر باشه
• فقط حروف فارسی و انگلیسی مجازه
• از کاراکترهای خاص استفاده نکن
"""
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit_personal")]
            ]
            
            await query.edit_message_text(
                edit_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            # Set conversation state for text input
            context = query._bot_data.get('context')
            if context:
                context.user_data['editing_field'] = 'display_name'
                context.user_data['callback_query'] = query
            
        except Exception as e:
            self.logger.error(f"Failed to handle edit display name: {e}")
            await query.edit_message_text("❌ خطا در ویرایش نام نمایشی")
    
    async def _handle_edit_nickname(self, query, user_id: int) -> None:
        """Handle edit nickname"""
        try:
            edit_text = """
🏷️ **ویرایش نام مستعار**

لطفاً نام مستعار جدیدت رو وارد کن:

⚠️ **نکات مهم:**
• نام مستعار باید بین 2 تا 30 کاراکتر باشه
• فقط حروف، اعداد و _ مجازه
• از فاصله و کاراکترهای خاص استفاده نکن
"""
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit_personal")]
            ]
            
            await query.edit_message_text(
                edit_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle edit nickname: {e}")
            await query.edit_message_text("❌ خطا در ویرایش نام مستعار")
    
    async def _handle_edit_phone(self, query, user_id: int) -> None:
        """Handle edit phone number"""
        try:
            edit_text = """
📱 **ویرایش شماره تلفن**

لطفاً شماره تلفن جدیدت رو وارد کن:

⚠️ **نکات مهم:**
• شماره باید با 09 شروع بشه
• باید 11 رقم باشه
• مثال: 09123456789
"""
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit_personal")]
            ]
            
            await query.edit_message_text(
                edit_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle edit phone: {e}")
            await query.edit_message_text("❌ خطا در ویرایش شماره تلفن")
    
    async def _handle_edit_study_track(self, query, user_id: int) -> None:
        """Handle edit study track"""
        try:
            edit_text = """
🎯 **ویرایش رشته تحصیلی**

لطفاً رشته تحصیلی جدیدت رو انتخاب کن:

• ریاضی و فیزیک
• تجربی
• انسانی
• هنر
• زبان
• فنی و حرفه‌ای
"""
            
            keyboard = [
                [InlineKeyboardButton("ریاضی و فیزیک", callback_data="set_track_math")],
                [InlineKeyboardButton("تجربی", callback_data="set_track_experimental")],
                [InlineKeyboardButton("انسانی", callback_data="set_track_humanities")],
                [InlineKeyboardButton("هنر", callback_data="set_track_art")],
                [InlineKeyboardButton("زبان", callback_data="set_track_language")],
                [InlineKeyboardButton("فنی و حرفه‌ای", callback_data="set_track_technical")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit_personal")]
            ]
            
            await query.edit_message_text(
                edit_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle edit study track: {e}")
            await query.edit_message_text("❌ خطا در ویرایش رشته تحصیلی")
    
    async def _handle_edit_grade(self, query, user_id: int) -> None:
        """Handle edit grade"""
        try:
            edit_text = """
📚 **ویرایش مقطع تحصیلی**

لطفاً مقطع تحصیلی جدیدت رو انتخاب کن:

• دهم
• یازدهم
• دوازدهم
• فارغ‌التحصیل
• دانشجو
"""
            
            keyboard = [
                [InlineKeyboardButton("دهم", callback_data="set_grade_10")],
                [InlineKeyboardButton("یازدهم", callback_data="set_grade_11")],
                [InlineKeyboardButton("دوازدهم", callback_data="set_grade_12")],
                [InlineKeyboardButton("فارغ‌التحصیل", callback_data="set_grade_graduate")],
                [InlineKeyboardButton("دانشجو", callback_data="set_grade_student")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit_personal")]
            ]
            
            await query.edit_message_text(
                edit_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle edit grade: {e}")
            await query.edit_message_text("❌ خطا در ویرایش مقطع تحصیلی")
    
    async def _handle_edit_bio(self, query, user_id: int) -> None:
        """Handle edit bio"""
        try:
            edit_text = """
📄 **ویرایش بیوگرافی**

لطفاً بیوگرافی جدیدت رو وارد کن:

⚠️ **نکات مهم:**
• حداکثر 500 کاراکتر
• می‌تونی درباره خودت، اهدافت یا هر چیز دیگه‌ای بنویسی
• از ایموجی و علائم نگارشی استفاده کن
"""
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit_personal")]
            ]
            
            await query.edit_message_text(
                edit_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle edit bio: {e}")
            await query.edit_message_text("❌ خطا در ویرایش بیوگرافی")
    
    async def _save_personal_info(self, query, user_id: int, field: str, callback_data: str) -> None:
        """Save personal information to database"""
        try:
            from src.database.connection import db_manager
            
            # Extract value from callback_data
            value = callback_data.split('_')[-1]
            
            # Map values to display names
            if field == "study_track":
                track_mapping = {
                    "math": "ریاضی و فیزیک",
                    "experimental": "تجربی", 
                    "humanities": "انسانی",
                    "art": "هنر",
                    "language": "زبان",
                    "technical": "فنی و حرفه‌ای"
                }
                display_value = track_mapping.get(value, value)
                column_name = "study_track"
            elif field == "grade":
                grade_mapping = {
                    "10": "دهم",
                    "11": "یازدهم",
                    "12": "دوازدهم",
                    "graduate": "فارغ‌التحصیل",
                    "student": "دانشجو"
                }
                display_value = grade_mapping.get(value, value)
                column_name = "grade_year"
            else:
                display_value = value
                column_name = field
            
            # Save to database
            await db_manager.execute(f"""
                UPDATE users SET {column_name} = $2, updated_at = NOW()
                WHERE user_id = $1
            """, user_id, display_value)
            
            # Success message
            field_names = {
                "study_track": "رشته تحصیلی",
                "grade": "مقطع تحصیلی"
            }
            
            success_text = f"""
✅ **{field_names[field]} به‌روزرسانی شد!**

مقدار جدید: {display_value}

🎯 اطلاعاتت با موفقیت ذخیره شد.
"""
            
            keyboard = [
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit_personal")],
                [InlineKeyboardButton("🏠 خانه", callback_data="profile_back")]
            ]
            
            await query.edit_message_text(
                success_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            self.logger.info(f"Personal info {field} updated for user {user_id}: {display_value}")
            
        except Exception as e:
            self.logger.error(f"Failed to save personal info: {e}")
            await query.edit_message_text("❌ خطا در ذخیره اطلاعات")
    
    async def _show_detailed_stats(self, query, user_id: int) -> None:
        """Show detailed statistics"""
        try:
            profile_summary = await profile_service.get_profile_summary(user_id)
            
            if not profile_summary:
                await query.edit_message_text("❌ آمار یافت نشد")
                return
            
            statistics = profile_summary.get("statistics")
            level = profile_summary.get("level")
            
            if not statistics:
                await query.edit_message_text("❌ آمار یافت نشد")
                return
            
            # Format time
            total_hours = statistics.total_study_time // 60
            total_minutes = statistics.total_study_time % 60
            daily_hours = statistics.daily_study_time // 60
            daily_minutes = statistics.daily_study_time % 60
            
            # Calculate efficiency
            efficiency = (statistics.completed_goals / max(statistics.total_goals, 1)) * 100
            
            # Generate detailed stats
            detailed_stats = f"""
📊 **آمار تفصیلی مطالعه**

⏱️ **زمان‌بندی:**
• کل زمان: {total_hours:,} ساعت {total_minutes} دقیقه
• امروز: {daily_hours} ساعت {daily_minutes} دقیقه
• این هفته: {statistics.weekly_study_time:,} دقیقه
• این ماه: {statistics.monthly_study_time:,} دقیقه

📚 **آزمون‌ها:**
• کل آزمون‌ها: {statistics.total_tests:,}
• آزمون‌های امروز: {statistics.daily_tests}
• آزمون‌های این هفته: {statistics.weekly_tests}
• آزمون‌های این ماه: {statistics.monthly_tests}

🎯 **اهداف:**
• اهداف تکمیل شده: {statistics.completed_goals}
• کل اهداف: {statistics.total_goals}
• درصد موفقیت: {efficiency:.1f}%

🏆 **سطح و امتیاز:**
• سطح فعلی: {level.current_level if level else 1}
• امتیاز کل: {level.total_points if level else 0:,}
• امتیاز این سطح: {level.level_points if level else 0}
• نشان فعلی: {level.badge if level else 'Novice 🚀'}

📈 **روند مطالعه:**
• میانگین روزانه: {statistics.daily_study_time // 60} ساعت
• بهترین روز: {statistics.best_study_day} دقیقه
• روزهای مطالعه: {statistics.study_days} روز
• رکورد هفتگی: {statistics.best_weekly_study} دقیقه
"""
            
            keyboard = [
                [InlineKeyboardButton("📊 نمودار پیشرفت", callback_data="profile_chart")],
                [InlineKeyboardButton("🏆 دستاوردها", callback_data="profile_achievements")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="profile_edit")]
            ]
            
            await query.edit_message_text(
                detailed_stats,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show detailed stats: {e}")
            await query.edit_message_text("❌ خطا در نمایش آمار تفصیلی")
    
    async def menu_profile_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle menu profile callback"""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            
            # Get profile summary
            profile_summary = await profile_service.get_profile_summary(user_id)
            
            # Generate profile card
            profile_card = await self._generate_profile_card(profile_summary, user_id)
            
            # Update message
            await query.edit_message_text(
                profile_card["text"],
                reply_markup=profile_card["keyboard"],
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Menu profile callback failed: {e}")
            await query.edit_message_text("❌ خطا در نمایش پروفایل")


# Global profile handler instance
profile_handler_v3 = ProfileHandlerV3()

