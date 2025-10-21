#!/usr/bin/env python3
"""
🌌 Create Admin Profile
Create profile for admin user
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import db_manager
from src.services.profile_service import profile_service, ProfileData
from src.utils.logging import get_logger

logger = get_logger(__name__)

async def create_admin_profile():
    """Create profile for admin user"""
    try:
        print("🌌 Creating Admin Profile...")
        
        # Admin user ID
        admin_user_id = 694245594
        
        # Create profile data
        profile_data = ProfileData(
            user_id=admin_user_id,
            display_name="Alireza",
            nickname="ar_slk98",
            bio="مدیر سیستم ربات سرلک",
            study_track="تجربی",
            grade_level="متوسطه دوم",
            grade_year=12,
            privacy_level="friends_only",
            is_public=True,
            show_statistics=True,
            show_achievements=True,
            show_streak=True
        )
        
        # Check if profile already exists
        existing_profile = await profile_service.get_profile(admin_user_id)
        if existing_profile:
            print("✅ Profile already exists, updating...")
            success = await profile_service.update_profile(admin_user_id, profile_data)
        else:
            print("✅ Creating new profile...")
            success = await profile_service.create_profile(admin_user_id, profile_data)
        
        if success:
            print("✅ Admin profile created/updated successfully!")
            
            # Test profile summary
            summary = await profile_service.get_profile_summary(admin_user_id)
            if summary:
                print("✅ Profile summary works!")
                profile = summary.get('profile')
                if profile:
                    print(f"   - Name: {profile.display_name}")
                    print(f"   - Nickname: {profile.nickname}")
                    print(f"   - Bio: {profile.bio}")
            else:
                print("❌ Profile summary failed")
        else:
            print("❌ Profile creation/update failed")
        
        return success
        
    except Exception as e:
        print(f"❌ Failed to create admin profile: {e}")
        logger.error(f"Admin profile creation failed: {e}")
        return False

async def main():
    """Main function"""
    try:
        # Initialize database connection
        await db_manager.initialize()
        
        # Create admin profile
        success = await create_admin_profile()
        
        if success:
            print("\n🎉 Admin profile setup completed successfully!")
        else:
            print("\n❌ Admin profile setup failed.")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        logger.error(f"Setup failed: {e}")
    finally:
        # Close database connection
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())

