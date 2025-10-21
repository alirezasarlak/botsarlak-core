#!/usr/bin/env python3
"""
اصلاح کامل Database Schema طبق اصول Engineering Contract
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_complete_database_schema():
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            database="sarlak_academy",
            user="postgres",
            password="ali123123"
        )
        
        print("🔧 **اصلاح کامل Database Schema**")
        print("=" * 50)
        
        # 1. Fix user_profiles table
        print("\n1️⃣ **اصلاح جدول user_profiles:**")
        
        try:
            # Drop and recreate user_profiles table with correct schema
            await conn.execute("DROP TABLE IF EXISTS user_profiles CASCADE")
            
            await conn.execute("""
                CREATE TABLE user_profiles (
                    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                    display_name TEXT,
                    nickname TEXT UNIQUE,
                    bio TEXT,
                    avatar_url TEXT,
                    phone_number TEXT,
                    birth_date DATE,
                    study_track TEXT,
                    grade_level TEXT,
                    grade_year INTEGER,
                    privacy_level TEXT DEFAULT 'friends_only',
                    is_public BOOLEAN DEFAULT FALSE,
                    show_statistics BOOLEAN DEFAULT TRUE,
                    show_achievements BOOLEAN DEFAULT TRUE,
                    show_streak BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            print("   ✅ جدول user_profiles با schema صحیح ایجاد شد")
            
        except Exception as e:
            print(f"   ❌ خطا در ایجاد user_profiles: {e}")
        
        # 2. Fix user_levels table
        print("\n2️⃣ **اصلاح جدول user_levels:**")
        
        try:
            # Drop and recreate user_levels table with correct schema
            await conn.execute("DROP TABLE IF EXISTS user_levels CASCADE")
            
            await conn.execute("""
                CREATE TABLE user_levels (
                    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                    current_level INTEGER DEFAULT 1,
                    total_points INTEGER DEFAULT 0,
                    level_points INTEGER DEFAULT 0,
                    next_level_points INTEGER DEFAULT 100,
                    level_title TEXT DEFAULT 'مبتدی',
                    level_color TEXT DEFAULT '#4CAF50',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            print("   ✅ جدول user_levels با schema صحیح ایجاد شد")
            
        except Exception as e:
            print(f"   ❌ خطا در ایجاد user_levels: {e}")
        
        # 3. Create achievement_definitions table
        print("\n3️⃣ **ایجاد جدول achievement_definitions:**")
        
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS achievement_definitions (
                    achievement_id SERIAL PRIMARY KEY,
                    achievement_name TEXT NOT NULL,
                    achievement_description TEXT,
                    achievement_type TEXT NOT NULL,
                    achievement_category TEXT NOT NULL,
                    requirements JSONB NOT NULL,
                    points_awarded INTEGER DEFAULT 0,
                    badge_icon TEXT DEFAULT '🏆',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            print("   ✅ جدول achievement_definitions ایجاد شد")
            
        except Exception as e:
            print(f"   ❌ خطا در ایجاد achievement_definitions: {e}")
        
        # 4. Create missing system tables
        print("\n4️⃣ **ایجاد جداول سیستم:**")
        
        # Create routes table
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS routes (
                    route_id SERIAL PRIMARY KEY,
                    route_name TEXT NOT NULL UNIQUE,
                    route_path TEXT NOT NULL UNIQUE,
                    handler_class TEXT NOT NULL,
                    handler_method TEXT NOT NULL,
                    route_type TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            print("   ✅ جدول routes ایجاد شد")
        except Exception as e:
            print(f"   ❌ خطا در ایجاد routes: {e}")
        
        # Create menus table
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS menus (
                    menu_id SERIAL PRIMARY KEY,
                    menu_name TEXT NOT NULL UNIQUE,
                    menu_title TEXT NOT NULL,
                    menu_description TEXT,
                    parent_menu_id INTEGER REFERENCES menus(menu_id),
                    route_id INTEGER REFERENCES routes(route_id),
                    menu_order INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            print("   ✅ جدول menus ایجاد شد")
        except Exception as e:
            print(f"   ❌ خطا در ایجاد menus: {e}")
        
        # Create route_history table
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS route_history (
                    history_id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    route_id INTEGER REFERENCES routes(route_id),
                    access_time TIMESTAMPTZ DEFAULT NOW(),
                    user_agent TEXT,
                    ip_address INET
                )
            """)
            print("   ✅ جدول route_history ایجاد شد")
        except Exception as e:
            print(f"   ❌ خطا در ایجاد route_history: {e}")
        
        # Create audit_logs table
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    log_id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    action_type TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    details JSONB,
                    security_level TEXT NOT NULL,
                    ip_address INET,
                    user_agent TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            print("   ✅ جدول audit_logs ایجاد شد")
        except Exception as e:
            print(f"   ❌ خطا در ایجاد audit_logs: {e}")
        
        # Create version_history table
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS version_history (
                    version_id SERIAL PRIMARY KEY,
                    version TEXT NOT NULL UNIQUE,
                    release_date TIMESTAMPTZ DEFAULT NOW(),
                    description TEXT,
                    changes JSONB,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            print("   ✅ جدول version_history ایجاد شد")
        except Exception as e:
            print(f"   ❌ خطا در ایجاد version_history: {e}")
        
        # 5. Create indexes
        print("\n5️⃣ **ایجاد ایندکس‌ها:**")
        
        indexes = [
            ("idx_users_user_id", "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)"),
            ("idx_users_nickname", "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_nickname ON users(nickname) WHERE nickname IS NOT NULL"),
            ("idx_users_onboarding_completed", "CREATE INDEX IF NOT EXISTS idx_users_onboarding_completed ON users(onboarding_completed) WHERE onboarding_completed = TRUE"),
            ("idx_user_profiles_user_id", "CREATE UNIQUE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id)"),
            ("idx_user_profiles_nickname", "CREATE UNIQUE INDEX IF NOT EXISTS idx_user_profiles_nickname ON user_profiles(nickname) WHERE nickname IS NOT NULL"),
            ("idx_user_statistics_user_id", "CREATE UNIQUE INDEX IF NOT EXISTS idx_user_statistics_user_id ON user_statistics(user_id)"),
            ("idx_user_levels_user_id", "CREATE UNIQUE INDEX IF NOT EXISTS idx_user_levels_user_id ON user_levels(user_id)"),
            ("idx_user_achievements_user_id", "CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id)"),
            ("idx_user_badges_user_id", "CREATE INDEX IF NOT EXISTS idx_user_badges_user_id ON user_badges(user_id)"),
            ("idx_routes_route_name", "CREATE UNIQUE INDEX IF NOT EXISTS idx_routes_route_name ON routes(route_name)"),
            ("idx_routes_route_path", "CREATE UNIQUE INDEX IF NOT EXISTS idx_routes_route_path ON routes(route_path)"),
            ("idx_menus_menu_name", "CREATE UNIQUE INDEX IF NOT EXISTS idx_menus_menu_name ON menus(menu_name)"),
            ("idx_audit_logs_user_id", "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)"),
            ("idx_audit_logs_created_at", "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at)")
        ]
        
        for index_name, index_sql in indexes:
            try:
                await conn.execute(index_sql)
                print(f"   ✅ {index_name}")
            except Exception as e:
                print(f"   ❌ {index_name}: {e}")
        
        # 6. Insert initial data
        print("\n6️⃣ **درج داده‌های اولیه:**")
        
        # Insert initial levels for existing users
        try:
            await conn.execute("""
                INSERT INTO user_levels (user_id)
                SELECT user_id FROM users
                WHERE user_id NOT IN (SELECT user_id FROM user_levels)
            """)
            print("   ✅ سطوح اولیه برای کاربران ایجاد شد")
        except Exception as e:
            print(f"   ❌ خطا در ایجاد سطوح اولیه: {e}")
        
        # Insert initial statistics for existing users
        try:
            await conn.execute("""
                INSERT INTO user_statistics (user_id)
                SELECT user_id FROM users
                WHERE user_id NOT IN (SELECT user_id FROM user_statistics)
            """)
            print("   ✅ آمار اولیه برای کاربران ایجاد شد")
        except Exception as e:
            print(f"   ❌ خطا در ایجاد آمار اولیه: {e}")
        
        # Insert sample achievement definitions
        try:
            achievements = [
                ("first_study", "اولین مطالعه", "اولین جلسه مطالعه خود را تکمیل کنید", "study", "beginner", {"total_sessions": 1}, 10, "🎓"),
                ("study_streak_7", "Streak هفتگی", "7 روز متوالی مطالعه کنید", "streak", "consistency", {"current_streak": 7}, 50, "🔥"),
                ("study_streak_30", "Streak ماهانه", "30 روز متوالی مطالعه کنید", "streak", "consistency", {"current_streak": 30}, 200, "💪"),
                ("study_time_100", "100 ساعت مطالعه", "100 ساعت مطالعه کنید", "time", "dedication", {"total_study_time": 6000}, 100, "⏰"),
                ("study_time_500", "500 ساعت مطالعه", "500 ساعت مطالعه کنید", "time", "dedication", {"total_study_time": 30000}, 500, "🏆")
            ]
            
            for achievement in achievements:
                await conn.execute("""
                    INSERT INTO achievement_definitions 
                    (achievement_name, achievement_description, achievement_type, achievement_category, requirements, points_awarded, badge_icon)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT DO NOTHING
                """, *achievement)
            
            print("   ✅ تعاریف دستاوردها ایجاد شد")
        except Exception as e:
            print(f"   ❌ خطا در ایجاد تعاریف دستاوردها: {e}")
        
        # Insert current version
        try:
            await conn.execute("""
                INSERT INTO version_history (version, description, changes)
                VALUES ($1, $2, $3)
                ON CONFLICT (version) DO NOTHING
            """, "3.1.2", "Complete Profile System Implementation", {
                "added": ["Complete Profile System", "Database Schema Fix", "Navigation System"],
                "fixed": ["User Persistence", "Phone Registration", "Profile Display"],
                "improved": ["Database Schema", "Error Handling", "User Experience"]
            })
            print("   ✅ ورژن فعلی ثبت شد")
        except Exception as e:
            print(f"   ❌ خطا در ثبت ورژن: {e}")
        
        # 7. Verify schema
        print("\n7️⃣ **بررسی نهایی schema:**")
        
        tables = ['users', 'user_profiles', 'user_statistics', 'user_levels', 
                 'user_achievements', 'user_badges', 'achievement_definitions',
                 'routes', 'menus', 'route_history', 'audit_logs', 'version_history']
        
        for table in tables:
            try:
                exists = await conn.fetchval(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                if exists:
                    count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                    print(f"   ✅ {table}: {count} رکورد")
                else:
                    print(f"   ❌ {table}: وجود ندارد")
            except Exception as e:
                print(f"   ❌ {table}: خطا - {e}")
        
        await conn.close()
        print("\n🎉 **اصلاح کامل Database Schema تمام شد!**")
        
    except Exception as e:
        print(f"❌ خطا در اصلاح schema: {e}")

if __name__ == "__main__":
    asyncio.run(fix_complete_database_schema())


