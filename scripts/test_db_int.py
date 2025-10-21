#!/usr/bin/env python3
"""
Test database query with int parameter
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import db_manager

async def test():
    try:
        await db_manager.initialize()
        
        # Test with int parameter
        result = await db_manager.fetch_one("SELECT * FROM user_profiles WHERE user_id = $1", 694245594)
        if result:
            print(f"✅ Int parameter works: {result['display_name']}")
        else:
            print("❌ Int parameter failed")
        
        await db_manager.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())

