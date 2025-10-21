#!/usr/bin/env python3
"""
Check Profile Tables
Check profile tables structure
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def check_profile_tables():
    """Check profile tables structure"""
    try:
        logger.info("🔍 Checking profile tables structure...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Check user_profiles table
        logger.info("📋 Checking user_profiles table...")
        result = await db_manager.fetch_all(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_profiles' ORDER BY ordinal_position"
        )
        
        if result:
            logger.info("✅ user_profiles table columns:")
            for row in result:
                logger.info(f"  {row['column_name']}: {row['data_type']}")
        else:
            logger.error("❌ user_profiles table not found or empty")
        
        # Check if table exists
        exists = await db_manager.fetch_value(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_profiles')"
        )
        
        if exists:
            logger.info("✅ user_profiles table exists")
        else:
            logger.error("❌ user_profiles table does not exist")
        
        # Check other tables
        tables = ['user_statistics', 'user_levels', 'user_achievements', 'user_badges', 'achievement_definitions']
        
        for table in tables:
            exists = await db_manager.fetch_value(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                table
            )
            
            if exists:
                logger.info(f"✅ {table} table exists")
            else:
                logger.error(f"❌ {table} table does not exist")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Check failed: {e}")
        return False
    finally:
        await db_manager.close()


async def main():
    """Main function"""
    success = await check_profile_tables()
    
    if success:
        print("✅ Profile tables check completed!")
        sys.exit(0)
    else:
        print("❌ Profile tables check failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())



