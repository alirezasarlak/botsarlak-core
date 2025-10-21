"""
🌌 SarlakBot v3.1.0 - Token Service
Professional token management system with lottery integration
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from decimal import Decimal

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TokenTransaction:
    """Token transaction data container"""
    user_id: int
    transaction_type: str  # earn, spend, lock, unlock, transfer
    amount: int
    source: str  # referral, achievement, purchase, lottery
    description: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LotteryEntry:
    """Lottery entry data container"""
    user_id: int
    lottery_id: int
    tokens_spent: int
    entry_count: int = 1


class TokenService:
    """
    🌌 Token Service
    Professional token management with lottery system
    """
    
    def __init__(self):
        self.logger = logger
    
    async def get_user_tokens(self, user_id: int) -> Dict[str, int]:
        """
        Get user token balance
        
        Args:
            user_id: User ID
            
        Returns:
            Token balance dictionary
        """
        try:
            # Ensure user has token record
            await self._ensure_user_tokens(user_id)
            
            result = await db_manager.fetch_one("""
                SELECT total_tokens, available_tokens, spent_tokens, locked_tokens
                FROM user_tokens 
                WHERE user_id = $1
            """, user_id)
            
            if result:
                return {
                    "total_tokens": result["total_tokens"],
                    "available_tokens": result["available_tokens"],
                    "spent_tokens": result["spent_tokens"],
                    "locked_tokens": result["locked_tokens"]
                }
            else:
                return {
                    "total_tokens": 0,
                    "available_tokens": 0,
                    "spent_tokens": 0,
                    "locked_tokens": 0
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get tokens for user {user_id}: {e}")
            return {"total_tokens": 0, "available_tokens": 0, "spent_tokens": 0, "locked_tokens": 0}
    
    async def add_tokens(self, user_id: int, amount: int, source: str, description: str) -> bool:
        """
        Add tokens to user account
        
        Args:
            user_id: User ID
            amount: Amount to add
            source: Source of tokens
            description: Description
            
        Returns:
            Success status
        """
        try:
            # Ensure user has token record
            await self._ensure_user_tokens(user_id)
            
            # Add tokens
            await db_manager.execute("""
                UPDATE user_tokens 
                SET total_tokens = total_tokens + $2,
                    available_tokens = available_tokens + $2,
                    updated_at = NOW()
                WHERE user_id = $1
            """, user_id, amount)
            
            # Log transaction
            await self._log_transaction(user_id, "earn", amount, source, description)
            
            self.logger.info(f"Added {amount} tokens to user {user_id} from {source}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add tokens: {e}")
            return False
    
    async def spend_tokens(self, user_id: int, amount: int, source: str, description: str) -> bool:
        """
        Spend tokens from user account
        
        Args:
            user_id: User ID
            amount: Amount to spend
            source: Source of spending
            description: Description
            
        Returns:
            Success status
        """
        try:
            # Check if user has enough tokens
            balance = await self.get_user_tokens(user_id)
            if balance["available_tokens"] < amount:
                self.logger.warning(f"User {user_id} has insufficient tokens: {balance['available_tokens']} < {amount}")
                return False
            
            # Spend tokens
            await db_manager.execute("""
                UPDATE user_tokens 
                SET available_tokens = available_tokens - $2,
                    spent_tokens = spent_tokens + $2,
                    updated_at = NOW()
                WHERE user_id = $1
            """, user_id, amount)
            
            # Log transaction
            await self._log_transaction(user_id, "spend", amount, source, description)
            
            self.logger.info(f"Spent {amount} tokens from user {user_id} for {source}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to spend tokens: {e}")
            return False
    
    async def lock_tokens(self, user_id: int, amount: int, reason: str) -> bool:
        """
        Lock tokens (for pending transactions)
        
        Args:
            user_id: User ID
            amount: Amount to lock
            reason: Reason for locking
            
        Returns:
            Success status
        """
        try:
            # Check if user has enough available tokens
            balance = await self.get_user_tokens(user_id)
            if balance["available_tokens"] < amount:
                return False
            
            # Lock tokens
            await db_manager.execute("""
                UPDATE user_tokens 
                SET available_tokens = available_tokens - $2,
                    locked_tokens = locked_tokens + $2,
                    updated_at = NOW()
                WHERE user_id = $1
            """, user_id, amount)
            
            # Log transaction
            await self._log_transaction(user_id, "lock", amount, "system", reason)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to lock tokens: {e}")
            return False
    
    async def unlock_tokens(self, user_id: int, amount: int, reason: str) -> bool:
        """
        Unlock tokens (for failed transactions)
        
        Args:
            user_id: User ID
            amount: Amount to unlock
            reason: Reason for unlocking
            
        Returns:
            Success status
        """
        try:
            # Unlock tokens
            await db_manager.execute("""
                UPDATE user_tokens 
                SET available_tokens = available_tokens + $2,
                    locked_tokens = locked_tokens - $2,
                    updated_at = NOW()
                WHERE user_id = $1
            """, user_id, amount)
            
            # Log transaction
            await self._log_transaction(user_id, "unlock", amount, "system", reason)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unlock tokens: {e}")
            return False
    
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
    
    async def _log_transaction(self, user_id: int, transaction_type: str, 
                             amount: int, source: str, description: str, 
                             metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log token transaction"""
        try:
            await db_manager.execute("""
                INSERT INTO token_transactions (
                    user_id, transaction_type, amount, source, description, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """, user_id, transaction_type, amount, source, description, metadata)
            
        except Exception as e:
            self.logger.error(f"Failed to log token transaction: {e}")
    
    async def get_token_transactions(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get user token transactions
        
        Args:
            user_id: User ID
            limit: Number of transactions to return
            
        Returns:
            List of transactions
        """
        try:
            transactions = await db_manager.fetch_all("""
                SELECT transaction_type, amount, source, description, created_at
                FROM token_transactions 
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """, user_id, limit)
            
            return [dict(transaction) for transaction in transactions]
            
        except Exception as e:
            self.logger.error(f"Failed to get token transactions: {e}")
            return []
    
    # ==================== LOTTERY SYSTEM ====================
    
    async def get_active_lotteries(self) -> List[Dict[str, Any]]:
        """
        Get active lotteries
        
        Returns:
            List of active lotteries
        """
        try:
            lotteries = await db_manager.fetch_all("""
                SELECT * FROM lotteries 
                WHERE status = 'active' AND ends_at > NOW()
                ORDER BY created_at DESC
            """)
            
            return [dict(lottery) for lottery in lotteries]
            
        except Exception as e:
            self.logger.error(f"Failed to get active lotteries: {e}")
            return []
    
    async def enter_lottery(self, user_id: int, lottery_id: int, entry_count: int = 1) -> bool:
        """
        Enter user into lottery
        
        Args:
            user_id: User ID
            lottery_id: Lottery ID
            entry_count: Number of entries
            
        Returns:
            Success status
        """
        try:
            # Get lottery info
            lottery = await db_manager.fetch_one("""
                SELECT * FROM lotteries 
                WHERE id = $1 AND status = 'active' AND ends_at > NOW()
            """, lottery_id)
            
            if not lottery:
                self.logger.warning(f"Lottery {lottery_id} not found or inactive")
                return False
            
            # Calculate total cost
            total_cost = lottery["token_cost_per_entry"] * entry_count
            
            # Check if user has enough tokens
            balance = await self.get_user_tokens(user_id)
            if balance["available_tokens"] < total_cost:
                self.logger.warning(f"User {user_id} has insufficient tokens for lottery entry")
                return False
            
            # Check max entries per user
            if lottery["max_entries_per_user"] > 0:
                current_entries = await db_manager.fetch_value("""
                    SELECT COALESCE(SUM(entry_count), 0) FROM lottery_entries 
                    WHERE user_id = $1 AND lottery_id = $2
                """, user_id, lottery_id)
                
                if current_entries + entry_count > lottery["max_entries_per_user"]:
                    self.logger.warning(f"User {user_id} exceeds max entries for lottery {lottery_id}")
                    return False
            
            # Spend tokens
            if not await self.spend_tokens(user_id, total_cost, "lottery", 
                                         f"Lottery entry: {entry_count} entries"):
                return False
            
            # Create lottery entry
            await db_manager.execute("""
                INSERT INTO lottery_entries (
                    user_id, lottery_id, tokens_spent, entry_count
                ) VALUES ($1, $2, $3, $4)
            """, user_id, lottery_id, total_cost, entry_count)
            
            # Update lottery total entries
            await db_manager.execute("""
                UPDATE lotteries 
                SET total_entries = total_entries + $2
                WHERE id = $1
            """, lottery_id, entry_count)
            
            self.logger.info(f"User {user_id} entered lottery {lottery_id} with {entry_count} entries")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enter lottery: {e}")
            return False
    
    async def get_user_lottery_entries(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get user's lottery entries
        
        Args:
            user_id: User ID
            
        Returns:
            List of lottery entries
        """
        try:
            entries = await db_manager.fetch_all("""
                SELECT le.*, l.lottery_name, l.prize_pool, l.prize_currency
                FROM lottery_entries le
                JOIN lotteries l ON le.lottery_id = l.id
                WHERE le.user_id = $1
                ORDER BY le.created_at DESC
            """, user_id)
            
            return [dict(entry) for entry in entries]
            
        except Exception as e:
            self.logger.error(f"Failed to get user lottery entries: {e}")
            return []
    
    async def get_lottery_stats(self, lottery_id: int) -> Dict[str, Any]:
        """
        Get lottery statistics
        
        Args:
            lottery_id: Lottery ID
            
        Returns:
            Lottery statistics
        """
        try:
            # Get lottery info
            lottery = await db_manager.fetch_one("""
                SELECT * FROM lotteries WHERE id = $1
            """, lottery_id)
            
            if not lottery:
                return {}
            
            # Get entry stats
            entry_stats = await db_manager.fetch_one("""
                SELECT 
                    COUNT(DISTINCT user_id) as unique_participants,
                    SUM(entry_count) as total_entries,
                    SUM(tokens_spent) as total_tokens_spent
                FROM lottery_entries 
                WHERE lottery_id = $1
            """, lottery_id)
            
            return {
                "lottery": dict(lottery),
                "stats": dict(entry_stats) if entry_stats else {
                    "unique_participants": 0,
                    "total_entries": 0,
                    "total_tokens_spent": 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get lottery stats: {e}")
            return {}
    
    async def get_token_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get token leaderboard
        
        Args:
            limit: Number of top users to return
            
        Returns:
            Leaderboard data
        """
        try:
            leaderboard = await db_manager.fetch_all("""
                SELECT 
                    u.user_id,
                    u.username,
                    u.first_name,
                    ut.total_tokens,
                    ut.available_tokens,
                    ROW_NUMBER() OVER (ORDER BY ut.total_tokens DESC) as rank
                FROM users u
                INNER JOIN user_tokens ut ON u.user_id = ut.user_id
                ORDER BY ut.total_tokens DESC
                LIMIT $1
            """, limit)
            
            return [dict(row) for row in leaderboard]
            
        except Exception as e:
            self.logger.error(f"Failed to get token leaderboard: {e}")
            return []


# Global token service instance
token_service = TokenService()
