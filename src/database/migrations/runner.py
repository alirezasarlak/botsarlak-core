"""
🌌 SarlakBot v3.0 - Database Migration Runner
Professional database migration system with version tracking
"""

import asyncio
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


class MigrationRunner:
    """
    🌌 Professional Migration Runner
    Handles database migrations with version tracking and rollback support
    """
    
    def __init__(self):
        self.logger = logger
        self.migrations_dir = Path(__file__).parent
        self.applied_migrations: List[str] = []
    
    async def initialize(self) -> None:
        """Initialize migration system"""
        try:
            self.logger.info("🌌 Initializing migration system...")
            
            # Ensure schema_versions table exists
            await self._ensure_version_table()
            
            # Get applied migrations
            await self._load_applied_migrations()
            
            self.logger.info("✅ Migration system initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Migration system initialization failed: {e}")
            raise
    
    async def _ensure_version_table(self) -> None:
        """Ensure schema_versions table exists"""
        try:
            await db_manager.execute("""
                CREATE TABLE IF NOT EXISTS schema_versions (
                    version VARCHAR(20) PRIMARY KEY,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            self.logger.debug("✅ Schema versions table ensured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to ensure version table: {e}")
            raise
    
    async def _load_applied_migrations(self) -> None:
        """Load list of applied migrations"""
        try:
            migrations = await db_manager.fetch_all("""
                SELECT version FROM schema_versions 
                ORDER BY applied_at
            """)
            
            self.applied_migrations = [m['version'] for m in migrations]
            
            self.logger.info(f"📋 Loaded {len(self.applied_migrations)} applied migrations")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load applied migrations: {e}")
            raise
    
    async def get_pending_migrations(self) -> List[str]:
        """Get list of pending migrations"""
        try:
            # Get all migration files
            migration_files = []
            for file_path in self.migrations_dir.glob("*.sql"):
                if file_path.name.startswith("001_"):  # Skip initial schema
                    continue
                version = file_path.stem
                migration_files.append(version)
            
            # Sort by version
            migration_files.sort()
            
            # Filter out applied migrations
            pending = [m for m in migration_files if m not in self.applied_migrations]
            
            self.logger.info(f"📋 Found {len(pending)} pending migrations")
            
            return pending
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get pending migrations: {e}")
            return []
    
    async def run_migration(self, version: str) -> bool:
        """
        Run a specific migration
        
        Args:
            version: Migration version to run
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"🚀 Running migration: {version}")
            
            # Check if already applied
            if version in self.applied_migrations:
                self.logger.warning(f"⚠️ Migration {version} already applied")
                return True
            
            # Read migration file
            migration_file = self.migrations_dir / f"{version}.sql"
            if not migration_file.exists():
                self.logger.error(f"❌ Migration file not found: {migration_file}")
                return False
            
            # Read SQL content
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Split into individual statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            # Run migration in transaction
            async with db_manager.transaction() as conn:
                for statement in statements:
                    if statement:
                        await conn.execute(statement)
                        self.logger.debug(f"📝 Executed: {statement[:100]}...")
                
                # Record migration as applied
                await conn.execute("""
                    INSERT INTO schema_versions (version, description, applied_at)
                    VALUES ($1, $2, $3)
                """, version, f"Migration {version}", datetime.now())
            
            # Update applied migrations list
            self.applied_migrations.append(version)
            
            self.logger.info(f"✅ Migration {version} completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Migration {version} failed: {e}")
            return False
    
    async def run_all_pending_migrations(self) -> bool:
        """
        Run all pending migrations
        
        Returns:
            True if all successful, False otherwise
        """
        try:
            self.logger.info("🚀 Running all pending migrations...")
            
            pending = await self.get_pending_migrations()
            
            if not pending:
                self.logger.info("✅ No pending migrations")
                return True
            
            success_count = 0
            for version in pending:
                if await self.run_migration(version):
                    success_count += 1
                else:
                    self.logger.error(f"❌ Migration {version} failed, stopping")
                    break
            
            if success_count == len(pending):
                self.logger.info(f"✅ All {success_count} migrations completed successfully")
                return True
            else:
                self.logger.error(f"❌ Only {success_count}/{len(pending)} migrations completed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Run all migrations failed: {e}")
            return False
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """
        Get migration status information
        
        Returns:
            Dictionary with migration status
        """
        try:
            # Get applied migrations
            applied = await db_manager.fetch_all("""
                SELECT version, description, applied_at
                FROM schema_versions 
                ORDER BY applied_at DESC
            """)
            
            # Get pending migrations
            pending = await self.get_pending_migrations()
            
            return {
                'applied_count': len(applied),
                'pending_count': len(pending),
                'applied_migrations': applied,
                'pending_migrations': pending,
                'last_migration': applied[0] if applied else None,
                'status': 'up_to_date' if not pending else 'pending'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get migration status failed: {e}")
            return {
                'applied_count': 0,
                'pending_count': 0,
                'applied_migrations': [],
                'pending_migrations': [],
                'last_migration': None,
                'status': 'error'
            }
    
    async def rollback_migration(self, version: str) -> bool:
        """
        Rollback a specific migration (if rollback file exists)
        
        Args:
            version: Migration version to rollback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"🔄 Rolling back migration: {version}")
            
            # Check if migration was applied
            if version not in self.applied_migrations:
                self.logger.warning(f"⚠️ Migration {version} not applied")
                return True
            
            # Look for rollback file
            rollback_file = self.migrations_dir / f"{version}_rollback.sql"
            if not rollback_file.exists():
                self.logger.error(f"❌ Rollback file not found: {rollback_file}")
                return False
            
            # Read rollback SQL
            with open(rollback_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Split into statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            # Run rollback in transaction
            async with db_manager.transaction() as conn:
                for statement in statements:
                    if statement:
                        await conn.execute(statement)
                        self.logger.debug(f"📝 Rollback executed: {statement[:100]}...")
                
                # Remove migration record
                await conn.execute("""
                    DELETE FROM schema_versions WHERE version = $1
                """, version)
            
            # Update applied migrations list
            self.applied_migrations.remove(version)
            
            self.logger.info(f"✅ Migration {version} rolled back successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Rollback migration {version} failed: {e}")
            return False
    
    async def reset_database(self) -> bool:
        """
        Reset database to initial state (DANGEROUS!)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.warning("⚠️ Resetting database to initial state...")
            
            # Get all tables
            tables = await db_manager.fetch_all("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename != 'schema_versions'
            """)
            
            # Drop all tables
            async with db_manager.transaction() as conn:
                for table in tables:
                    await conn.execute(f"DROP TABLE IF EXISTS {table['tablename']} CASCADE")
                    self.logger.debug(f"🗑️ Dropped table: {table['tablename']}")
                
                # Clear migration history
                await conn.execute("DELETE FROM schema_versions")
            
            # Reset applied migrations
            self.applied_migrations = []
            
            self.logger.warning("✅ Database reset completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Database reset failed: {e}")
            return False


# Global migration runner instance
migration_runner = MigrationRunner()


async def run_migrations() -> bool:
    """
    Run all pending migrations
    
    Returns:
        True if successful, False otherwise
    """
    try:
        await migration_runner.initialize()
        return await migration_runner.run_all_pending_migrations()
    except Exception as e:
        logger.error(f"❌ Run migrations failed: {e}")
        return False


async def get_migration_status() -> Dict[str, Any]:
    """
    Get migration status
    
    Returns:
        Migration status dictionary
    """
    try:
        await migration_runner.initialize()
        return await migration_runner.get_migration_status()
    except Exception as e:
        logger.error(f"❌ Get migration status failed: {e}")
        return {'status': 'error', 'error': str(e)}


if __name__ == "__main__":
    # Run migrations if called directly
    async def main():
        success = await run_migrations()
        if success:
            print("✅ Migrations completed successfully")
        else:
            print("❌ Migrations failed")
            exit(1)
    
    asyncio.run(main())




