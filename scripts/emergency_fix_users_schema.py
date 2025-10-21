#!/usr/bin/env python3
"""
Emergency fix for users table schema
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def emergency_fix_users_schema():
    try:
        # Connect using the same connection string as the bot
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            database="sarlak_academy",
            user="postgres",
            password="ali123123"
        )
        
        print("🔧 شروع اصلاح اضطراری schema جدول users...")
        
        # Add missing columns one by one
        columns_to_add = [
            ("first_name", "TEXT"),
            ("last_name", "TEXT"),
            ("username", "TEXT"),
            ("language_code", "TEXT"),
            ("onboarding_completed", "BOOLEAN DEFAULT FALSE"),
            ("real_name", "TEXT"),
            ("nickname", "TEXT"),
            ("study_track", "TEXT"),
            ("grade_band", "TEXT"),
            ("grade_year", "TEXT"),
            ("phone", "TEXT"),
            ("updated_at", "TIMESTAMPTZ DEFAULT NOW()"),
            ("last_activity", "TIMESTAMPTZ DEFAULT NOW()")
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                # Check if column exists
                exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'users' AND column_name = $1
                    )
                """, column_name)
                
                if not exists:
                    print(f"  ➕ اضافه کردن ستون: {column_name}")
                    await conn.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                else:
                    print(f"  ✅ ستون موجود: {column_name}")
                    
            except Exception as e:
                print(f"  ❌ خطا در اضافه کردن ستون {column_name}: {e}")
        
        # Create indexes
        indexes_to_create = [
            ("idx_users_nickname", "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_nickname ON users(nickname) WHERE nickname IS NOT NULL"),
            ("idx_users_onboarding_completed", "CREATE INDEX IF NOT EXISTS idx_users_onboarding_completed ON users(onboarding_completed) WHERE onboarding_completed = TRUE"),
            ("idx_users_study_track", "CREATE INDEX IF NOT EXISTS idx_users_study_track ON users(study_track)"),
            ("idx_users_grade_year", "CREATE INDEX IF NOT EXISTS idx_users_grade_year ON users(grade_year)")
        ]
        
        for index_name, index_sql in indexes_to_create:
            try:
                print(f"  📊 ایجاد ایندکس: {index_name}")
                await conn.execute(index_sql)
            except Exception as e:
                print(f"  ❌ خطا در ایجاد ایندکس {index_name}: {e}")
        
        # Update existing users
        try:
            print("  🔄 بروزرسانی کاربران موجود...")
            await conn.execute("""
                UPDATE users 
                SET 
                    onboarding_completed = COALESCE(onboarding_completed, FALSE),
                    updated_at = COALESCE(updated_at, created_at),
                    last_activity = COALESCE(last_activity, created_at)
                WHERE onboarding_completed IS NULL 
                   OR updated_at IS NULL 
                   OR last_activity IS NULL
            """)
        except Exception as e:
            print(f"  ❌ خطا در بروزرسانی کاربران: {e}")
        
        # Verify the schema
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        print("\n📋 Schema جدید جدول users:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Check required columns
        required_columns = [
            'user_id', 'first_name', 'last_name', 'username', 'language_code',
            'onboarding_completed', 'real_name', 'nickname', 'study_track',
            'grade_band', 'grade_year', 'phone', 'is_active', 'created_at',
            'last_seen_at', 'updated_at', 'last_activity'
        ]
        
        existing_columns = [col['column_name'] for col in columns]
        
        print("\n🔍 بررسی ستون‌های مورد نیاز:")
        missing_columns = []
        for req_col in required_columns:
            if req_col in existing_columns:
                print(f"  ✅ {req_col}: موجود")
            else:
                print(f"  ❌ {req_col}: مفقود")
                missing_columns.append(req_col)
        
        if missing_columns:
            print(f"\n⚠️  ستون‌های مفقود: {missing_columns}")
        else:
            print("\n🎉 همه ستون‌های مورد نیاز موجود هستند!")
        
        # Check if we have any users
        user_count = await conn.fetchval('SELECT COUNT(*) FROM users')
        print(f"\n👥 تعداد کاربران: {user_count}")
        
        if user_count > 0:
            # Show sample user data
            sample_user = await conn.fetchrow('SELECT * FROM users LIMIT 1')
            print('\n📄 نمونه داده کاربر:')
            for key, value in sample_user.items():
                print(f'  {key}: {value}')
        
        await conn.close()
        print("\n✅ اصلاح اضطراری schema جدول users کامل شد!")
        
    except Exception as e:
        print(f"❌ خطا در اصلاح اضطراری schema: {e}")

if __name__ == "__main__":
    asyncio.run(emergency_fix_users_schema())


