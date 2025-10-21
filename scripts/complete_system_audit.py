#!/usr/bin/env python3
"""
بررسی کامل سیستم - Complete System Audit
طبق اصول Engineering Contract
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def complete_system_audit():
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            database="sarlak_academy",
            user="postgres",
            password="ali123123"
        )
        
        print("🔍 **بررسی کامل سیستم SarlakBot v3.1.2**")
        print("=" * 60)
        
        # 1. Database Schema Audit
        print("\n📊 **1. بررسی Schema دیتابیس:**")
        
        # Check all required tables
        required_tables = [
            'users', 'user_profiles', 'user_statistics', 'user_levels',
            'user_achievements', 'user_badges', 'achievement_definitions',
            'routes', 'menus', 'route_history', 'audit_logs', 'version_history'
        ]
        
        existing_tables = []
        missing_tables = []
        
        for table in required_tables:
            exists = await conn.fetchval(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
            if exists:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                existing_tables.append((table, count))
                print(f"   ✅ {table}: {count} رکورد")
            else:
                missing_tables.append(table)
                print(f"   ❌ {table}: وجود ندارد")
        
        # 2. Users Table Schema Audit
        print(f"\n👥 **2. بررسی Schema جدول users:**")
        
        users_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        required_users_columns = [
            'user_id', 'first_name', 'last_name', 'username', 'language_code',
            'onboarding_completed', 'real_name', 'nickname', 'study_track',
            'grade_band', 'grade_year', 'phone', 'is_active', 'created_at',
            'last_seen_at', 'updated_at', 'last_activity'
        ]
        
        existing_users_columns = [col['column_name'] for col in users_columns]
        missing_users_columns = []
        
        for req_col in required_users_columns:
            if req_col in existing_users_columns:
                print(f"   ✅ {req_col}")
            else:
                missing_users_columns.append(req_col)
                print(f"   ❌ {req_col}: مفقود")
        
        # 3. Profile System Tables Audit
        print(f"\n🪐 **3. بررسی جداول Profile System:**")
        
        profile_tables = ['user_profiles', 'user_statistics', 'user_levels', 'user_achievements', 'user_badges']
        
        for table in profile_tables:
            if table in [t[0] for t in existing_tables]:
                # Check table schema
                columns = await conn.fetch(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position;
                """)
                
                print(f"   📋 {table} schema:")
                for col in columns:
                    print(f"      - {col['column_name']}: {col['data_type']}")
            else:
                print(f"   ❌ {table}: جدول وجود ندارد")
        
        # 4. User Data Audit
        print(f"\n👤 **4. بررسی داده‌های کاربران:**")
        
        users_data = await conn.fetch("""
            SELECT 
                user_id, real_name, first_name, nickname, username,
                study_track, grade_year, phone, onboarding_completed,
                is_active, created_at, last_seen_at
            FROM users 
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        for user in users_data:
            print(f"   👤 کاربر {user['user_id']}:")
            print(f"      نام: {user['real_name'] or user['first_name'] or 'نامشخص'}")
            print(f"      نام مستعار: {user['nickname'] or 'نامشخص'}")
            print(f"      رشته: {user['study_track'] or 'نامشخص'}")
            print(f"      پایه: {user['grade_year'] or 'نامشخص'}")
            print(f"      شماره: {user['phone'] or 'نامشخص'}")
            print(f"      onboarding: {user['onboarding_completed']}")
            print(f"      فعال: {user['is_active']}")
            print(f"      ایجاد: {user['created_at']}")
            print()
        
        # 5. Profile System Data Audit
        print(f"\n📊 **5. بررسی داده‌های Profile System:**")
        
        # Check user_statistics
        if 'user_statistics' in [t[0] for t in existing_tables]:
            stats_data = await conn.fetch("""
                SELECT user_id, total_study_time, current_streak, total_sessions
                FROM user_statistics 
                LIMIT 3
            """)
            
            print("   📈 آمار کاربران:")
            for stat in stats_data:
                print(f"      کاربر {stat['user_id']}: {stat['total_study_time']} دقیقه، {stat['current_streak']} روز، {stat['total_sessions']} جلسه")
        
        # Check user_levels
        if 'user_levels' in [t[0] for t in existing_tables]:
            levels_data = await conn.fetch("""
                SELECT user_id, current_level, total_points, level_title
                FROM user_levels 
                LIMIT 3
            """)
            
            print("   🏆 سطوح کاربران:")
            for level in levels_data:
                print(f"      کاربر {level['user_id']}: سطح {level['current_level']} ({level['level_title']}), {level['total_points']} امتیاز")
        
        # 6. System Health Check
        print(f"\n🏥 **6. بررسی سلامت سیستم:**")
        
        # Check database connection
        db_info = await conn.fetchrow("""
            SELECT 
                current_database() as database_name,
                version() as version,
                current_user as current_user
        """)
        
        print(f"   🗄️ دیتابیس: {db_info['database_name']}")
        print(f"   👤 کاربر: {db_info['current_user']}")
        print(f"   📝 نسخه: {db_info['version'][:50]}...")
        
        # Check indexes
        indexes = await conn.fetch("""
            SELECT indexname, tablename 
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        
        print(f"   📊 ایندکس‌ها: {len(indexes)} عدد")
        for idx in indexes[:5]:  # Show first 5
            print(f"      - {idx['indexname']} on {idx['tablename']}")
        
        # 7. Issues Summary
        print(f"\n⚠️ **7. خلاصه مشکلات:**")
        
        if missing_tables:
            print(f"   ❌ جداول مفقود: {', '.join(missing_tables)}")
        
        if missing_users_columns:
            print(f"   ❌ ستون‌های مفقود در users: {', '.join(missing_users_columns)}")
        
        # Check for incomplete onboarding
        incomplete_users = await conn.fetchval("""
            SELECT COUNT(*) FROM users 
            WHERE onboarding_completed = FALSE OR onboarding_completed IS NULL
        """)
        
        if incomplete_users > 0:
            print(f"   ⚠️ کاربران با onboarding ناقص: {incomplete_users} نفر")
        
        # Check for users without profiles
        users_without_profiles = await conn.fetchval("""
            SELECT COUNT(*) FROM users u
            LEFT JOIN user_profiles up ON u.user_id = up.user_id
            WHERE up.user_id IS NULL
        """)
        
        if users_without_profiles > 0:
            print(f"   ⚠️ کاربران بدون پروفایل: {users_without_profiles} نفر")
        
        # 8. Recommendations
        print(f"\n💡 **8. توصیه‌ها:**")
        
        if missing_tables:
            print(f"   🔧 ایجاد جداول مفقود")
        
        if missing_users_columns:
            print(f"   🔧 اضافه کردن ستون‌های مفقود")
        
        if incomplete_users > 0:
            print(f"   🔧 تکمیل onboarding کاربران")
        
        if users_without_profiles > 0:
            print(f"   🔧 ایجاد پروفایل برای کاربران")
        
        print(f"\n✅ **بررسی کامل سیستم تمام شد!**")
        
        await conn.close()
        
        return {
            'missing_tables': missing_tables,
            'missing_users_columns': missing_users_columns,
            'incomplete_users': incomplete_users,
            'users_without_profiles': users_without_profiles
        }
        
    except Exception as e:
        print(f"❌ خطا در بررسی سیستم: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(complete_system_audit())


