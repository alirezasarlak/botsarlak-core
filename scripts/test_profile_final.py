#!/usr/bin/env python3
"""
Test profile system final
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import db_manager
from src.services.profile_service import profile_service

async def test():
    try:
        await db_manager.initialize()
        
        # Test profile summary
        summary = await profile_service.get_profile_summary(694245594)
        if summary and summary.get('profile'):
            profile = summary['profile']
            print(f"✅ Profile summary works: {profile.display_name}")
            print(f"   - Statistics: {summary.get('statistics') is not None}")
            print(f"   - Level: {summary.get('level') is not None}")
            print(f"   - Achievements: {len(summary.get('achievements', []))}")
            print(f"   - Badges: {len(summary.get('badges', []))}")
        else:
            print("❌ Profile summary failed")
        
        await db_manager.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())

