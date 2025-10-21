#!/usr/bin/env python3
"""
Test database query - all records
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import db_manager

async def test():
    try:
        await db_manager.initialize()
        
        # Test without parameters
        result = await db_manager.fetch_all("SELECT * FROM user_profiles")
        if result:
            print(f"✅ All records query works: {len(result)} records")
            for record in result:
                print(f"   - user_id: {record['user_id']}, name: {record['display_name']}")
        else:
            print("❌ All records query failed")
        
        await db_manager.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())

