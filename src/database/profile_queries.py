"""
🌌 SarlakBot v2.4.0 - Profile Database Queries
MERGE-SAFE: Profile and gamification database operations
"""

import asyncpg
from typing import Optional, Dict, Any, List
from src.utils.logging import get_logger

logger = get_logger(__name__)

class ProfileQueries:
    """
    Profile and gamification database operations
    """
    
    def __init__(self, connection: asyncpg.Connection):
        self.conn = connection
    
    # Stats queries
    async def get_today_totals(self, user_id: int) -> Dict[str, Any]:
        """Get today's study totals"""
        try:
            result = await self.conn.fetchrow(
                """
                SELECT 
                    COALESCE(study_minutes, 0) as study_minutes,
                    COALESCE(tests_count, 0) as tests
                FROM study_reports 
                WHERE user_id = $1 AND report_date = CURRENT_DATE
                """,
                user_id
            )
            
            if result:
                return dict(result)
            else:
                return {"study_minutes": 0, "tests": 0}
                
        except Exception as e:
            logger.error(f"Error getting today totals: {e}")
            return {"study_minutes": 0, "tests": 0}
    
    async def get_lifetime_totals(self, user_id: int) -> Dict[str, Any]:
        """Get lifetime study totals"""
        try:
            result = await self.conn.fetchrow(
                """
                SELECT 
                    COALESCE(SUM(study_minutes), 0) as study_minutes,
                    COALESCE(SUM(tests_count), 0) as tests
                FROM study_reports 
                WHERE user_id = $1
                """,
                user_id
            )
            
            if result:
                return dict(result)
            else:
                return {"study_minutes": 0, "tests": 0}
                
        except Exception as e:
            logger.error(f"Error getting lifetime totals: {e}")
            return {"study_minutes": 0, "tests": 0}
    
    # Gamification queries
    async def recalc_gamification(self, user_id: int) -> Dict[str, Any]:
        """Recalculate and store gamification data"""
        try:
            result = await self.conn.fetchrow(
                "SELECT * FROM recalc_user_gamification($1)",
                user_id
            )
            
            if result:
                return dict(result)
            else:
                return {"points": 0, "level": 1, "badge": "Novice 🚀"}
                
        except Exception as e:
            logger.error(f"Error recalculating gamification: {e}")
            return {"points": 0, "level": 1, "badge": "Novice 🚀"}
    
    async def get_gamification(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's gamification data"""
        try:
            result = await self.conn.fetchrow(
                "SELECT * FROM user_gamification WHERE user_id = $1",
                user_id
            )
            
            return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"Error getting gamification: {e}")
            return None
    
    async def get_global_rank(self, user_id: int) -> Optional[int]:
        """Get user's global rank"""
        try:
            result = await self.conn.fetchval(
                """
                SELECT rank FROM (
                    SELECT user_id, ROW_NUMBER() OVER (ORDER BY points DESC) as rank
                    FROM user_gamification
                ) ranked WHERE user_id = $1
                """,
                user_id
            )
            
            return result
                
        except Exception as e:
            logger.error(f"Error getting global rank: {e}")
            return None
    
    # Privacy & public ID queries
    async def ensure_public_profile_id(self, user_id: int) -> str:
        """Ensure user has public profile ID"""
        try:
            result = await self.conn.fetchval(
                "SELECT public_profile_id FROM users WHERE user_id = $1",
                user_id
            )
            
            if result:
                return result
            
            # Generate new ID
            new_id = await self.conn.fetchval(
                "SELECT generate_public_profile_id($1)",
                user_id
            )
            
            await self.conn.execute(
                "UPDATE users SET public_profile_id = $1 WHERE user_id = $2",
                new_id, user_id
            )
            
            return new_id
                
        except Exception as e:
            logger.error(f"Error ensuring public profile ID: {e}")
            return f"SB-{user_id}-XX"
    
    async def set_profile_visibility(self, user_id: int, is_public: bool) -> bool:
        """Set profile visibility"""
        try:
            await self.conn.execute(
                "UPDATE users SET profile_public = $1 WHERE user_id = $2",
                is_public, user_id
            )
            return True
                
        except Exception as e:
            logger.error(f"Error setting profile visibility: {e}")
            return False
    
    # Profile field setters
    async def set_exam_brand(self, user_id: int, brand: str) -> bool:
        """Set exam brand"""
        try:
            await self.conn.execute(
                "UPDATE users SET exam_brand = $1 WHERE user_id = $2",
                brand, user_id
            )
            return True
        except Exception as e:
            logger.error(f"Error setting exam brand: {e}")
            return False
    
    async def set_exam_tscore_avg(self, user_id: int, val: Optional[float]) -> bool:
        """Set exam tscore average"""
        try:
            await self.conn.execute(
                "UPDATE users SET exam_tscore_avg = $1 WHERE user_id = $2",
                val, user_id
            )
            return True
        except Exception as e:
            logger.error(f"Error setting exam tscore: {e}")
            return False
    
    async def set_konkur_experience(self, user_id: int, took: bool, times: Optional[int], last_rank: Optional[str]) -> bool:
        """Set konkur experience"""
        try:
            await self.conn.execute(
                """
                UPDATE users 
                SET took_konkur = $1, konkur_times = $2, last_konkur_rank = $3
                WHERE user_id = $4
                """,
                took, times, last_rank, user_id
            )
            return True
        except Exception as e:
            logger.error(f"Error setting konkur experience: {e}")
            return False
    
    async def set_has_advisor(self, user_id: int, flag: bool) -> bool:
        """Set advisor status"""
        try:
            await self.conn.execute(
                "UPDATE users SET has_advisor = $1 WHERE user_id = $2",
                flag, user_id
            )
            return True
        except Exception as e:
            logger.error(f"Error setting advisor status: {e}")
            return False
    
    async def set_phone(self, user_id: int, phone: Optional[str]) -> bool:
        """Set phone number"""
        try:
            await self.conn.execute(
                "UPDATE users SET phone = $1 WHERE user_id = $2",
                phone, user_id
            )
            return True
        except Exception as e:
            logger.error(f"Error setting phone: {e}")
            return False
    
    async def set_track(self, user_id: int, track: str) -> bool:
        """Set study track"""
        try:
            await self.conn.execute(
                "UPDATE users SET study_track = $1 WHERE user_id = $2",
                track, user_id
            )
            return True
        except Exception as e:
            logger.error(f"Error setting track: {e}")
            return False
    
    async def set_location(self, user_id: int, province: str, city: str) -> bool:
        """Set location"""
        try:
            await self.conn.execute(
                "UPDATE users SET province = $1, city = $2 WHERE user_id = $3",
                province, city, user_id
            )
            return True
        except Exception as e:
            logger.error(f"Error setting location: {e}")
            return False
    
    async def set_school_type(self, user_id: int, school: str) -> bool:
        """Set school type"""
        try:
            await self.conn.execute(
                "UPDATE users SET school_type = $1 WHERE user_id = $2",
                school, user_id
            )
            return True
        except Exception as e:
            logger.error(f"Error setting school type: {e}")
            return False
    
    async def set_target(self, user_id: int, major: Optional[str], uni: Optional[str], city: Optional[str]) -> bool:
        """Set target goals"""
        try:
            await self.conn.execute(
                """
                UPDATE users 
                SET target_major = $1, target_university = $2, target_city = $3
                WHERE user_id = $4
                """,
                major, uni, city, user_id
            )
            return True
        except Exception as e:
            logger.error(f"Error setting target: {e}")
            return False
    
    # Profile completion
    async def compute_profile_completion(self, user_id: int) -> int:
        """Calculate profile completion percentage"""
        try:
            result = await self.conn.fetchval(
                "SELECT calculate_profile_completion($1)",
                user_id
            )
            return result or 0
        except Exception as e:
            logger.error(f"Error computing profile completion: {e}")
            return 0
    
    # Public profile queries
    async def get_public_profile(self, public_id: str) -> Optional[Dict[str, Any]]:
        """Get public profile by public ID"""
        try:
            result = await self.conn.fetchrow(
                """
                SELECT u.*, ug.points, ug.level, ug.badge
                FROM users u
                LEFT JOIN user_gamification ug ON u.user_id = ug.user_id
                WHERE u.public_profile_id = $1 AND u.profile_public = true
                """,
                public_id
            )
            
            return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"Error getting public profile: {e}")
            return None




