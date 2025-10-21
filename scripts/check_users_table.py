#!/usr/bin/env python3
"""
Check Users Table
Check users table structure
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def check_users_table():
    """Check users table structure"""
    try:
        logger.info("🔍 Checking users table structure...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Check users table columns
        result = await db_manager.fetch_all(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position"
        )
        
        if result:
            logger.info("✅ users table columns:")
            for row in result:
                logger.info(f"  {row['column_name']}: {row['data_type']}")
        else:
            logger.error("❌ users table not found or empty")
        
        # Check if table exists
        exists = await db_manager.fetch_value(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
        )
        
        if exists:
            logger.info("✅ users table exists")
        else:
            logger.error("❌ users table does not exist")
        
        # Check user data
        user_count = await db_manager.fetch_value("SELECT COUNT(*) FROM users")
        logger.info(f"📊 Total users: {user_count}")
        
        # Check specific user
        test_user_id = 7630624621
        user_data = await db_manager.fetch_one("SELECT * FROM users WHERE user_id = $1", test_user_id)
        
        if user_data:
            logger.info(f"✅ User {test_user_id} found:")
            for key, value in user_data.items():
                logger.info(f"  {key}: {value}")
        else:
            logger.info(f"ℹ️ User {test_user_id} not found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Check failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await db_manager.close()


async def main():
    """Main function"""
    success = await check_users_table()
    
    if success:
        print("✅ Users table check completed!")
        sys.exit(0)
    else:
        print("❌ Users table check failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


