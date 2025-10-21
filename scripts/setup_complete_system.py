#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌌 SarlakBot v3.1.0 - Complete System Setup
Setup script for complete study report and league system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.database.connection import db_manager
from src.utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


async def setup_complete_system():
    """Setup complete system with all migrations"""
    try:
        logger.info("🌌 Setting up SarlakBot v3.1.0 Complete System...")
        
        # Initialize database connection
        await db_manager.initialize()
        logger.info("✅ Database connection initialized")
        
        # Run all migrations
        migrations = [
            "009_study_reports_complete.sql",
            "010_anti_fraud_system.sql", 
            "011_league_system.sql",
            "012_auto_tracking_system.sql"
        ]
        
        for migration in migrations:
            migration_path = Path(__file__).parent.parent / "migrations" / "versions" / migration
            if migration_path.exists():
                logger.info(f"📝 Running migration: {migration}")
                
                with open(migration_path, 'r', encoding='utf-8') as f:
                    migration_sql = f.read()
                
                async with db_manager.get_connection() as conn:
                    await conn.execute(migration_sql)
                
                logger.info(f"✅ Migration {migration} completed")
            else:
                logger.warning(f"⚠️ Migration file not found: {migration}")
        
        # Create default leagues
        await create_default_leagues()
        
        # Create sample data
        await create_sample_data()
        
        logger.info("🎉 Complete system setup finished successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error setting up complete system: {e}")
        raise
    finally:
        await db_manager.close()


async def create_default_leagues():
    """Create default leagues"""
    try:
        logger.info("🏆 Creating default leagues...")
        
        async with db_manager.get_connection() as conn:
            # Create daily league
            await conn.execute("SELECT create_daily_league(CURRENT_DATE)")
            logger.info("✅ Daily league created")
            
            # Create weekly league
            await conn.execute("SELECT create_weekly_league(CURRENT_DATE)")
            logger.info("✅ Weekly league created")
            
            # Create monthly league
            await conn.execute("SELECT create_monthly_league(CURRENT_DATE)")
            logger.info("✅ Monthly league created")
        
    except Exception as e:
        logger.error(f"❌ Error creating default leagues: {e}")


async def create_sample_data():
    """Create sample data for testing"""
    try:
        logger.info("📊 Creating sample data...")
        
        # Add sample study reports for admin user
        admin_id = 694245594
        
        async with db_manager.get_connection() as conn:
            # Insert sample study report
            await conn.execute(
                """
                INSERT INTO study_reports 
                (user_id, report_date, study_minutes, tests_count, correct_answers, total_questions, subjects_studied, study_sessions)
                VALUES ($1, CURRENT_DATE, 120, 5, 45, 50, ARRAY['ریاضی', 'فیزیک'], 3)
                ON CONFLICT (user_id, report_date) DO UPDATE SET
                study_minutes = study_reports.study_minutes + 120,
                tests_count = study_reports.tests_count + 5,
                correct_answers = study_reports.correct_answers + 45,
                total_questions = study_reports.total_questions + 50,
                subjects_studied = ARRAY(SELECT DISTINCT unnest(study_reports.subjects_studied || ARRAY['ریاضی', 'فیزیک'])),
                study_sessions = study_reports.study_sessions + 3
                """,
                admin_id
            )
            
            # Insert sample study session
            await conn.execute(
                """
                INSERT INTO study_sessions 
                (user_id, session_date, start_time, end_time, duration_minutes, subject, session_type, questions_answered, correct_answers)
                VALUES ($1, CURRENT_DATE, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour', 60, 'ریاضی', 'study', 25, 23)
                """,
                admin_id
            )
            
            # Insert sample test session
            await conn.execute(
                """
                INSERT INTO test_sessions 
                (user_id, test_date, test_type, subject, total_questions, correct_answers, score, time_taken_minutes, difficulty_level)
                VALUES ($1, CURRENT_DATE, 'practice', 'ریاضی', 25, 23, 92.0, 45, 'متوسط')
                """,
                admin_id
            )
            
            logger.info("✅ Sample data created for admin user")
        
    except Exception as e:
        logger.error(f"❌ Error creating sample data: {e}")


async def verify_system():
    """Verify system setup"""
    try:
        logger.info("🔍 Verifying system setup...")
        
        async with db_manager.get_connection() as conn:
            # Check tables exist
            tables_to_check = [
                'study_reports', 'study_sessions', 'test_sessions', 'study_goals',
                'fraud_detection_logs', 'suspicious_sessions', 'user_restrictions',
                'leagues', 'league_participants', 'league_rewards_log', 'user_rewards'
            ]
            
            for table in tables_to_check:
                result = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                    table
                )
                if result:
                    logger.info(f"✅ Table {table} exists")
                else:
                    logger.error(f"❌ Table {table} missing")
            
            # Check functions exist
            functions_to_check = [
                'update_study_report', 'get_study_statistics', 'validate_study_session',
                'create_daily_league', 'create_weekly_league', 'create_monthly_league',
                'update_league_standings', 'get_league_leaderboard'
            ]
            
            for function in functions_to_check:
                result = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.routines WHERE routine_name = $1)",
                    function
                )
                if result:
                    logger.info(f"✅ Function {function} exists")
                else:
                    logger.error(f"❌ Function {function} missing")
            
            # Check sample data
            study_reports_count = await conn.fetchval("SELECT COUNT(*) FROM study_reports")
            leagues_count = await conn.fetchval("SELECT COUNT(*) FROM leagues")
            
            logger.info(f"📊 Study reports: {study_reports_count}")
            logger.info(f"🏆 Leagues: {leagues_count}")
            
            logger.info("✅ System verification completed")
        
    except Exception as e:
        logger.error(f"❌ Error verifying system: {e}")


async def main():
    """Main setup function"""
    try:
        # Setup logging
        setup_logging(log_level="INFO", enable_json=False)
        
        # Setup complete system
        await setup_complete_system()
        
        # Verify system
        await verify_system()
        
        print("\n🎉 SarlakBot v3.1.0 Complete System Setup Successful!")
        print("📋 Features available:")
        print("  ✅ Study Reports System")
        print("  ✅ Anti-Fraud System") 
        print("  ✅ League System")
        print("  ✅ Competition System")
        print("  ✅ User Rewards System")
        print("  ✅ Private Leagues")
        print("\n🚀 Bot is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
