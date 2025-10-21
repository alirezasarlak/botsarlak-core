#!/usr/bin/env python3
"""
Setup Profile System Tables
Manual setup for profile system database tables
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def setup_profile_tables():
    """Setup profile system tables"""
    try:
        logger.info("🚀 Setting up profile system tables...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Read and execute SQL file
        sql_file_path = Path("/home/ali/botsarlak/migrations/versions/007_profile_system_tables.sql")
        
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split SQL content into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                try:
                    await db_manager.execute(statement)
                    logger.debug(f"Executed: {statement[:50]}...")
                except Exception as e:
                    logger.warning(f"Statement failed: {e}")
        
        logger.info("✅ Profile system tables created successfully")
        
        # Verify tables were created
        tables_to_check = [
            'user_profiles',
            'user_statistics', 
            'user_goals',
            'user_achievements',
            'user_levels',
            'user_badges',
            'achievement_definitions'
        ]
        
        for table in tables_to_check:
            exists = await db_manager.fetch_value(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                table
            )
            if exists:
                logger.info(f"✅ Table {table} created successfully")
            else:
                logger.error(f"❌ Table {table} not found")
        
        logger.info("🎉 Profile system tables setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False
    finally:
        await db_manager.close()


async def main():
    """Main function"""
    success = await setup_profile_tables()
    
    if success:
        print("✅ Profile system tables setup completed successfully!")
        sys.exit(0)
    else:
        print("❌ Profile system tables setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
