#!/usr/bin/env python3
"""
Check users in database
"""

import asyncio
import sys
sys.path.append('src')
from src.database.connection import db_manager
from src.database.user_queries import UserQueries

async def check_users():
    try:
        await db_manager.initialize()
        conn = await db_manager.pool.acquire()
        user_queries = UserQueries(conn)
        
        # Get all users
        users = await user_queries.get_users_with_onboarding_completed()
        print(f'Users with completed onboarding: {len(users)}')
        
        for user in users[:5]:  # Show first 5 users
            print(f'User {user["user_id"]}: {user.get("nickname", "No nickname")} - {user.get("real_name", "No name")}')
        
        await db_manager.pool.release(conn)
        await db_manager.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_users())



