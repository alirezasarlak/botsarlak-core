#!/usr/bin/env python3
"""
اصلاح schema جدول users برای user persistence
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_users_table_schema():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        
        print("🔧 شروع اصلاح schema جدول users...")
        
        # Read and execute the migration script
        with open('migrations/versions/008_fix_users_table_schema.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Execute the migration
        await conn.execute(migration_sql)
        
        print("✅ Migration اجرا شد")
        
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
        print("\n✅ اصلاح schema جدول users کامل شد!")
        
    except Exception as e:
        print(f"❌ خطا در اصلاح schema: {e}")

if __name__ == "__main__":
    asyncio.run(fix_users_table_schema())


