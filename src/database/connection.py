"""
🌌 SarlakBot v3.0 - Database Connection Management
Professional async database handling with connection pooling
"""

import asyncio
import asyncpg
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from src.config import config
from src.utils.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """
    🌌 Professional Database Manager
    Handles all database operations with connection pooling and error handling
    """
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.connection_string = config.database.connection_string
        self.logger = logger
    
    async def initialize(self) -> None:
        """Initialize database connection pool"""
        try:
            self.logger.info("🌌 Initializing database connection pool...")
            
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=5,
                max_size=20,
                command_timeout=60,
                server_settings={
                    'application_name': 'SarlakBot_v3',
                    'timezone': 'Asia/Tehran'
                }
            )
            
            # Test connection
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")
            
            self.logger.info("✅ Database connection pool initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    async def close(self) -> None:
        """Close database connection pool"""
        if self.pool:
            self.logger.info("🛑 Closing database connection pool...")
            await self.pool.close()
            self.logger.info("✅ Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, *args) -> str:
        """
        Execute a query without returning results
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Status message
        """
        try:
            async with self.get_connection() as conn:
                result = await conn.execute(query, *args)
                self.logger.debug(f"📝 Executed query: {query[:100]}...")
                return result
        except Exception as e:
            self.logger.error(f"❌ Query execution failed: {e}")
            raise
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """
        Fetch one row from database
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Dictionary with row data or None
        """
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(query, *args)
                if row:
                    return dict(row)
                return None
        except Exception as e:
            self.logger.error(f"❌ Fetch one failed: {e}")
            raise
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """
        Fetch all rows from database
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            List of dictionaries with row data
        """
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"❌ Fetch all failed: {e}")
            raise
    
    async def fetch_value(self, query: str, *args) -> Any:
        """
        Fetch single value from database
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Single value or None
        """
        try:
            async with self.get_connection() as conn:
                value = await conn.fetchval(query, *args)
                return value
        except Exception as e:
            self.logger.error(f"❌ Fetch value failed: {e}")
            raise
    
    async def transaction(self):
        """Get database transaction context manager"""
        async with self.get_connection() as conn:
            async with conn.transaction():
                yield conn
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check database health
        
        Returns:
            Health status dictionary
        """
        try:
            async with self.get_connection() as conn:
                # Test basic connectivity
                await conn.execute("SELECT 1")
                
                # Get connection pool stats
                pool_stats = {
                    'size': self.pool.get_size(),
                    'idle_size': self.pool.get_idle_size(),
                    'max_size': self.pool.get_max_size()
                }
                
                # Get database info
                db_info = await conn.fetchrow("""
                    SELECT 
                        current_database() as database_name,
                        version() as version,
                        current_user as current_user
                """)
                
                return {
                    'status': 'healthy',
                    'pool_stats': pool_stats,
                    'database_info': dict(db_info) if db_info else {},
                    'timestamp': asyncio.get_event_loop().time()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': asyncio.get_event_loop().time()
            }


# Global database manager instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager




