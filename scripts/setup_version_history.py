#!/usr/bin/env python3
"""
Setup Version History Table
Create version history table for tracking deployments
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def setup_version_history():
    """Setup version history table"""
    try:
        logger.info("🚀 Setting up version history table...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Create version_history table
        version_history_sql = """
        CREATE TABLE IF NOT EXISTS version_history (
            id SERIAL PRIMARY KEY,
            version VARCHAR(50) NOT NULL,
            description TEXT,
            deployed_by VARCHAR(100),
            migration_count INTEGER DEFAULT 0,
            deployment_notes TEXT,
            features_added TEXT[],
            features_modified TEXT[],
            features_removed TEXT[],
            breaking_changes TEXT,
            security_updates TEXT[],
            performance_improvements TEXT[],
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        await db_manager.execute(version_history_sql)
        logger.info("✅ Version history table created")
        
        # Create index
        index_sql = "CREATE INDEX IF NOT EXISTS idx_version_history_version ON version_history(version);"
        await db_manager.execute(index_sql)
        logger.info("✅ Version history index created")
        
        # Insert initial version record
        initial_version_sql = """
        INSERT INTO version_history (
            version, 
            description, 
            deployed_by, 
            migration_count, 
            deployment_notes,
            features_added,
            features_modified,
            features_removed,
            breaking_changes,
            security_updates,
            performance_improvements
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11
        );
        """
        
        features_added = [
            "Route Registry System (The Living Map)",
            "Preflight Validation System", 
            "Menu Synchronization System",
            "Data Immortality & User Preservation",
            "Security & Audit System",
            "Scalability & Performance Optimizations",
            "Testing Framework",
            "Professional Deployment Pipeline"
        ]
        
        features_modified = [
            "User persistence system",
            "Error handling",
            "Database connection management",
            "Performance optimization"
        ]
        
        features_removed = []
        
        breaking_changes = "None (backward compatible)"
        
        security_updates = [
            "Comprehensive audit logging",
            "Rate limiting implemented",
            "Suspicious activity detection",
            "Admin access controls",
            "Data integrity guaranteed"
        ]
        
        performance_improvements = [
            "Caching system implemented",
            "Database optimization",
            "Performance monitoring",
            "System metrics tracking"
        ]
        
        await db_manager.execute(
            initial_version_sql,
            "3.0.0",
            "Engineering Contract Implementation Complete - All professional systems implemented",
            "deployment_script",
            6,  # Number of migrations
            "Complete implementation of ChatGPT Engineering Contract with all safety measures, data immortality, and professional deployment pipeline",
            features_added,
            features_modified,
            features_removed,
            breaking_changes,
            security_updates,
            performance_improvements
        )
        
        logger.info("✅ Initial version record inserted")
        logger.info("🎉 Version history table setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False
    finally:
        await db_manager.close()


async def main():
    """Main function"""
    success = await setup_version_history()
    
    if success:
        print("✅ Version history table setup completed successfully!")
        sys.exit(0)
    else:
        print("❌ Version history table setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())



