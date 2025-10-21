"""
🌌 SarlakBot v3.1.0 - Referral Service
Professional referral system with gamification and token rewards
"""

import asyncio
import secrets
import string
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ReferralData:
    """Referral data container"""
    referrer_user_id: int
    referred_user_id: int
    referral_code: str
    referral_status: str = "pending"
    referral_level: int = 1
    points_earned: int = 0
    tokens_earned: int = 0


@dataclass
class ReferralCodeData:
    """Referral code data container"""
    user_id: int
    code: str
    total_uses: int = 0
    max_uses: int = 0
    is_active: bool = True
    expires_at: Optional[datetime] = None


@dataclass
class TokenData:
    """Token data container"""
    user_id: int
    total_tokens: int = 0
    available_tokens: int = 0
    spent_tokens: int = 0
    locked_tokens: int = 0


class ReferralService:
    """
    🌌 Referral Service
    Professional referral system with gamification
    """
    
    def __init__(self):
        self.logger = logger
        self._referral_rewards = {
            1: {"points": 100, "tokens": 10, "name": "اولین دعوت"},
            5: {"points": 500, "tokens": 50, "name": "5 دعوت"},
            10: {"points": 1200, "tokens": 120, "name": "10 دعوت"},
            25: {"points": 3500, "tokens": 350, "name": "25 دعوت"},
            50: {"points": 8000, "tokens": 800, "name": "50 دعوت"},
            100: {"points": 20000, "tokens": 2000, "name": "100 دعوت"}
        }
    
    async def create_referral_code(self, user_id: int, custom_code: Optional[str] = None) -> str:
        """
        Create referral code for user
        
        Args:
            user_id: User ID
            custom_code: Custom code (optional)
            
        Returns:
            Generated referral code
        """
        try:
            # Generate unique code
            if custom_code:
                code = custom_code.upper()
            else:
                code = self._generate_unique_code()
            
            # Check if code already exists
            existing = await db_manager.fetch_one(
                "SELECT id FROM referral_codes WHERE code = $1", code
            )
            
            if existing:
                # Generate new code if exists
                code = self._generate_unique_code()
            
            # Create referral code
            await db_manager.execute("""
                INSERT INTO referral_codes (user_id, code, max_uses, is_active, expires_at)
                VALUES ($1, $2, $3, $4, $5)
            """, user_id, code, 0, True, None)
            
            self.logger.info(f"Referral code created for user {user_id}: {code}")
            return code
            
        except Exception as e:
            self.logger.error(f"Failed to create referral code for user {user_id}: {e}")
            raise
    
    def _generate_unique_code(self) -> str:
        """Generate unique referral code"""
        # Generate 8-character code with letters and numbers
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(8))
    
    async def get_user_referral_code(self, user_id: int) -> Optional[str]:
        """
        Get user's active referral code
        
        Args:
            user_id: User ID
            
        Returns:
            Referral code or None
        """
        try:
            result = await db_manager.fetch_one("""
                SELECT code FROM referral_codes 
                WHERE user_id = $1 AND is_active = TRUE
                ORDER BY created_at DESC
                LIMIT 1
            """, user_id)
            
            return result['code'] if result else None
            
        except Exception as e:
            self.logger.error(f"Failed to get referral code for user {user_id}: {e}")
            return None
    
    async def process_referral(self, referrer_user_id: int, referred_user_id: int, referral_code: str) -> bool:
        """
        Process referral when new user joins
        
        Args:
            referrer_user_id: User who made the referral
            referred_user_id: User who was referred
            referral_code: Referral code used
            
        Returns:
            Success status
        """
        try:
            # Validate referral code
            code_data = await db_manager.fetch_one("""
                SELECT * FROM referral_codes 
                WHERE code = $1 AND user_id = $2 AND is_active = TRUE
            """, referral_code, referrer_user_id)
            
            if not code_data:
                self.logger.warning(f"Invalid referral code: {referral_code}")
                return False
            
            # Check if already referred
            existing = await db_manager.fetch_one("""
                SELECT id FROM user_referrals 
                WHERE referrer_user_id = $1 AND referred_user_id = $2
            """, referrer_user_id, referred_user_id)
            
            if existing:
                self.logger.warning(f"User {referred_user_id} already referred by {referrer_user_id}")
                return False
            
            # Create referral record
            await db_manager.execute("""
                INSERT INTO user_referrals (
                    referrer_user_id, referred_user_id, referral_code, 
                    referral_status, points_earned, tokens_earned
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """, referrer_user_id, referred_user_id, referral_code, 
                "completed", 0, 0)
            
            # Update referral code usage
            await db_manager.execute("""
                UPDATE referral_codes 
                SET total_uses = total_uses + 1
                WHERE id = $1
            """, code_data['id'])
            
            # Award rewards
            await self._award_referral_rewards(referrer_user_id)
            
            self.logger.info(f"Referral processed: {referrer_user_id} -> {referred_user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process referral: {e}")
            return False
    
    async def _award_referral_rewards(self, user_id: int) -> None:
        """Award referral rewards to user"""
        try:
            # Get user's referral count
            referral_count = await db_manager.fetch_value("""
                SELECT COUNT(*) FROM user_referrals 
                WHERE referrer_user_id = $1 AND referral_status = 'completed'
            """, user_id)
            
            # Check for milestone rewards
            for milestone, rewards in self._referral_rewards.items():
                if referral_count == milestone:
                    # Award points and tokens
                    await self._award_points(user_id, rewards["points"])
                    await self._award_tokens(user_id, rewards["tokens"])
                    
                    # Create achievement
                    await self._create_referral_achievement(user_id, milestone, rewards)
                    
                    self.logger.info(f"Awarded milestone {milestone} to user {user_id}: {rewards}")
                    break
            
        except Exception as e:
            self.logger.error(f"Failed to award referral rewards: {e}")
    
    async def _award_points(self, user_id: int, points: int) -> None:
        """Award points to user"""
        try:
            # Update user level points
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
            await self._ensure_user_tokens(user_id)
            
            # Update tokens
            await db_manager.execute("""
                UPDATE user_tokens 
                SET total_tokens = total_tokens + $2,
                    available_tokens = available_tokens + $2,
                    updated_at = NOW()
                WHERE user_id = $1
            """, user_id, tokens)
            
            # Log transaction
            await self._log_token_transaction(user_id, "earn", tokens, "referral", 
                f"Referral reward: {tokens} tokens")
            
        except Exception as e:
            self.logger.error(f"Failed to award tokens: {e}")
    
    async def _ensure_user_tokens(self, user_id: int) -> None:
        """Ensure user has token record"""
        try:
            existing = await db_manager.fetch_one(
                "SELECT id FROM user_tokens WHERE user_id = $1", user_id
            )
            
            if not existing:
                await db_manager.execute("""
                    INSERT INTO user_tokens (user_id) VALUES ($1)
                """, user_id)
                
        except Exception as e:
            self.logger.error(f"Failed to ensure user tokens: {e}")
    
    async def _log_token_transaction(self, user_id: int, transaction_type: str, 
                                   amount: int, source: str, description: str) -> None:
        """Log token transaction"""
        try:
            await db_manager.execute("""
                INSERT INTO token_transactions (
                    user_id, transaction_type, amount, source, description
                ) VALUES ($1, $2, $3, $4, $5)
            """, user_id, transaction_type, amount, source, description)
            
        except Exception as e:
            self.logger.error(f"Failed to log token transaction: {e}")
    
    async def _create_referral_achievement(self, user_id: int, milestone: int, rewards: Dict[str, Any]) -> None:
        """Create referral achievement"""
        try:
            await db_manager.execute("""
                INSERT INTO user_achievements (
                    user_id, achievement_id, achievement_name, 
                    achievement_description, achievement_type, 
                    achievement_category, points_awarded, badge_icon
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, user_id, f"referral_{milestone}", rewards["name"],
                f"دعوت {milestone} دوست موفق", "referral", "milestone",
                rewards["points"], "🎯")
                
        except Exception as e:
            self.logger.error(f"Failed to create referral achievement: {e}")
    
    async def get_user_referral_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get user referral statistics
        
        Args:
            user_id: User ID
            
        Returns:
            Referral statistics
        """
        try:
            # Get basic stats
            stats = await db_manager.fetch_one("""
                SELECT 
                    COUNT(*) as total_referrals,
                    COUNT(CASE WHEN referral_status = 'completed' THEN 1 END) as completed_referrals,
                    SUM(points_earned) as total_points,
                    SUM(tokens_earned) as total_tokens
                FROM user_referrals 
                WHERE referrer_user_id = $1
            """, user_id)
            
            # Get referral code
            referral_code = await self.get_user_referral_code(user_id)
            
            # Get recent referrals
            recent_referrals = await db_manager.fetch_all("""
                SELECT u.username, u.first_name, ur.referred_at, ur.referral_status
                FROM user_referrals ur
                JOIN users u ON ur.referred_user_id = u.user_id
                WHERE ur.referrer_user_id = $1
                ORDER BY ur.referred_at DESC
                LIMIT 10
            """, user_id)
            
            return {
                "total_referrals": stats["total_referrals"] or 0,
                "completed_referrals": stats["completed_referrals"] or 0,
                "total_points": stats["total_points"] or 0,
                "total_tokens": stats["total_tokens"] or 0,
                "referral_code": referral_code,
                "recent_referrals": recent_referrals
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get referral stats for user {user_id}: {e}")
            return {}
    
    async def get_referral_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get referral leaderboard
        
        Args:
            limit: Number of top referrers to return
            
        Returns:
            Leaderboard data
        """
        try:
            leaderboard = await db_manager.fetch_all("""
                SELECT 
                    u.user_id,
                    u.username,
                    u.first_name,
                    COUNT(ur.id) as referral_count,
                    SUM(ur.tokens_earned) as total_tokens,
                    ROW_NUMBER() OVER (ORDER BY COUNT(ur.id) DESC) as rank
                FROM users u
                INNER JOIN user_referrals ur ON u.user_id = ur.referrer_user_id
                WHERE ur.referral_status = 'completed'
                GROUP BY u.user_id, u.username, u.first_name
                ORDER BY referral_count DESC, total_tokens DESC
                LIMIT $1
            """, limit)
            
            return [dict(row) for row in leaderboard]
            
        except Exception as e:
            self.logger.error(f"Failed to get referral leaderboard: {e}")
            return []
    
    async def validate_referral_code(self, referral_code: str) -> Optional[int]:
        """
        Validate referral code and return referrer user ID
        
        Args:
            referral_code: Referral code to validate
            
        Returns:
            Referrer user ID or None
        """
        try:
            result = await db_manager.fetch_one("""
                SELECT user_id FROM referral_codes 
                WHERE code = $1 AND is_active = TRUE
            """, referral_code.upper())
            
            return result['user_id'] if result else None
            
        except Exception as e:
            self.logger.error(f"Failed to validate referral code: {e}")
            return None


# Global referral service instance
referral_service = ReferralService()
