"""
🌌 SarlakBot v3.1.0 - Profile Service
Comprehensive profile management service
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ProfileData:
    """Profile data container"""
    user_id: int
    display_name: Optional[str] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: Optional[date] = None
    study_track: Optional[str] = None
    grade_level: Optional[str] = None
    grade_year: Optional[int] = None
    privacy_level: str = "friends_only"
    is_public: bool = False
    show_statistics: bool = True
    show_achievements: bool = True
    show_streak: bool = True


@dataclass
class StatisticsData:
    """Statistics data container"""
    user_id: int
    total_study_time: int = 0
    daily_study_time: int = 0
    weekly_study_time: int = 0
    monthly_study_time: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    total_sessions: int = 0
    completed_goals: int = 0
    total_goals: int = 0
    study_days: int = 0
    last_study_date: Optional[date] = None


@dataclass
class LevelData:
    """Level data container"""
    user_id: int
    current_level: int = 1
    total_points: int = 0
    level_points: int = 0
    next_level_points: int = 100
    level_title: str = "مبتدی"
    level_color: str = "#4CAF50"


class ProfileService:
    """
    🌌 Profile Service
    Comprehensive profile management
    """
    
    def __init__(self):
        self.logger = logger
        self._level_thresholds = {
            1: (0, 100, "مبتدی", "#4CAF50"),
            2: (100, 250, "تازه‌کار", "#8BC34A"),
            3: (250, 500, "در حال یادگیری", "#CDDC39"),
            4: (500, 750, "پیشرفته", "#FFEB3B"),
            5: (750, 1000, "متخصص", "#FFC107"),
            6: (1000, 1500, "استاد", "#FF9800"),
            7: (1500, 2000, "نابغه", "#FF5722"),
            8: (2000, 3000, "افسانه", "#E91E63"),
            9: (3000, 5000, "اسطوره", "#9C27B0"),
            10: (5000, 10000, "خداوند", "#673AB7")
        }
    
    async def get_profile(self, user_id: int) -> Optional[ProfileData]:
        """Get user profile"""
        try:
            # First try to get from user_profiles table
            query = """
                SELECT * FROM user_profiles 
                WHERE user_id = $1
            """
            
            result = await db_manager.fetch_one(query, user_id)
            
            if result:
                return ProfileData(
                    user_id=result['user_id'],
                    display_name=result['display_name'],
                    nickname=result['nickname'],
                    bio=result['bio'],
                    avatar_url=result['avatar_url'],
                    phone_number=result['phone_number'],
                    birth_date=result['birth_date'],
                    study_track=result['study_track'],
                    grade_level=result['grade_level'],
                    grade_year=result['grade_year'],
                    privacy_level=result['privacy_level'],
                    is_public=result['is_public'],
                    show_statistics=result['show_statistics'],
                    show_achievements=result['show_achievements'],
                    show_streak=result['show_streak']
                )
            
            # If not found in user_profiles, get from users table
            query = """
                SELECT * FROM users 
                WHERE user_id = $1
            """
            
            result = await db_manager.fetch_one(query, user_id)
            
            if result:
                return ProfileData(
                    user_id=result['user_id'],
                    display_name=result['real_name'] or result['first_name'],
                    nickname=result['nickname'],
                    bio="",
                    avatar_url=None,
                    phone_number=result['phone'],
                    birth_date=None,
                    study_track=result['study_track'],
                    grade_level=result['grade_band'],
                    grade_year=result['grade_year'],
                    privacy_level="friends_only",
                    is_public=False,
                    show_statistics=True,
                    show_achievements=True,
                    show_streak=True
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get profile for user {user_id}: {e}")
            return None
    
    async def create_profile(self, user_id: int, profile_data: ProfileData) -> bool:
        """Create user profile"""
        try:
            query = """
                INSERT INTO user_profiles (
                    user_id, display_name, nickname, bio, avatar_url, phone_number,
                    birth_date, study_track, grade_level, grade_year, privacy_level,
                    is_public, show_statistics, show_achievements, show_streak
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
                )
            """
            
            await db_manager.execute(
                query,
                user_id,
                profile_data.display_name,
                profile_data.nickname,
                profile_data.bio,
                profile_data.avatar_url,
                profile_data.phone_number,
                profile_data.birth_date,
                profile_data.study_track,
                profile_data.grade_level,
                profile_data.grade_year,
                profile_data.privacy_level,
                profile_data.is_public,
                profile_data.show_statistics,
                profile_data.show_achievements,
                profile_data.show_streak
            )
            
            # Create initial statistics
            await self._create_initial_statistics(user_id)
            
            # Create initial level
            await self._create_initial_level(user_id)
            
            self.logger.info(f"Profile created for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create profile for user {user_id}: {e}")
            return False
    
    async def update_profile(self, user_id: int, profile_data: ProfileData) -> bool:
        """Update user profile"""
        try:
            query = """
                UPDATE user_profiles SET
                    display_name = $2,
                    nickname = $3,
                    bio = $4,
                    avatar_url = $5,
                    phone_number = $6,
                    birth_date = $7,
                    study_track = $8,
                    grade_level = $9,
                    grade_year = $10,
                    privacy_level = $11,
                    is_public = $12,
                    show_statistics = $13,
                    show_achievements = $14,
                    show_streak = $15,
                    updated_at = NOW()
                WHERE user_id = $1
            """
            
            await db_manager.execute(
                query,
                user_id,
                profile_data.display_name,
                profile_data.nickname,
                profile_data.bio,
                profile_data.avatar_url,
                profile_data.phone_number,
                profile_data.birth_date,
                profile_data.study_track,
                profile_data.grade_level,
                profile_data.grade_year,
                profile_data.privacy_level,
                profile_data.is_public,
                profile_data.show_statistics,
                profile_data.show_achievements,
                profile_data.show_streak
            )
            
            self.logger.info(f"Profile updated for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update profile for user {user_id}: {e}")
            return False
    
    async def get_statistics(self, user_id: int) -> Optional[StatisticsData]:
        """Get user statistics"""
        try:
            query = """
                SELECT * FROM user_statistics 
                WHERE user_id = $1
            """
            
            result = await db_manager.fetch_one(query, user_id)
            
            if result:
                return StatisticsData(
                    user_id=result['user_id'],
                    total_study_time=result['total_study_time'],
                    daily_study_time=result['daily_study_time'],
                    weekly_study_time=result['weekly_study_time'],
                    monthly_study_time=result['monthly_study_time'],
                    current_streak=result['current_streak'],
                    longest_streak=result['longest_streak'],
                    total_sessions=result['total_sessions'],
                    completed_goals=result['completed_goals'],
                    total_goals=result['total_goals'],
                    study_days=result['study_days'],
                    last_study_date=result['last_study_date']
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics for user {user_id}: {e}")
            return None
    
    async def update_statistics(self, user_id: int, study_time: int = 0, session_count: int = 0) -> bool:
        """Update user statistics"""
        try:
            # Get current statistics
            stats = await self.get_statistics(user_id)
            if not stats:
                await self._create_initial_statistics(user_id)
                stats = await self.get_statistics(user_id)
            
            # Update statistics
            new_total_time = stats.total_study_time + study_time
            new_sessions = stats.total_sessions + session_count
            new_streak = await self._calculate_streak(user_id)
            
            query = """
                UPDATE user_statistics SET
                    total_study_time = $2,
                    total_sessions = $3,
                    current_streak = $4,
                    longest_streak = GREATEST(longest_streak, $4),
                    last_study_date = CURRENT_DATE,
                    updated_at = NOW()
                WHERE user_id = $1
            """
            
            await db_manager.execute(query, user_id, new_total_time, new_sessions, new_streak)
            
            # Update points and level
            await self._update_points_and_level(user_id, study_time)
            
            # Check for new achievements
            await self._check_achievements(user_id)
            
            self.logger.info(f"Statistics updated for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update statistics for user {user_id}: {e}")
            return False
    
    async def get_level(self, user_id: int) -> Optional[LevelData]:
        """Get user level"""
        try:
            query = """
                SELECT * FROM user_levels 
                WHERE user_id = $1
            """
            
            result = await db_manager.fetch_one(query, user_id)
            
            if result:
                return LevelData(
                    user_id=result['user_id'],
                    current_level=result['current_level'],
                    total_points=result['total_points'],
                    level_points=result['level_points'],
                    next_level_points=result['next_level_points'],
                    level_title=result['level_title'],
                    level_color=result['level_color']
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get level for user {user_id}: {e}")
            return None
    
    async def get_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user achievements"""
        try:
            query = """
                SELECT * FROM user_achievements 
                WHERE user_id = $1 
                ORDER BY unlocked_at DESC
            """
            
            achievements = await db_manager.fetch_all(query, user_id)
            return [dict(achievement) for achievement in achievements]
            
        except Exception as e:
            self.logger.error(f"Failed to get achievements for user {user_id}: {e}")
            return []
    
    async def get_badges(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user badges"""
        try:
            query = """
                SELECT * FROM user_badges 
                WHERE user_id = $1 AND is_displayed = TRUE
                ORDER BY earned_at DESC
            """
            
            badges = await db_manager.fetch_all(query, user_id)
            return [dict(badge) for badge in badges]
            
        except Exception as e:
            self.logger.error(f"Failed to get badges for user {user_id}: {e}")
            return []
    
    async def get_profile_summary(self, user_id: int) -> Dict[str, Any]:
        """Get complete profile summary"""
        try:
            # Get profile data
            profile = await self.get_profile(user_id)
            statistics = await self.get_statistics(user_id)
            level = await self.get_level(user_id)
            achievements = await self.get_achievements(user_id)
            badges = await self.get_badges(user_id)
            
            return {
                "profile": profile,
                "statistics": statistics,
                "level": level,
                "achievements": achievements,
                "badges": badges,
                "achievement_count": len(achievements),
                "badge_count": len(badges)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get profile summary for user {user_id}: {e}")
            return {}
    
    async def _create_initial_statistics(self, user_id: int) -> None:
        """Create initial statistics for user"""
        try:
            query = """
                INSERT INTO user_statistics (user_id) 
                VALUES ($1)
            """
            
            await db_manager.execute(query, user_id)
            
        except Exception as e:
            self.logger.error(f"Failed to create initial statistics for user {user_id}: {e}")
    
    async def _create_initial_level(self, user_id: int) -> None:
        """Create initial level for user"""
        try:
            query = """
                INSERT INTO user_levels (user_id) 
                VALUES ($1)
            """
            
            await db_manager.execute(query, user_id)
            
        except Exception as e:
            self.logger.error(f"Failed to create initial level for user {user_id}: {e}")
    
    async def _calculate_streak(self, user_id: int) -> int:
        """Calculate current streak"""
        try:
            # This is a simplified streak calculation
            # In production, you'd check actual study sessions
            query = """
                SELECT last_study_date FROM user_statistics 
                WHERE user_id = $1
            """
            
            result = await db_manager.fetch_one(query, user_id)
            
            if result and result['last_study_date']:
                last_study = result['last_study_date']
                today = date.today()
                
                if last_study == today:
                    # User studied today, increment streak
                    return await self._get_current_streak(user_id) + 1
                elif last_study == today - timedelta(days=1):
                    # User studied yesterday, maintain streak
                    return await self._get_current_streak(user_id)
                else:
                    # Streak broken
                    return 0
            
            return 1  # First study session
            
        except Exception as e:
            self.logger.error(f"Failed to calculate streak for user {user_id}: {e}")
            return 0
    
    async def _get_current_streak(self, user_id: int) -> int:
        """Get current streak from database"""
        try:
            query = """
                SELECT current_streak FROM user_statistics 
                WHERE user_id = $1
            """
            
            result = await db_manager.fetch_one(query, user_id)
            return result['current_streak'] if result else 0
            
        except Exception as e:
            self.logger.error(f"Failed to get current streak for user {user_id}: {e}")
            return 0
    
    async def _update_points_and_level(self, user_id: int, study_time: int) -> None:
        """Update points and level based on study time"""
        try:
            # Calculate points (1 point per minute of study)
            points_earned = study_time
            
            # Get current level
            level = await self.get_level(user_id)
            if not level:
                return
            
            new_total_points = level.total_points + points_earned
            
            # Calculate new level
            new_level, level_points, next_level_points, level_title, level_color = self._calculate_level(new_total_points)
            
            # Update level
            query = """
                UPDATE user_levels SET
                    current_level = $2,
                    total_points = $3,
                    level_points = $4,
                    next_level_points = $5,
                    level_title = $6,
                    level_color = $7,
                    updated_at = NOW()
                WHERE user_id = $1
            """
            
            await db_manager.execute(
                query, user_id, new_level, new_total_points, 
                level_points, next_level_points, level_title, level_color
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update points and level for user {user_id}: {e}")
    
    def _calculate_level(self, total_points: int) -> Tuple[int, int, int, str, str]:
        """Calculate level based on total points"""
        for level, (min_points, max_points, title, color) in self._level_thresholds.items():
            if min_points <= total_points < max_points:
                level_points = total_points - min_points
                next_level_points = max_points - total_points
                return level, level_points, next_level_points, title, color
        
        # Max level
        max_level = max(self._level_thresholds.keys())
        max_points = self._level_thresholds[max_level][1]
        level_points = total_points - max_points
        return max_level, level_points, 0, "خداوند", "#673AB7"
    
    async def _check_achievements(self, user_id: int) -> None:
        """Check and unlock new achievements"""
        try:
            # Get user statistics
            stats = await self.get_statistics(user_id)
            if not stats:
                return
            
            # Get all achievement definitions
            query = """
                SELECT * FROM achievement_definitions 
                WHERE is_active = TRUE
            """
            
            definitions = await db_manager.fetch_all(query)
            
            for definition in definitions:
                achievement_id = definition['achievement_id']
                requirements = definition['requirements']
                
                # Check if user already has this achievement
                existing_query = """
                    SELECT id FROM user_achievements 
                    WHERE user_id = $1 AND achievement_id = $2
                """
                
                existing = await db_manager.fetch_one(existing_query, user_id, achievement_id)
                if existing:
                    continue
                
                # Check requirements
                if await self._check_achievement_requirements(user_id, requirements, stats):
                    # Unlock achievement
                    await self._unlock_achievement(user_id, definition)
            
        except Exception as e:
            self.logger.error(f"Failed to check achievements for user {user_id}: {e}")
    
    async def _check_achievement_requirements(self, user_id: int, requirements: Dict[str, Any], stats: StatisticsData) -> bool:
        """Check if user meets achievement requirements"""
        try:
            for key, value in requirements.items():
                if key == "total_study_time" and stats.total_study_time < value:
                    return False
                elif key == "current_streak" and stats.current_streak < value:
                    return False
                elif key == "completed_goals" and stats.completed_goals < value:
                    return False
                # Add more requirement checks as needed
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check achievement requirements: {e}")
            return False
    
    async def _unlock_achievement(self, user_id: int, definition: Dict[str, Any]) -> None:
        """Unlock achievement for user"""
        try:
            # Insert achievement
            query = """
                INSERT INTO user_achievements (
                    user_id, achievement_id, achievement_name, achievement_description,
                    achievement_type, achievement_category, points_awarded, badge_icon
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8
                )
            """
            
            await db_manager.execute(
                query,
                user_id,
                definition['achievement_id'],
                definition['achievement_name'],
                definition['achievement_description'],
                definition['achievement_type'],
                definition['achievement_category'],
                definition['points_awarded'],
                definition['badge_icon']
            )
            
            # Add points to user level
            if definition['points_awarded'] > 0:
                await self._add_points(user_id, definition['points_awarded'])
            
            self.logger.info(f"Achievement {definition['achievement_id']} unlocked for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to unlock achievement for user {user_id}: {e}")
    
    async def _add_points(self, user_id: int, points: int) -> None:
        """Add points to user"""
        try:
            query = """
                UPDATE user_levels SET
                    total_points = total_points + $2,
                    updated_at = NOW()
                WHERE user_id = $1
            """
            
            await db_manager.execute(query, user_id, points)
            
        except Exception as e:
            self.logger.error(f"Failed to add points for user {user_id}: {e}")


# Global profile service instance
profile_service = ProfileService()

