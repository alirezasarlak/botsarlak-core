#!/usr/bin/env python3
"""
تست ثبت شماره تلفن در onboarding
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_phone_registration():
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            database="sarlak_academy",
            user="postgres",
            password="ali123123"
        )
        
        print("📱 تست ثبت شماره تلفن در onboarding...")
        
        # Test 1: Check users table schema
        print(f"\n1️⃣ بررسی schema جدول users:")
        
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        phone_related_columns = []
        for col in columns:
            if 'phone' in col['column_name'].lower():
                phone_related_columns.append(col['column_name'])
                print(f"   ✅ {col['column_name']}: {col['data_type']}")
        
        if not phone_related_columns:
            print("   ❌ هیچ ستون مربوط به شماره تلفن یافت نشد!")
            return
        
        # Test 2: Check existing user data
        print(f"\n2️⃣ بررسی داده‌های کاربران موجود:")
        
        users = await conn.fetch("""
            SELECT user_id, real_name, nickname, phone, onboarding_completed
            FROM users 
            LIMIT 5
        """)
        
        for user in users:
            print(f"   👤 کاربر {user['user_id']}:")
            print(f"      نام: {user['real_name']}")
            print(f"      نام مستعار: {user['nickname']}")
            print(f"      شماره: {user['phone']}")
            print(f"      onboarding: {user['onboarding_completed']}")
        
        # Test 3: Test phone number validation
        print(f"\n3️⃣ تست validation شماره تلفن:")
        
        test_phones = [
            "09123456789",
            "+989123456789",
            "0912-345-6789",
            "9123456789",
            "invalid_phone"
        ]
        
        import re
        phone_pattern = r'^(\+98|0)?9\d{9}$'
        
        for phone in test_phones:
            clean_phone = phone.replace(' ', '').replace('-', '')
            is_valid = bool(re.match(phone_pattern, clean_phone))
            print(f"   {'✅' if is_valid else '❌'} {phone} -> {clean_phone} ({'معتبر' if is_valid else 'نامعتبر'})")
        
        # Test 4: Test database update
        print(f"\n4️⃣ تست بروزرسانی شماره تلفن:")
        
        test_user_id = 6670874228
        test_phone = "09123456789"
        
        try:
            # Update phone number
            result = await conn.execute("""
                UPDATE users 
                SET phone = $1, updated_at = NOW()
                WHERE user_id = $2
            """, test_phone, test_user_id)
            
            print(f"   ✅ شماره تلفن بروزرسانی شد: {result}")
            
            # Verify update
            updated_user = await conn.fetchrow("""
                SELECT phone FROM users WHERE user_id = $1
            """, test_user_id)
            
            if updated_user:
                print(f"   ✅ شماره جدید: {updated_user['phone']}")
            else:
                print("   ❌ کاربر یافت نشد")
                
        except Exception as e:
            print(f"   ❌ خطا در بروزرسانی: {e}")
        
        # Test 5: Test onboarding completion
        print(f"\n5️⃣ تست تکمیل onboarding:")
        
        try:
            # Simulate complete onboarding
            result = await conn.execute("""
                UPDATE users 
                SET 
                    real_name = $1,
                    nickname = $2,
                    study_track = $3,
                    grade_band = $4,
                    grade_year = $5,
                    phone = $6,
                    onboarding_completed = TRUE,
                    updated_at = NOW()
                WHERE user_id = $7
            """, 
            "تست کاربر", "test_user", "تجربی", "متوسطه دوم", "دوازدهم", "09123456789", test_user_id)
            
            print(f"   ✅ onboarding تکمیل شد: {result}")
            
            # Verify completion
            completed_user = await conn.fetchrow("""
                SELECT real_name, nickname, study_track, grade_year, phone, onboarding_completed
                FROM users WHERE user_id = $1
            """, test_user_id)
            
            if completed_user:
                print(f"   ✅ اطلاعات تکمیل شده:")
                print(f"      نام: {completed_user['real_name']}")
                print(f"      نام مستعار: {completed_user['nickname']}")
                print(f"      رشته: {completed_user['study_track']}")
                print(f"      پایه: {completed_user['grade_year']}")
                print(f"      شماره: {completed_user['phone']}")
                print(f"      تکمیل شده: {completed_user['onboarding_completed']}")
            else:
                print("   ❌ کاربر یافت نشد")
                
        except Exception as e:
            print(f"   ❌ خطا در تکمیل onboarding: {e}")
        
        await conn.close()
        print("\n✅ تست ثبت شماره تلفن کامل شد!")
        
    except Exception as e:
        print(f"❌ خطا در تست ثبت شماره تلفن: {e}")

if __name__ == "__main__":
    asyncio.run(test_phone_registration())


