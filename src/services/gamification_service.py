"""
🌌 SarlakBot v3.1.0 - Gamification Service
Professional gamification system with quests, streaks, and leaderboards
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class QuestData:
    """Quest data container"""
    quest_id: int
    quest_name: str
    quest_description: str
    quest_type: str
    quest_target: int
    points_reward: int
    tokens_reward: int
    difficulty: str


@dataclass
class StreakData:
    """Streak data container"""
    user_id: int
    streak_type: str
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date]
    streak_multiplier: float


class GamificationService:
    """
    🌌 Gamification Service
    Professional gamification with quests, streaks, and leaderboards
    """
    
    def __init__(self):
        self.logger = logger
        self._quest_types = {
            "study": "مطالعه",
            "referral": "دعوت دوستان",
            "achievement": "دستاوردها",
            "social": "فعالیت اجتماعی"
        }
        self._difficulty_multipliers = {
            "easy": 1.0,
            "medium": 1.5,
            "hard": 2.0,
            "epic": 3.0
        }
    
    # ==================== QUEST SYSTEM ====================
    
    async def get_daily_quests(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get daily quests for user
        
        Args:
            user_id: User ID
            
        Returns:
            List of daily quests
        """
        try:
            # Get active quests
            quests = await db_manager.fetch_all("""
                SELECT dq.*, 
                       COALESCE(uq.progress, 0) as user_progress,
                       COALESCE(uq.is_completed, FALSE) as is_completed,
                       COALESCE(uq.is_claimed, FALSE) as is_claimed
                FROM daily_quests dq
                LEFT JOIN user_quests uq ON dq.id = uq.quest_id 
                    AND uq.user_id = $1 
                    AND uq.created_at::date = CURRENT_DATE
                WHERE dq.is_active = TRUE
                ORDER BY dq.difficulty, dq.points_reward
            """, user_id)
            
            return [dict(quest) for quest in quests]
            
        except Exception as e:
            self.logger.error(f"Failed to get daily quests for user {user_id}: {e}")
            return []
    
    async def update_quest_progress(self, user_id: int, quest_type: str, progress: int = 1) -> None:
        """
        Update quest progress for user
        
        Args:
            user_id: User ID
            quest_type: Type of quest
            progress: Progress amount
        """
        try:
            # Get active quests of this type
            quests = await db_manager.fetch_all("""
                SELECT dq.*, uq.id as user_quest_id, uq.progress as current_progress
                FROM daily_quests dq
                LEFT JOIN user_quests uq ON dq.id = uq.quest_id 
                    AND uq.user_id = $1 
                    AND uq.created_at::date = CURRENT_DATE
                WHERE dq.quest_type = $2 AND dq.is_active = TRUE
            """, user_id, quest_type)
            
            for quest in quests:
                # Create user quest if doesn't exist
                if not quest["user_quest_id"]:
                    await self._create_user_quest(user_id, quest["id"])
                    current_progress = 0
                else:
                    current_progress = quest["current_progress"] or 0
                
                # Update progress
                new_progress = min(current_progress + progress, quest["quest_target"])
                
                await db_manager.execute("""
                    UPDATE user_quests 
                    SET progress = $3,
                        is_completed = $4,
                        updated_at = NOW()
                    WHERE user_id = $1 AND quest_id = $2
                """, user_id, quest["id"], new_progress, new_progress >= quest["quest_target"])
                
                # Check if quest is completed
                if new_progress >= quest["quest_target"] and not quest.get("is_completed", False):
                    await self._complete_quest(user_id, quest["id"], quest)
            
        except Exception as e:
            self.logger.error(f"Failed to update quest progress: {e}")
    
    async def _create_user_quest(self, user_id: int, quest_id: int) -> None:
        """Create user quest record"""
        try:
            await db_manager.execute("""
                INSERT INTO user_quests (user_id, quest_id, expires_at)
                VALUES ($1, $2, CURRENT_DATE + INTERVAL '1 day')
            """, user_id, quest_id)
            
        except Exception as e:
            self.logger.error(f"Failed to create user quest: {e}")
    
    async def _complete_quest(self, user_id: int, quest_id: int, quest_data: Dict[str, Any]) -> None:
        """Complete quest and award rewards"""
        try:
            # Award points
            if quest_data["points_reward"] > 0:
                await self._award_points(user_id, quest_data["points_reward"])
            
            # Award tokens
            if quest_data["tokens_reward"] > 0:
                await self._award_tokens(user_id, quest_data["tokens_reward"])
            
            # Create achievement
            await self._create_quest_achievement(user_id, quest_data)
            
            self.logger.info(f"Quest {quest_id} completed by user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to complete quest: {e}")
    
    async def claim_quest_reward(self, user_id: int, quest_id: int) -> bool:
        """
        Claim quest reward
        
        Args:
            user_id: User ID
            quest_id: Quest ID
            
        Returns:
            Success status
        """
        try:
            # Check if quest is completed and not claimed
            quest = await db_manager.fetch_one("""
                SELECT * FROM user_quests 
                WHERE user_id = $1 AND quest_id = $2 
                AND is_completed = TRUE AND is_claimed = FALSE
            """, user_id, quest_id)
            
            if not quest:
                return False
            
            # Mark as claimed
            await db_manager.execute("""
                UPDATE user_quests 
                SET is_claimed = TRUE, claimed_at = NOW()
                WHERE user_id = $1 AND quest_id = $2
            """, user_id, quest_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to claim quest reward: {e}")
            return False
    
    # ==================== STREAK SYSTEM ====================
    
    async def update_streak(self, user_id: int, streak_type: str, activity_date: Optional[date] = None) -> None:
        """
        Update user streak
        
        Args:
            user_id: User ID
            streak_type: Type of streak
            activity_date: Date of activity (default: today)
        """
        try:
            if activity_date is None:
                activity_date = date.today()
            
            # Get current streak
            streak = await db_manager.fetch_one("""
                SELECT * FROM user_streaks 
                WHERE user_id = $1 AND streak_type = $2
            """, user_id, streak_type)
            
            if not streak:
                # Create new streak
                await db_manager.execute("""
                    INSERT INTO user_streaks (user_id, streak_type, current_streak, longest_streak, last_activity_date)
                    VALUES ($1, $2, 1, 1, $3)
                """, user_id, streak_type, activity_date)
            else:
                last_activity = streak["last_activity_date"]
                
                if last_activity == activity_date:
                    # Already counted today
                    return
                elif last_activity == activity_date - timedelta(days=1):
                    # Consecutive day - increment streak
                    new_streak = streak["current_streak"] + 1
                    new_longest = max(streak["longest_streak"], new_streak)
                else:
                    # Streak broken - reset
                    new_streak = 1
                    new_longest = streak["longest_streak"]
                
                # Update streak
                await db_manager.execute("""
                    UPDATE user_streaks 
                    SET current_streak = $3,
                        longest_streak = $4,
                        last_activity_date = $5,
                        updated_at = NOW()
                    WHERE user_id = $1 AND streak_type = $2
                """, user_id, streak_type, new_streak, new_longest, activity_date)
            
        except Exception as e:
            self.logger.error(f"Failed to update streak: {e}")
    
    async def get_user_streaks(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get user streaks
        
        Args:
            user_id: User ID
            
        Returns:
            List of user streaks
        """
        try:
            streaks = await db_manager.fetch_all("""
                SELECT * FROM user_streaks 
                WHERE user_id = $1
                ORDER BY current_streak DESC
            """, user_id)
            
            return [dict(streak) for streak in streaks]
            
        except Exception as e:
            self.logger.error(f"Failed to get user streaks: {e}")
            return []
    
    # ==================== LEADERBOARD SYSTEM ====================
    
    async def create_leaderboard(self, name: str, leaderboard_type: str, 
                               period: str = "weekly", prize_pool: int = 0) -> int:
        """
        Create new leaderboard
        
        Args:
            name: Leaderboard name
            leaderboard_type: Type of leaderboard
            period: Period (daily, weekly, monthly, all_time)
            prize_pool: Prize pool in tokens
            
        Returns:
            Leaderboard ID
        """
        try:
            result = await db_manager.fetch_one("""
                INSERT INTO leaderboards (leaderboard_name, leaderboard_type, period, prize_pool)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, name, leaderboard_type, period, prize_pool)
            
            return result["id"]
            
        except Exception as e:
            self.logger.error(f"Failed to create leaderboard: {e}")
            return 0
    
    async def update_leaderboard(self, leaderboard_id: int, user_id: int, score: int) -> None:
        """
        Update leaderboard entry
        
        Args:
            leaderboard_id: Leaderboard ID
            user_id: User ID
            score: User score
        """
        try:
            # Upsert leaderboard entry
            await db_manager.execute("""
                INSERT INTO leaderboard_entries (leaderboard_id, user_id, score)
                VALUES ($1, $2, $3)
                ON CONFLICT (leaderboard_id, user_id) 
                DO UPDATE SET score = $3, updated_at = NOW()
            """, leaderboard_id, user_id, score)
            
            # Update ranks
            await self._update_leaderboard_ranks(leaderboard_id)
            
        except Exception as e:
            self.logger.error(f"Failed to update leaderboard: {e}")
    
    async def _update_leaderboard_ranks(self, leaderboard_id: int) -> None:
        """Update leaderboard ranks"""
        try:
            await db_manager.execute("""
                UPDATE leaderboard_entries 
                SET rank = subquery.rank
                FROM (
                    SELECT user_id, 
                           ROW_NUMBER() OVER (ORDER BY score DESC) as rank
                    FROM leaderboard_entries 
                    WHERE leaderboard_id = $1
                ) as subquery
                WHERE leaderboard_entries.leaderboard_id = $1 
                AND leaderboard_entries.user_id = subquery.user_id
            """, leaderboard_id)
            
        except Exception as e:
            self.logger.error(f"Failed to update leaderboard ranks: {e}")
    
    async def get_leaderboard(self, leaderboard_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get leaderboard data
        
        Args:
            leaderboard_id: Leaderboard ID
            limit: Number of entries to return
            
        Returns:
            Leaderboard data
        """
        try:
            entries = await db_manager.fetch_all("""
                SELECT 
                    u.user_id,
                    u.username,
                    u.first_name,
                    le.score,
                    le.rank,
                    le.prize_tokens
                FROM leaderboard_entries le
                JOIN users u ON le.user_id = u.user_id
                WHERE le.leaderboard_id = $1
                ORDER BY le.rank
                LIMIT $2
            """, leaderboard_id, limit)
            
            return [dict(entry) for entry in entries]
            
        except Exception as e:
            self.logger.error(f"Failed to get leaderboard: {e}")
            return []
    
    async def get_user_leaderboard_position(self, leaderboard_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user's position in leaderboard
        
        Args:
            leaderboard_id: Leaderboard ID
            user_id: User ID
            
        Returns:
            User position data
        """
        try:
            result = await db_manager.fetch_one("""
                SELECT 
                    u.user_id,
                    u.username,
                    u.first_name,
                    le.score,
                    le.rank,
                    le.prize_tokens
                FROM leaderboard_entries le
                JOIN users u ON le.user_id = u.user_id
                WHERE le.leaderboard_id = $1 AND le.user_id = $2
            """, leaderboard_id, user_id)
            
            return dict(result) if result else None
            
        except Exception as e:
            self.logger.error(f"Failed to get user leaderboard position: {e}")
            return None
    
    # ==================== REWARD SYSTEM ====================
    
    async def _award_points(self, user_id: int, points: int) -> None:
        """Award points to user"""
        try:
            await db_manager.execute("""
                UPDATE user_levels 
                SET total_points = total_points + $2,
                    updated_at = NOW()
                WHERE user_id = $1
            """, user_id, points)
            
        except Exception as e:
            self.logger.error(f"Failed to award points: {e}")
    
    async def _award_tokens(self, user_id: int, tokens: int) -> None:
        """Award tokens to user"""
        try:
            # Ensure user has token record
            await db_manager.execute("""
                INSERT INTO user_tokens (user_id) 
                VALUES ($1)
                ON CONFLICT (user_id) DO NOTHING
            """, user_id)
            
            # Award tokens
            await db_manager.execute("""
                UPDATE user_tokens 
                SET total_tokens = total_tokens + $2,
                    available_tokens = available_tokens + $2,
                    updated_at = NOW()
                WHERE user_id = $1
            """, user_id, tokens)
            
        except Exception as e:
            self.logger.error(f"Failed to award tokens: {e}")
    
    async def _create_quest_achievement(self, user_id: int, quest_data: Dict[str, Any]) -> None:
        """Create quest achievement"""
        try:
            await db_manager.execute("""
                INSERT INTO user_achievements (
                    user_id, achievement_id, achievement_name,
                    achievement_description, achievement_type,
                    achievement_category, points_awarded, badge_icon
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, user_id, f"quest_{quest_data['id']}", quest_data["quest_name"],
                f"تکمیل مأموریت: {quest_data['quest_name']}", "quest", "daily",
                quest_data["points_reward"], "🎯")
                
        except Exception as e:
            self.logger.error(f"Failed to create quest achievement: {e}")
    
    # ==================== STATISTICS ====================
    
    async def get_gamification_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get user gamification statistics
        
        Args:
            user_id: User ID
            
        Returns:
            Gamification statistics
        """
        try:
            # Get quest stats
            quest_stats = await db_manager.fetch_one("""
                SELECT 
                    COUNT(*) as total_quests,
                    COUNT(CASE WHEN is_completed = TRUE THEN 1 END) as completed_quests,
                    COUNT(CASE WHEN is_claimed = TRUE THEN 1 END) as claimed_quests
                FROM user_quests 
                WHERE user_id = $1
            """, user_id)
            
            # Get streak stats
            streak_stats = await db_manager.fetch_one("""
                SELECT 
                    COUNT(*) as total_streaks,
                    MAX(current_streak) as best_streak,
                    SUM(current_streak) as total_streak_days
                FROM user_streaks 
                WHERE user_id = $1
            """, user_id)
            
            # Get achievement stats
            achievement_stats = await db_manager.fetch_one("""
                SELECT 
                    COUNT(*) as total_achievements,
                    SUM(points_awarded) as total_achievement_points
                FROM user_achievements 
                WHERE user_id = $1
            """, user_id)
            
            return {
                "quests": dict(quest_stats) if quest_stats else {},
                "streaks": dict(streak_stats) if streak_stats else {},
                "achievements": dict(achievement_stats) if achievement_stats else {}
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get gamification stats: {e}")
            return {}


# Global gamification service instance
gamification_service = GamificationService()
