#!/usr/bin/env python3
"""
Setup Audit Logs Table
Manual setup for audit logs database table
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def setup_audit_tables():
    """Setup audit logs table"""
    try:
        logger.info("🚀 Setting up audit logs table...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Create audit_logs table
        audit_logs_sql = """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
            action VARCHAR(100) NOT NULL,
            resource VARCHAR(255) NOT NULL,
            details JSONB DEFAULT '{}',
            ip_address INET,
            user_agent TEXT,
            security_level VARCHAR(20) DEFAULT 'info',
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        await db_manager.execute(audit_logs_sql)
        logger.info("✅ Audit logs table created")
        
        # Create indexes
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_security_level ON audit_logs(security_level);",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource);",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_ip_address ON audit_logs(ip_address);",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_action ON audit_logs(user_id, action);",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_created ON audit_logs(user_id, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_action_created ON audit_logs(action, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_security_created ON audit_logs(security_level, created_at);"
        ]
        
        for index_sql in indexes_sql:
            await db_manager.execute(index_sql)
        
        logger.info("✅ Audit logs indexes created")
        
        # Create cleanup function
        cleanup_function_sql = """
        CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
        RETURNS INTEGER AS $$
        DECLARE
            deleted_count INTEGER;
        BEGIN
            -- Delete logs older than 90 days
            DELETE FROM audit_logs 
            WHERE created_at < NOW() - INTERVAL '90 days';
            
            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            
            -- Log the cleanup action
            INSERT INTO audit_logs (user_id, action, resource, details, security_level)
            VALUES (
                NULL,
                'system_event',
                'audit_cleanup',
                jsonb_build_object('deleted_count', deleted_count, 'retention_days', 90),
                'info'
            );
            
            RETURN deleted_count;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        await db_manager.execute(cleanup_function_sql)
        logger.info("✅ Cleanup function created")
        
        # Create security views
        security_violations_view_sql = """
        CREATE OR REPLACE VIEW security_violations AS
        SELECT 
            user_id,
            action,
            resource,
            details,
            ip_address,
            created_at
        FROM audit_logs 
        WHERE security_level IN ('error', 'critical') 
           OR action = 'security_violation'
        ORDER BY created_at DESC;
        """
        
        await db_manager.execute(security_violations_view_sql)
        logger.info("✅ Security violations view created")
        
        user_activity_view_sql = """
        CREATE OR REPLACE VIEW user_activity_summary AS
        SELECT 
            user_id,
            COUNT(*) as total_actions,
            COUNT(DISTINCT action) as unique_actions,
            COUNT(DISTINCT DATE(created_at)) as active_days,
            MIN(created_at) as first_activity,
            MAX(created_at) as last_activity
        FROM audit_logs 
        WHERE user_id IS NOT NULL
        GROUP BY user_id
        ORDER BY total_actions DESC;
        """
        
        await db_manager.execute(user_activity_view_sql)
        logger.info("✅ User activity summary view created")
        
        daily_stats_view_sql = """
        CREATE OR REPLACE VIEW daily_activity_stats AS
        SELECT 
            DATE(created_at) as activity_date,
            COUNT(*) as total_events,
            COUNT(DISTINCT user_id) as unique_users,
            COUNT(CASE WHEN security_level = 'critical' THEN 1 END) as critical_events,
            COUNT(CASE WHEN security_level = 'error' THEN 1 END) as error_events,
            COUNT(CASE WHEN security_level = 'warning' THEN 1 END) as warning_events
        FROM audit_logs 
        GROUP BY DATE(created_at)
        ORDER BY activity_date DESC;
        """
        
        await db_manager.execute(daily_stats_view_sql)
        logger.info("✅ Daily activity stats view created")
        
        # Insert initial audit log
        initial_log_sql = """
        INSERT INTO audit_logs (action, resource, details, security_level)
        VALUES (
            'system_event',
            'audit_system_init',
            jsonb_build_object(
                'version', '3.0.0',
                'description', 'Audit logging system initialized',
                'features', jsonb_build_array(
                    'rate_limiting',
                    'suspicious_activity_detection',
                    'security_summary',
                    'automatic_cleanup'
                )
            ),
            'info'
        );
        """
        
        await db_manager.execute(initial_log_sql)
        logger.info("✅ Initial audit log inserted")
        
        logger.info("🎉 Audit logs table setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False
    finally:
        await db_manager.close()


async def main():
    """Main function"""
    success = await setup_audit_tables()
    
    if success:
        print("✅ Audit logs table setup completed successfully!")
        sys.exit(0)
    else:
        print("❌ Audit logs table setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())



