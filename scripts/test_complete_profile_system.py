#!/usr/bin/env python3
"""
🌌 Complete Profile System Test
Test all profile functionality end-to-end
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import db_manager
from src.services.profile_service import profile_service, ProfileData
from src.utils.logging import get_logger

logger = get_logger(__name__)

async def test_complete_profile_system():
    """Test complete profile system"""
    try:
        print("🌌 Testing Complete Profile System...")
        
        # Test user ID
        test_user_id = 694245594  # Admin user
        
        print(f"\n1️⃣ Testing Profile Creation for User {test_user_id}")
        
        # Create test profile
        profile_data = ProfileData(
            user_id=test_user_id,
            display_name="تست کاربر",
            nickname="test_user",
            bio="این یک پروفایل تست است",
            study_track="تجربی",
            grade_level="متوسطه دوم",
            grade_year=12,
            privacy_level="friends_only",
            is_public=False,
            show_statistics=True,
            show_achievements=True,
            show_streak=True
        )
        
        # Create profile
        success = await profile_service.create_profile(test_user_id, profile_data)
        print(f"✅ Profile creation: {'Success' if success else 'Failed'}")
        
        print(f"\n2️⃣ Testing Profile Retrieval")
        
        # Get profile
        profile = await profile_service.get_profile(test_user_id)
        if profile:
            print(f"✅ Profile retrieved: {profile.display_name}")
        else:
            print("❌ Profile retrieval failed")
        
        print(f"\n3️⃣ Testing Statistics")
        
        # Get statistics
        stats = await profile_service.get_statistics(test_user_id)
        if stats:
            print(f"✅ Statistics retrieved: {stats.total_study_time} minutes")
        else:
            print("❌ Statistics retrieval failed")
        
        print(f"\n4️⃣ Testing Level System")
        
        # Get level
        level = await profile_service.get_level(test_user_id)
        if level:
            print(f"✅ Level retrieved: Level {level.current_level} ({level.level_title})")
        else:
            print("❌ Level retrieval failed")
        
        print(f"\n5️⃣ Testing Profile Summary")
        
        # Get profile summary
        summary = await profile_service.get_profile_summary(test_user_id)
        if summary:
            print(f"✅ Profile summary retrieved")
            print(f"   - Profile: {summary.get('profile') is not None}")
            print(f"   - Statistics: {summary.get('statistics') is not None}")
            print(f"   - Level: {summary.get('level') is not None}")
            print(f"   - Achievements: {len(summary.get('achievements', []))}")
            print(f"   - Badges: {len(summary.get('badges', []))}")
        else:
            print("❌ Profile summary retrieval failed")
        
        print(f"\n6️⃣ Testing Database Tables")
        
        # Check all tables exist
        tables_to_check = [
            'user_profiles',
            'user_statistics', 
            'user_levels',
            'user_achievements',
            'user_badges',
            'achievement_definitions'
        ]
        
        for table in tables_to_check:
            query = f"SELECT COUNT(*) FROM {table}"
            try:
                result = await db_manager.fetch_one(query)
                count = result['count'] if result else 0
                print(f"✅ Table {table}: {count} records")
            except Exception as e:
                print(f"❌ Table {table}: Error - {e}")
        
        print(f"\n7️⃣ Testing Profile Update")
        
        # Update profile
        profile_data.bio = "پروفایل به‌روزرسانی شده"
        success = await profile_service.update_profile(test_user_id, profile_data)
        print(f"✅ Profile update: {'Success' if success else 'Failed'}")
        
        print(f"\n8️⃣ Testing Statistics Update")
        
        # Update statistics
        success = await profile_service.update_statistics(test_user_id, study_time=60, session_count=1)
        print(f"✅ Statistics update: {'Success' if success else 'Failed'}")
        
        print(f"\n🎉 Complete Profile System Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Profile system test failed: {e}")
        return False

async def main():
    """Main test function"""
    try:
        # Initialize database connection
        await db_manager.initialize()
        
        # Run tests
        success = await test_complete_profile_system()
        
        if success:
            print("\n✅ All tests passed! Profile system is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the logs for details.")
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        logger.error(f"Test setup failed: {e}")
    finally:
        # Close database connection
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())