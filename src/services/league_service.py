"""
🌌 SarlakBot v3.1.0 - League Service
Advanced league and competition system
"""

import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum
from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


class LeagueType(Enum):
    """League types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"


class LeagueTier(Enum):
    """League tiers"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    CHALLENGER = "challenger"


@dataclass
class League:
    """League data structure"""
    league_id: int
    name: str
    tier: LeagueTier
    league_type: LeagueType
    start_date: date
    end_date: date
    max_participants: int
    current_participants: int
    entry_requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    is_active: bool = True


@dataclass
class LeagueParticipant:
    """League participant data structure"""
    user_id: int
    league_id: int
    rank: int
    points: int
    study_time: int
    tests_completed: int
    accuracy: float
    streak: int
    joined_at: datetime
    last_activity: datetime


@dataclass
class LeagueReward:
    """League reward data structure"""
    reward_id: int
    league_id: int
    rank_min: int
    rank_max: int
    reward_type: str  # points, badge, title, etc.
    reward_value: str
    reward_description: str


class LeagueService:
    """
    🌌 League Service
    Advanced league and competition system
    """
    
    def __init__(self):
        self.logger = logger
        self.league_config = {
            'daily': {
                'duration_days': 1,
                'max_participants': 100,
                'entry_points': 0,
                'rewards': {
                    'top_1': {'points': 100, 'badge': 'daily_champion'},
                    'top_3': {'points': 50, 'badge': 'daily_top3'},
                    'top_10': {'points': 25, 'badge': 'daily_top10'}
                }
            },
            'weekly': {
                'duration_days': 7,
                'max_participants': 500,
                'entry_points': 100,
                'rewards': {
                    'top_1': {'points': 500, 'badge': 'weekly_champion'},
                    'top_3': {'points': 300, 'badge': 'weekly_top3'},
                    'top_10': {'points': 150, 'badge': 'weekly_top10'}
                }
            },
            'monthly': {
                'duration_days': 30,
                'max_participants': 1000,
                'entry_points': 500,
                'rewards': {
                    'top_1': {'points': 2000, 'badge': 'monthly_champion'},
                    'top_3': {'points': 1200, 'badge': 'monthly_top3'},
                    'top_10': {'points': 600, 'badge': 'monthly_top10'}
                }
            },
            'seasonal': {
                'duration_days': 90,
                'max_participants': 2000,
                'entry_points': 1000,
                'rewards': {
                    'top_1': {'points': 10000, 'badge': 'seasonal_champion'},
                    'top_3': {'points': 6000, 'badge': 'seasonal_top3'},
                    'top_10': {'points': 3000, 'badge': 'seasonal_top10'}
                }
            }
        }
    
    async def create_league(
        self,
        league_type: LeagueType,
        name: str = None,
        start_date: date = None,
        custom_config: Dict[str, Any] = None
    ) -> Optional[League]:
        """Create a new league"""
        try:
            if start_date is None:
                start_date = date.today()
            
            config = self.league_config.get(league_type.value, {})
            if custom_config:
                config.update(custom_config)
            
            end_date = start_date + timedelta(days=config['duration_days'])
            
            if name is None:
                name = f"{league_type.value.title()} League - {start_date.strftime('%Y-%m-%d')}"
            
            async with db_manager.get_connection() as conn:
                result = await conn.fetchrow(
                    """
                    INSERT INTO leagues 
                    (name, tier, league_type, start_date, end_date, max_participants, 
                     entry_requirements, rewards, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING league_id, name, tier, league_type, start_date, end_date, 
                              max_participants, current_participants, entry_requirements, rewards, is_active
                    """,
                    name, LeagueTier.BRONZE.value, league_type.value, start_date, end_date,
                    config['max_participants'], config, config['rewards'], True
                )
                
                if result:
                    return League(
                        league_id=result['league_id'],
                        name=result['name'],
                        tier=LeagueTier(result['tier']),
                        league_type=LeagueType(result['league_type']),
                        start_date=result['start_date'],
                        end_date=result['end_date'],
                        max_participants=result['max_participants'],
                        current_participants=result['current_participants'],
                        entry_requirements=result['entry_requirements'],
                        rewards=result['rewards'],
                        is_active=result['is_active']
                    )
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating league: {e}")
            return None
    
    async def join_league(self, user_id: int, league_id: int) -> bool:
        """Join a league"""
        try:
            async with db_manager.get_connection() as conn:
                # Check if league exists and is active
                league = await conn.fetchrow(
                    """
                    SELECT * FROM leagues 
                    WHERE league_id = $1 AND is_active = TRUE 
                    AND start_date <= CURRENT_DATE AND end_date >= CURRENT_DATE
                    """,
                    league_id
                )
                
                if not league:
                    self.logger.warning(f"League {league_id} not found or not active")
                    return False
                
                # Check if user is already in the league
                existing = await conn.fetchrow(
                    """
                    SELECT * FROM league_participants 
                    WHERE user_id = $1 AND league_id = $2
                    """,
                    user_id, league_id
                )
                
                if existing:
                    self.logger.warning(f"User {user_id} already in league {league_id}")
                    return False
                
                # Check if league is full
                if league['current_participants'] >= league['max_participants']:
                    self.logger.warning(f"League {league_id} is full")
                    return False
                
                # Check entry requirements
                entry_reqs = league['entry_requirements']
                if entry_reqs.get('entry_points', 0) > 0:
                    user_points = await self._get_user_points(user_id)
                    if user_points < entry_reqs['entry_points']:
                        self.logger.warning(f"User {user_id} doesn't meet entry requirements")
                        return False
                
                # Add user to league
                await conn.execute(
                    """
                    INSERT INTO league_participants 
                    (user_id, league_id, points, study_time, tests_completed, 
                     accuracy, streak, joined_at, last_activity)
                    VALUES ($1, $2, 0, 0, 0, 0.0, 0, NOW(), NOW())
                    """,
                    user_id, league_id
                )
                
                # Update league participant count
                await conn.execute(
                    """
                    UPDATE leagues 
                    SET current_participants = current_participants + 1
                    WHERE league_id = $1
                    """,
                    league_id
                )
                
                self.logger.info(f"User {user_id} joined league {league_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error joining league: {e}")
            return False
    
    async def update_league_standings(self, league_id: int) -> bool:
        """Update league standings and rankings"""
        try:
            async with db_manager.get_connection() as conn:
                # Get all participants with their stats
                participants = await conn.fetch(
                    """
                    SELECT 
                        lp.user_id,
                        lp.league_id,
                        COALESCE(sr.total_study_minutes, 0) as study_time,
                        COALESCE(sr.tests_count, 0) as tests_completed,
                        CASE 
                            WHEN sr.total_questions > 0 
                            THEN (sr.correct_answers::DECIMAL / sr.total_questions::DECIMAL) * 100
                            ELSE 0.0
                        END as accuracy,
                        COALESCE(us.current_streak, 0) as streak,
                        lp.joined_at,
                        NOW() as last_activity
                    FROM league_participants lp
                    LEFT JOIN study_reports sr ON lp.user_id = sr.user_id 
                        AND sr.report_date >= (SELECT start_date FROM leagues WHERE league_id = lp.league_id)
                        AND sr.report_date <= (SELECT end_date FROM leagues WHERE league_id = lp.league_id)
                    LEFT JOIN user_statistics us ON lp.user_id = us.user_id
                    WHERE lp.league_id = $1
                    GROUP BY lp.user_id, lp.league_id, lp.joined_at
                    """,
                    league_id
                )
                
                # Calculate points for each participant
                for participant in participants:
                    points = self._calculate_league_points(
                        study_time=participant['study_time'],
                        tests_completed=participant['tests_completed'],
                        accuracy=participant['accuracy'],
                        streak=participant['streak']
                    )
                    
                    # Update participant stats
                    await conn.execute(
                        """
                        UPDATE league_participants 
                        SET points = $1, study_time = $2, tests_completed = $3, 
                            accuracy = $4, streak = $5, last_activity = $6
                        WHERE user_id = $7 AND league_id = $8
                        """,
                        points, participant['study_time'], participant['tests_completed'],
                        participant['accuracy'], participant['streak'], participant['last_activity'],
                        participant['user_id'], participant['league_id']
                    )
                
                # Update rankings
                await conn.execute(
                    """
                    UPDATE league_participants 
                    SET rank = ranked_participants.new_rank
                    FROM (
                        SELECT user_id, league_id,
                               ROW_NUMBER() OVER (ORDER BY points DESC, study_time DESC, accuracy DESC) as new_rank
                        FROM league_participants
                        WHERE league_id = $1
                    ) ranked_participants
                    WHERE league_participants.user_id = ranked_participants.user_id
                    AND league_participants.league_id = ranked_participants.league_id
                    """,
                    league_id
                )
                
                self.logger.info(f"Updated standings for league {league_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating league standings: {e}")
            return False
    
    async def get_league_standings(self, league_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get league standings"""
        try:
            async with db_manager.get_connection() as conn:
                results = await conn.fetch(
                    """
                    SELECT 
                        lp.rank,
                        u.real_name,
                        u.nickname,
                        lp.points,
                        lp.study_time,
                        lp.tests_completed,
                        lp.accuracy,
                        lp.streak,
                        lp.last_activity
                    FROM league_participants lp
                    JOIN users u ON lp.user_id = u.user_id
                    WHERE lp.league_id = $1
                    ORDER BY lp.rank ASC
                    LIMIT $2
                    """,
                    league_id, limit
                )
                
                standings = []
                for row in results:
                    standings.append({
                        'rank': row['rank'],
                        'name': row['real_name'] or row['nickname'] or 'Unknown',
                        'nickname': row['nickname'],
                        'points': row['points'],
                        'study_time': row['study_time'],
                        'tests_completed': row['tests_completed'],
                        'accuracy': round(row['accuracy'], 1),
                        'streak': row['streak'],
                        'last_activity': row['last_activity']
                    })
                
                return standings
                
        except Exception as e:
            self.logger.error(f"Error getting league standings: {e}")
            return []
    
    async def get_user_league_position(self, user_id: int, league_id: int) -> Optional[Dict[str, Any]]:
        """Get user's position in a specific league"""
        try:
            async with db_manager.get_connection() as conn:
                result = await conn.fetchrow(
                    """
                    SELECT 
                        lp.rank,
                        lp.points,
                        lp.study_time,
                        lp.tests_completed,
                        lp.accuracy,
                        lp.streak,
                        COUNT(*) as total_participants
                    FROM league_participants lp
                    CROSS JOIN (
                        SELECT COUNT(*) as total_participants
                        FROM league_participants
                        WHERE league_id = $2
                    ) total
                    WHERE lp.user_id = $1 AND lp.league_id = $2
                    """,
                    user_id, league_id
                )
                
                if result:
                    return {
                        'rank': result['rank'],
                        'points': result['points'],
                        'study_time': result['study_time'],
                        'tests_completed': result['tests_completed'],
                        'accuracy': round(result['accuracy'], 1),
                        'streak': result['streak'],
                        'total_participants': result['total_participants'],
                        'percentile': round((1 - (result['rank'] - 1) / result['total_participants']) * 100, 1)
                    }
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting user league position: {e}")
            return None
    
    async def get_active_leagues(self, league_type: LeagueType = None) -> List[League]:
        """Get active leagues"""
        try:
            async with db_manager.get_connection() as conn:
                if league_type:
                    results = await conn.fetch(
                        """
                        SELECT * FROM leagues 
                        WHERE is_active = TRUE 
                        AND start_date <= CURRENT_DATE 
                        AND end_date >= CURRENT_DATE
                        AND league_type = $1
                        ORDER BY start_date DESC
                        """,
                        league_type.value
                    )
                else:
                    results = await conn.fetch(
                        """
                        SELECT * FROM leagues 
                        WHERE is_active = TRUE 
                        AND start_date <= CURRENT_DATE 
                        AND end_date >= CURRENT_DATE
                        ORDER BY start_date DESC
                        """
                    )
                
                leagues = []
                for row in results:
                    leagues.append(League(
                        league_id=row['league_id'],
                        name=row['name'],
                        tier=LeagueTier(row['tier']),
                        league_type=LeagueType(row['league_type']),
                        start_date=row['start_date'],
                        end_date=row['end_date'],
                        max_participants=row['max_participants'],
                        current_participants=row['current_participants'],
                        entry_requirements=row['entry_requirements'],
                        rewards=row['rewards'],
                        is_active=row['is_active']
                    ))
                
                return leagues
                
        except Exception as e:
            self.logger.error(f"Error getting active leagues: {e}")
            return []
    
    async def distribute_league_rewards(self, league_id: int) -> bool:
        """Distribute rewards for completed league"""
        try:
            async with db_manager.get_connection() as conn:
                # Get league info
                league = await conn.fetchrow(
                    "SELECT * FROM leagues WHERE league_id = $1",
                    league_id
                )
                
                if not league:
                    return False
                
                # Get top participants
                top_participants = await conn.fetch(
                    """
                    SELECT user_id, rank, points
                    FROM league_participants
                    WHERE league_id = $1
                    ORDER BY rank ASC
                    LIMIT 10
                    """,
                    league_id
                )
                
                rewards = league['rewards']
                
                # Distribute rewards
                for participant in top_participants:
                    rank = participant['rank']
                    user_id = participant['user_id']
                    
                    # Determine reward tier
                    if rank == 1 and 'top_1' in rewards:
                        reward = rewards['top_1']
                    elif rank <= 3 and 'top_3' in rewards:
                        reward = rewards['top_3']
                    elif rank <= 10 and 'top_10' in rewards:
                        reward = rewards['top_10']
                    else:
                        continue
                    
                    # Give points reward
                    if 'points' in reward:
                        await conn.execute(
                            """
                            INSERT INTO user_rewards 
                            (user_id, reward_type, reward_value, reward_description, source, created_at)
                            VALUES ($1, 'points', $2, $3, $4, NOW())
                            """,
                            user_id, reward['points'], f"League {league['name']} - Rank {rank}", 'league'
                        )
                    
                    # Give badge reward
                    if 'badge' in reward:
                        await conn.execute(
                            """
                            INSERT INTO user_badges 
                            (user_id, badge_id, earned_at, source)
                            VALUES ($1, $2, NOW(), 'league')
                            """,
                            user_id, reward['badge']
                        )
                    
                    # Log reward distribution
                    await conn.execute(
                        """
                        INSERT INTO league_rewards_log 
                        (league_id, user_id, rank, reward_type, reward_value, distributed_at)
                        VALUES ($1, $2, $3, $4, $5, NOW())
                        """,
                        league_id, user_id, rank, 'league_reward', str(reward)
                    )
                
                self.logger.info(f"Distributed rewards for league {league_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error distributing league rewards: {e}")
            return False
    
    async def get_user_leagues(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all leagues user is participating in"""
        try:
            async with db_manager.get_connection() as conn:
                results = await conn.fetch(
                    """
                    SELECT 
                        l.league_id,
                        l.name,
                        l.tier,
                        l.league_type,
                        l.start_date,
                        l.end_date,
                        l.is_active,
                        lp.rank,
                        lp.points,
                        lp.study_time,
                        lp.tests_completed,
                        lp.accuracy,
                        lp.streak,
                        l.current_participants,
                        l.max_participants
                    FROM leagues l
                    JOIN league_participants lp ON l.league_id = lp.league_id
                    WHERE lp.user_id = $1
                    ORDER BY l.start_date DESC
                    """,
                    user_id
                )
                
                user_leagues = []
                for row in results:
                    user_leagues.append({
                        'league_id': row['league_id'],
                        'name': row['name'],
                        'tier': row['tier'],
                        'league_type': row['league_type'],
                        'start_date': row['start_date'],
                        'end_date': row['end_date'],
                        'is_active': row['is_active'],
                        'rank': row['rank'],
                        'points': row['points'],
                        'study_time': row['study_time'],
                        'tests_completed': row['tests_completed'],
                        'accuracy': round(row['accuracy'], 1),
                        'streak': row['streak'],
                        'current_participants': row['current_participants'],
                        'max_participants': row['max_participants']
                    })
                
                return user_leagues
                
        except Exception as e:
            self.logger.error(f"Error getting user leagues: {e}")
            return []
    
    def _calculate_league_points(
        self, 
        study_time: int, 
        tests_completed: int, 
        accuracy: float, 
        streak: int
    ) -> int:
        """Calculate league points based on various factors"""
        # Base points from study time (1 point per minute)
        time_points = study_time
        
        # Test completion points (10 points per test)
        test_points = tests_completed * 10
        
        # Accuracy bonus (up to 500 points for 100% accuracy)
        accuracy_points = int((accuracy / 100) * 500)
        
        # Streak bonus (up to 200 points for long streaks)
        streak_points = min(streak * 5, 200)
        
        # Calculate total points
        total_points = time_points + test_points + accuracy_points + streak_points
        
        return total_points
    
    async def _get_user_points(self, user_id: int) -> int:
        """Get user's total points"""
        try:
            async with db_manager.get_connection() as conn:
                result = await conn.fetchrow(
                    "SELECT total_points FROM user_levels WHERE user_id = $1",
                    user_id
                )
                
                return result['total_points'] if result else 0
        except Exception as e:
            self.logger.error(f"Error getting user points: {e}")
            return 0


# Global instance
league_service = LeagueService()
