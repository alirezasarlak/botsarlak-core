#!/usr/bin/env python3
"""
Setup Route Registry Tables
Manual setup for route registry database tables
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def setup_route_tables():
    """Setup route registry tables"""
    try:
        logger.info("🚀 Setting up route registry tables...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Create routes table
        routes_table_sql = """
        CREATE TABLE IF NOT EXISTS routes (
            id SERIAL PRIMARY KEY,
            route_key VARCHAR(255) UNIQUE NOT NULL,
            handler_name VARCHAR(500) NOT NULL,
            button_text VARCHAR(255) NOT NULL,
            parent_route VARCHAR(255),
            order_num INTEGER DEFAULT 0,
            route_type VARCHAR(50) DEFAULT 'menu',
            is_active BOOLEAN DEFAULT TRUE,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        await db_manager.execute(routes_table_sql)
        logger.info("✅ Routes table created")
        
        # Create menus table
        menus_table_sql = """
        CREATE TABLE IF NOT EXISTS menus (
            id SERIAL PRIMARY KEY,
            menu_name VARCHAR(255) UNIQUE NOT NULL,
            menu_json JSONB NOT NULL,
            version VARCHAR(50) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        await db_manager.execute(menus_table_sql)
        logger.info("✅ Menus table created")
        
        # Create route_history table
        route_history_sql = """
        CREATE TABLE IF NOT EXISTS route_history (
            id SERIAL PRIMARY KEY,
            action VARCHAR(100) NOT NULL,
            route_key VARCHAR(255),
            payload JSONB DEFAULT '{}',
            admin_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        await db_manager.execute(route_history_sql)
        logger.info("✅ Route history table created")
        
        # Create indexes
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_routes_route_key ON routes(route_key);",
            "CREATE INDEX IF NOT EXISTS idx_routes_parent_route ON routes(parent_route);",
            "CREATE INDEX IF NOT EXISTS idx_routes_is_active ON routes(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_routes_order ON routes(parent_route, order_num);",
            "CREATE INDEX IF NOT EXISTS idx_menus_menu_name ON menus(menu_name);",
            "CREATE INDEX IF NOT EXISTS idx_menus_version ON menus(version);",
            "CREATE INDEX IF NOT EXISTS idx_route_history_action ON route_history(action);",
            "CREATE INDEX IF NOT EXISTS idx_route_history_route_key ON route_history(route_key);",
            "CREATE INDEX IF NOT EXISTS idx_route_history_created_at ON route_history(created_at);"
        ]
        
        for index_sql in indexes_sql:
            await db_manager.execute(index_sql)
        
        logger.info("✅ Indexes created")
        
        # Insert initial routes
        initial_routes_sql = """
        INSERT INTO routes (route_key, handler_name, button_text, parent_route, order_num, route_type, is_active) VALUES
        ('main', 'main_menu', '🏠 منوی اصلی', NULL, 0, 'menu', TRUE),
        ('study', 'study_menu', '📚 مطالعه', 'main', 1, 'menu', TRUE),
        ('profile', 'profile_menu', '🪐 پروفایل', 'main', 2, 'menu', TRUE),
        ('motivation', 'motivation_menu', '🌟 انگیزه', 'main', 3, 'menu', TRUE),
        ('competition', 'competition_menu', '☄️ رقابت', 'main', 4, 'menu', TRUE),
        ('store', 'store_menu', '🛍️ فروشگاه', 'main', 5, 'menu', TRUE),
        ('compass', 'compass_menu', '🧭 قطب‌نما', 'main', 6, 'menu', TRUE),
        ('settings', 'settings_menu', '⚙️ تنظیمات', 'main', 7, 'menu', TRUE),
        ('help', 'help_menu', '❓ راهنما', 'main', 8, 'menu', TRUE)
        ON CONFLICT (route_key) DO NOTHING;
        """
        
        await db_manager.execute(initial_routes_sql)
        logger.info("✅ Initial routes inserted")
        
        # Insert study submenu
        study_routes_sql = """
        INSERT INTO routes (route_key, handler_name, button_text, parent_route, order_num, route_type, is_active) VALUES
        ('study.report', 'study_report', '📘 گزارش مطالعه', 'study', 1, 'action', TRUE),
        ('study.session', 'study_session', '⏱️ جلسه مطالعه', 'study', 2, 'action', TRUE),
        ('study.progress', 'study_progress', '📊 پیشرفت', 'study', 3, 'action', TRUE),
        ('study.goals', 'study_goals', '🎯 اهداف', 'study', 4, 'action', TRUE)
        ON CONFLICT (route_key) DO NOTHING;
        """
        
        await db_manager.execute(study_routes_sql)
        logger.info("✅ Study routes inserted")
        
        # Insert profile submenu
        profile_routes_sql = """
        INSERT INTO routes (route_key, handler_name, button_text, parent_route, order_num, route_type, is_active) VALUES
        ('profile.view', 'profile_view', '👤 مشاهده پروفایل', 'profile', 1, 'action', TRUE),
        ('profile.edit', 'profile_edit', '✏️ ویرایش پروفایل', 'profile', 2, 'action', TRUE),
        ('profile.stats', 'profile_stats', '📈 آمار', 'profile', 3, 'action', TRUE),
        ('profile.achievements', 'profile_achievements', '🏆 دستاوردها', 'profile', 4, 'action', TRUE)
        ON CONFLICT (route_key) DO NOTHING;
        """
        
        await db_manager.execute(profile_routes_sql)
        logger.info("✅ Profile routes inserted")
        
        logger.info("🎉 Route registry tables setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False
    finally:
        await db_manager.close()


async def main():
    """Main function"""
    success = await setup_route_tables()
    
    if success:
        print("✅ Route registry tables setup completed successfully!")
        sys.exit(0)
    else:
        print("❌ Route registry tables setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())



