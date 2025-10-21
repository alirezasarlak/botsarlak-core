#!/usr/bin/env python3
"""
بررسی دقیق schema جدول users و تشخیص مشکل user persistence
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_users_table():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        
        # Check if users table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            );
        """)
        
        if not table_exists:
            print('❌ جدول users وجود ندارد!')
            return
            
        # Get table schema
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        print('📋 Schema جدول users:')
        for col in columns:
            print(f'  - {col["column_name"]}: {col["data_type"]} (nullable: {col["is_nullable"]})')
            
        # Check if we have any users
        user_count = await conn.fetchval('SELECT COUNT(*) FROM users')
        print(f'\n👥 تعداد کاربران: {user_count}')
        
        if user_count > 0:
            # Show sample user data
            sample_user = await conn.fetchrow('SELECT * FROM users LIMIT 1')
            print('\n📄 نمونه داده کاربر:')
            for key, value in sample_user.items():
                print(f'  {key}: {value}')
        
        # Check for required columns for user persistence
        required_columns = ['user_id', 'first_name', 'last_name', 'username', 'onboarding_completed']
        existing_columns = [col['column_name'] for col in columns]
        
        print('\n🔍 بررسی ستون‌های مورد نیاز:')
        missing_columns = []
        for req_col in required_columns:
            if req_col in existing_columns:
                print(f'  ✅ {req_col}: موجود')
            else:
                print(f'  ❌ {req_col}: مفقود')
                missing_columns.append(req_col)
        
        if missing_columns:
            print(f'\n⚠️  ستون‌های مفقود: {missing_columns}')
            print('این مشکل باعث عدم کارکرد صحیح user persistence می‌شود.')
        
        await conn.close()
        
    except Exception as e:
        print(f'❌ خطا: {e}')

if __name__ == "__main__":
    asyncio.run(check_users_table())


