"""
🌌 SarlakBot v3.0 - User Database Queries
Professional user data management with UPSERT operations
"""

import asyncpg
from typing import Optional, Dict, Any, List
from datetime import datetime
from src.utils.logging import get_logger

logger = get_logger(__name__)


class UserQueries:
    """
    🌌 User Database Queries
    Handles all user-related database operations with UPSERT logic
    """
    
    def __init__(self, connection: asyncpg.Connection):
        self.conn = connection
        self.logger = logger
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User data dictionary or None
        """
        try:
            query = """
                SELECT * FROM users 
                WHERE user_id = $1
            """
            
            row = await self.conn.fetchrow(query, user_id)
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Get user by ID failed: {e}")
            return None
    
    async def create_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = None,
        is_active: bool = True
    ) -> bool:
        """
        Create new user
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: First name
            last_name: Last name
            language_code: Language code
            is_active: Active status
            
        Returns:
            Success status
        """
        try:
            query = """
                INSERT INTO users (
                    user_id, username, first_name, last_name, 
                    language_code, is_active, created_at, last_seen_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, NOW(), NOW()
                )
            """
            
            await self.conn.execute(
                query, user_id, username, first_name, 
                last_name, language_code, is_active
            )
            
            self.logger.info(f"✅ User {user_id} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Create user failed: {e}")
            return False
    
    async def update_user_activity(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = None,
        is_active: bool = True
    ) -> bool:
        """
        Update user activity (UPSERT logic)
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: First name
            last_name: Last name
            language_code: Language code
            is_active: Active status
            
        Returns:
            Success status
        """
        try:
            query = """
                UPDATE users SET
                    username = COALESCE($2, username),
                    first_name = COALESCE($3, first_name),
                    last_name = COALESCE($4, last_name),
                    language_code = COALESCE($5, language_code),
                    is_active = $6,
                    last_seen_at = NOW(),
                    updated_at = NOW()
                WHERE user_id = $1
            """
            
            result = await self.conn.execute(
                query, user_id, username, first_name, 
                last_name, language_code, is_active
            )
            
            if result == "UPDATE 1":
                self.logger.info(f"✅ User {user_id} activity updated successfully")
                return True
            else:
                self.logger.warning(f"⚠️ User {user_id} not found for update")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Update user activity failed: {e}")
            return False
    
    async def get_or_create_user(self, user_id: int) -> Dict[str, Any]:
        """
        Get or create user (UPSERT pattern)
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User data dictionary
        """
        try:
            # Try to get existing user
            user = await self.get_user_by_id(user_id)
            
            if user:
                return user
            
            # Create new user if doesn't exist
            success = await self.create_user(user_id)
            if success:
                # Return the newly created user
                return await self.get_user_by_id(user_id) or {}
            
            return {}
            
        except Exception as e:
            self.logger.error(f"❌ Get or create user failed: {e}")
            return {}
    
    async def update_user_onboarding_data(
        self,
        user_id: int,
        real_name: Optional[str] = None,
        nickname: Optional[str] = None,
        study_track: Optional[str] = None,
        grade_band: Optional[str] = None,
        grade_year: Optional[str] = None,
        phone: Optional[str] = None,
        onboarding_completed: bool = True
    ) -> bool:
        """
        Update user onboarding data
        
        Args:
            user_id: Telegram user ID
            real_name: Real name
            nickname: Nickname
            study_track: Study track
            grade_band: Grade band
            grade_year: Grade year
            phone: Phone number
            onboarding_completed: Onboarding completion status
            
        Returns:
            Success status
        """
        try:
            query = """
                UPDATE users SET
                    real_name = COALESCE($2, real_name),
                    nickname = COALESCE($3, nickname),
                    study_track = COALESCE($4, study_track),
                    grade_band = COALESCE($5, grade_band),
                    grade_year = COALESCE($6, grade_year),
                    phone = COALESCE($7, phone),
                    onboarding_completed = $8,
                    updated_at = NOW()
                WHERE user_id = $1
            """
            
            result = await self.conn.execute(
                query, user_id, real_name, nickname, study_track,
                grade_band, grade_year, phone, onboarding_completed
            )
            
            if result == "UPDATE 1":
                self.logger.info(f"✅ User {user_id} onboarding data updated successfully")
                return True
            else:
                self.logger.warning(f"⚠️ User {user_id} not found for onboarding update")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Update user onboarding data failed: {e}")
            return False
    
    async def is_nickname_taken(self, nickname: str, exclude_user_id: Optional[int] = None) -> bool:
        """
        Check if nickname is already taken
        
        Args:
            nickname: Nickname to check
            exclude_user_id: User ID to exclude from check
            
        Returns:
            True if nickname is taken
        """
        try:
            if exclude_user_id:
                query = """
                    SELECT COUNT(*) FROM users 
                    WHERE nickname = $1 AND user_id != $2
                """
                count = await self.conn.fetchval(query, nickname, exclude_user_id)
            else:
                query = """
                    SELECT COUNT(*) FROM users 
                    WHERE nickname = $1
                """
                count = await self.conn.fetchval(query, nickname)
            
            return count > 0
            
        except Exception as e:
            self.logger.error(f"❌ Check nickname taken failed: {e}")
            return True  # Assume taken if error
    
    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user profile with gamification data
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User profile data or None
        """
        try:
            query = """
                SELECT 
                    u.*,
                    up.xp_points,
                    up.level,
                    up.total_study_time,
                    up.streak_days,
                    up.last_study_date,
                    up.achievements_count
                FROM users u
                LEFT JOIN user_profiles up ON u.user_id = up.user_id
                WHERE u.user_id = $1
            """
            
            row = await self.conn.fetchrow(query, user_id)
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Get user profile failed: {e}")
            return None
    
    async def update_user_activity_timestamp(self, user_id: int) -> bool:
        """
        Update user last activity timestamp
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Success status
        """
        try:
            query = """
                UPDATE users SET
                    last_activity = NOW(),
                    last_seen_at = NOW()
                WHERE user_id = $1
            """
            
            result = await self.conn.execute(query, user_id)
            
            if result == "UPDATE 1":
                return True
            else:
                self.logger.warning(f"⚠️ User {user_id} not found for activity update")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Update user activity timestamp failed: {e}")
            return False
    
    async def get_active_users_count(self) -> int:
        """
        Get count of active users
        
        Returns:
            Number of active users
        """
        try:
            query = """
                SELECT COUNT(*) FROM users 
                WHERE is_active = TRUE
            """
            
            count = await self.conn.fetchval(query)
            return count or 0
            
        except Exception as e:
            self.logger.error(f"❌ Get active users count failed: {e}")
            return 0
    
    async def get_users_with_onboarding_completed(self) -> List[Dict[str, Any]]:
        """
        Get users who completed onboarding
        
        Returns:
            List of users with completed onboarding
        """
        try:
            query = """
                SELECT * FROM users 
                WHERE onboarding_completed = TRUE
                ORDER BY created_at DESC
            """
            
            rows = await self.conn.fetch(query)
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"❌ Get users with onboarding completed failed: {e}")
            return []
    
    async def search_users(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search users by name, nickname, or username
        
        Args:
            search_term: Search term
            
        Returns:
            List of matching users
        """
        try:
            query = """
                SELECT * FROM users 
                WHERE 
                    real_name ILIKE $1 OR
                    nickname ILIKE $1 OR
                    username ILIKE $1
                ORDER BY 
                    CASE 
                        WHEN real_name ILIKE $1 THEN 1
                        WHEN nickname ILIKE $1 THEN 2
                        WHEN username ILIKE $1 THEN 3
                    END,
                    created_at DESC
                LIMIT 50
            """
            
            search_pattern = f"%{search_term}%"
            rows = await self.conn.fetch(query, search_pattern)
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"❌ Search users failed: {e}")
            return []