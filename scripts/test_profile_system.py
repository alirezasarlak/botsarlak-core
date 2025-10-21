#!/usr/bin/env python3
"""
Test Profile System
Test profile system functionality
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.database.connection import db_manager
from src.services.profile_service import profile_service
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def test_profile_system():
    """Test profile system"""
    try:
        logger.info("🚀 Testing profile system...")
        
        # Initialize database
        await db_manager.initialize()
        logger.info("✅ Database initialized")
        
        # Test user ID (your admin ID)
        test_user_id = 7630624621
        
        # Test 1: Check if user exists in users table
        logger.info("🔍 Test 1: Checking if user exists...")
        user_query = "SELECT * FROM users WHERE user_id = $1"
        user_result = await db_manager.fetch_one(user_query, test_user_id)
        
        if user_result:
            logger.info(f"✅ User {test_user_id} exists in users table")
        else:
            logger.info(f"❌ User {test_user_id} not found in users table")
            return False
        
        # Test 2: Check profile tables exist
        logger.info("🔍 Test 2: Checking profile tables...")
        tables_to_check = [
            'user_profiles',
            'user_statistics', 
            'user_levels',
            'user_achievements',
            'user_badges',
            'achievement_definitions'
        ]
        
        for table in tables_to_check:
            exists = await db_manager.fetch_value(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                table
            )
            if exists:
                logger.info(f"✅ Table {table} exists")
            else:
                logger.error(f"❌ Table {table} not found")
                return False
        
        # Test 3: Test profile service
        logger.info("🔍 Test 3: Testing profile service...")
        
        # Get profile
        profile = await profile_service.get_profile(test_user_id)
        if profile:
            logger.info(f"✅ Profile found: {profile.display_name}")
        else:
            logger.info("ℹ️ No profile found, creating initial profile...")
            
            # Create initial profile
            from src.services.profile_service import ProfileData
            profile_data = ProfileData(
                user_id=test_user_id,
                display_name="Test User",
                nickname="test_user",
                privacy_level="friends_only"
            )
            
            success = await profile_service.create_profile(test_user_id, profile_data)
            if success:
                logger.info("✅ Initial profile created")
            else:
                logger.error("❌ Failed to create initial profile")
                return False
        
        # Test 4: Get profile summary
        logger.info("🔍 Test 4: Testing profile summary...")
        profile_summary = await profile_service.get_profile_summary(test_user_id)
        
        if profile_summary:
            logger.info("✅ Profile summary retrieved successfully")
            logger.info(f"Profile: {profile_summary.get('profile')}")
            logger.info(f"Statistics: {profile_summary.get('statistics')}")
            logger.info(f"Level: {profile_summary.get('level')}")
        else:
            logger.error("❌ Failed to get profile summary")
            return False
        
        # Test 5: Test statistics
        logger.info("🔍 Test 5: Testing statistics...")
        statistics = await profile_service.get_statistics(test_user_id)
        
        if statistics:
            logger.info(f"✅ Statistics found: {statistics.total_study_time} minutes")
        else:
            logger.info("ℹ️ No statistics found")
        
        # Test 6: Test level
        logger.info("🔍 Test 6: Testing level...")
        level = await profile_service.get_level(test_user_id)
        
        if level:
            logger.info(f"✅ Level found: {level.current_level} ({level.level_title})")
        else:
            logger.info("ℹ️ No level found")
        
        logger.info("🎉 All profile system tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Profile system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await db_manager.close()


async def main():
    """Main function"""
    success = await test_profile_system()
    
    if success:
        print("✅ Profile system test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Profile system test failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())



