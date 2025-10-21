#!/usr/bin/env python3
"""
🌌 Debug Profile Issue
Debug why profile service is not working
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import db_manager
from src.services.profile_service import profile_service
from src.utils.logging import get_logger

logger = get_logger(__name__)

async def debug_profile_issue():
    """Debug profile service issue"""
    try:
        print("🌌 Debugging Profile Issue...")
        
        # Initialize database
        await db_manager.initialize()
        
        user_id = 694245594
        
        print(f"\n1️⃣ Testing Direct Database Query")
        
        # Test direct database query
        try:
            result = await db_manager.fetch_one("SELECT * FROM user_profiles WHERE user_id = $1", user_id)
            if result:
                print(f"✅ Direct query works: {result['display_name']}")
            else:
                print("❌ Direct query: No result")
        except Exception as e:
            print(f"❌ Direct query failed: {e}")
        
        print(f"\n2️⃣ Testing Profile Service")
        
        # Test profile service
        try:
            profile = await profile_service.get_profile(user_id)
            if profile:
                print(f"✅ Profile service works: {profile.display_name}")
            else:
                print("❌ Profile service: No result")
        except Exception as e:
            print(f"❌ Profile service failed: {e}")
        
        print(f"\n3️⃣ Testing Statistics Service")
        
        # Test statistics service
        try:
            stats = await profile_service.get_statistics(user_id)
            if stats:
                print(f"✅ Statistics service works: {stats.total_study_time}")
            else:
                print("❌ Statistics service: No result")
        except Exception as e:
            print(f"❌ Statistics service failed: {e}")
        
        print(f"\n4️⃣ Testing Level Service")
        
        # Test level service
        try:
            level = await profile_service.get_level(user_id)
            if level:
                print(f"✅ Level service works: {level.current_level}")
            else:
                print("❌ Level service: No result")
        except Exception as e:
            print(f"❌ Level service failed: {e}")
        
        print(f"\n5️⃣ Testing Profile Summary")
        
        # Test profile summary
        try:
            summary = await profile_service.get_profile_summary(user_id)
            if summary:
                print(f"✅ Profile summary works")
                print(f"   - Profile: {summary.get('profile') is not None}")
                print(f"   - Statistics: {summary.get('statistics') is not None}")
                print(f"   - Level: {summary.get('level') is not None}")
            else:
                print("❌ Profile summary: No result")
        except Exception as e:
            print(f"❌ Profile summary failed: {e}")
        
        print(f"\n6️⃣ Checking Database Tables")
        
        # Check if tables exist and have data
        tables = ['user_profiles', 'user_statistics', 'user_levels']
        for table in tables:
            try:
                result = await db_manager.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                count = result['count'] if result else 0
                print(f"✅ Table {table}: {count} records")
            except Exception as e:
                print(f"❌ Table {table}: Error - {e}")
        
        print(f"\n🎉 Debug completed!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        logger.error(f"Debug failed: {e}")
    finally:
        await db_manager.close()

async def main():
    """Main function"""
    await debug_profile_issue()

if __name__ == "__main__":
    asyncio.run(main())