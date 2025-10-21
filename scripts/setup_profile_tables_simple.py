#!/usr/bin/env python3
"""
Setup Profile System Tables - Simple Version
Manual setup for profile system database tables
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def setup_profile_tables():
    """Setup profile system tables"""
    try:
        logger.info("🚀 Setting up profile system tables...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Create user_profiles table
        user_profiles_sql = """
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
            display_name VARCHAR(100),
            nickname VARCHAR(50),
            bio TEXT,
            avatar_url TEXT,
            phone_number VARCHAR(20),
            birth_date DATE,
            study_track VARCHAR(50),
            grade_level VARCHAR(20),
            grade_year INTEGER,
            privacy_level VARCHAR(20) DEFAULT 'friends_only',
            is_public BOOLEAN DEFAULT FALSE,
            show_statistics BOOLEAN DEFAULT TRUE,
            show_achievements BOOLEAN DEFAULT TRUE,
            show_streak BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        await db_manager.execute(user_profiles_sql)
        logger.info("✅ user_profiles table created")
        
        # Create user_statistics table
        user_statistics_sql = """
        CREATE TABLE IF NOT EXISTS user_statistics (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            total_study_time INTEGER DEFAULT 0,
            daily_study_time INTEGER DEFAULT 0,
            weekly_study_time INTEGER DEFAULT 0,
            monthly_study_time INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            total_sessions INTEGER DEFAULT 0,
            completed_goals INTEGER DEFAULT 0,
            total_goals INTEGER DEFAULT 0,
            study_days INTEGER DEFAULT 0,
            last_study_date DATE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id)
        );
        """
        
        await db_manager.execute(user_statistics_sql)
        logger.info("✅ user_statistics table created")
        
        # Create user_levels table
        user_levels_sql = """
        CREATE TABLE IF NOT EXISTS user_levels (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            current_level INTEGER DEFAULT 1,
            total_points INTEGER DEFAULT 0,
            level_points INTEGER DEFAULT 0,
            next_level_points INTEGER DEFAULT 100,
            level_title VARCHAR(50) DEFAULT 'مبتدی',
            level_color VARCHAR(20) DEFAULT '#4CAF50',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(user_id)
        );
        """
        
        await db_manager.execute(user_levels_sql)
        logger.info("✅ user_levels table created")
        
        # Create user_achievements table
        user_achievements_sql = """
        CREATE TABLE IF NOT EXISTS user_achievements (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            achievement_id VARCHAR(100) NOT NULL,
            achievement_name VARCHAR(100) NOT NULL,
            achievement_description TEXT,
            achievement_type VARCHAR(50) NOT NULL,
            achievement_category VARCHAR(50) NOT NULL,
            points_awarded INTEGER DEFAULT 0,
            badge_icon VARCHAR(20),
            unlocked_at TIMESTAMPTZ DEFAULT NOW(),
            is_featured BOOLEAN DEFAULT FALSE,
            UNIQUE(user_id, achievement_id)
        );
        """
        
        await db_manager.execute(user_achievements_sql)
        logger.info("✅ user_achievements table created")
        
        # Create user_badges table
        user_badges_sql = """
        CREATE TABLE IF NOT EXISTS user_badges (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            badge_id VARCHAR(100) NOT NULL,
            badge_name VARCHAR(100) NOT NULL,
            badge_description TEXT,
            badge_icon VARCHAR(20),
            badge_color VARCHAR(20),
            earned_at TIMESTAMPTZ DEFAULT NOW(),
            is_displayed BOOLEAN DEFAULT TRUE,
            UNIQUE(user_id, badge_id)
        );
        """
        
        await db_manager.execute(user_badges_sql)
        logger.info("✅ user_badges table created")
        
        # Create achievement_definitions table
        achievement_definitions_sql = """
        CREATE TABLE IF NOT EXISTS achievement_definitions (
            id SERIAL PRIMARY KEY,
            achievement_id VARCHAR(100) UNIQUE NOT NULL,
            achievement_name VARCHAR(100) NOT NULL,
            achievement_description TEXT,
            achievement_type VARCHAR(50) NOT NULL,
            achievement_category VARCHAR(50) NOT NULL,
            points_awarded INTEGER DEFAULT 0,
            badge_icon VARCHAR(20),
            requirements JSONB NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        await db_manager.execute(achievement_definitions_sql)
        logger.info("✅ achievement_definitions table created")
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_statistics_user_id ON user_statistics(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_levels_user_id ON user_levels(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_badges_user_id ON user_badges(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_achievement_definitions_id ON achievement_definitions(achievement_id);"
        ]
        
        for index_sql in indexes:
            await db_manager.execute(index_sql)
        
        logger.info("✅ Indexes created")
        
        # Insert initial achievement definitions
        achievements = [
            ("study_1_hour", "اولین ساعت مطالعه", "اولین ساعت مطالعه خود را تکمیل کنید", "study", "bronze", 10, "⏰", '{"total_study_time": 60}'),
            ("study_10_hours", "10 ساعت مطالعه", "10 ساعت مطالعه کنید", "study", "silver", 50, "📚", '{"total_study_time": 600}'),
            ("streak_3_days", "3 روز متوالی", "3 روز متوالی مطالعه کنید", "streak", "bronze", 15, "🔥", '{"current_streak": 3}'),
            ("streak_7_days", "یک هفته متوالی", "7 روز متوالی مطالعه کنید", "streak", "silver", 50, "🔥", '{"current_streak": 7}')
        ]
        
        for achievement in achievements:
            achievement_sql = """
                INSERT INTO achievement_definitions (
                    achievement_id, achievement_name, achievement_description,
                    achievement_type, achievement_category, points_awarded, badge_icon, requirements
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (achievement_id) DO NOTHING
            """
            
            await db_manager.execute(achievement_sql, *achievement)
        
        logger.info("✅ Initial achievements inserted")
        
        logger.info("🎉 Profile system tables setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False
    finally:
        await db_manager.close()


async def main():
    """Main function"""
    success = await setup_profile_tables()
    
    if success:
        print("✅ Profile system tables setup completed successfully!")
        sys.exit(0)
    else:
        print("❌ Profile system tables setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())



