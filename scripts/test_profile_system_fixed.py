#!/usr/bin/env python3
"""
تست Profile System اصلاح شده
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_profile_system():
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            database="sarlak_academy",
            user="postgres",
            password="ali123123"
        )
        
        print("🧪 تست Profile System اصلاح شده...")
        
        # Test 1: Check if user exists
        user_id = 6670874228  # Test user ID
        print(f"\n1️⃣ بررسی وجود کاربر {user_id}:")
        
        user_query = "SELECT * FROM users WHERE user_id = $1"
        user_data = await conn.fetchrow(user_query, user_id)
        
        if user_data:
            print("✅ کاربر موجود است")
            print(f"   نام: {user_data.get('real_name') or user_data.get('first_name')}")
            print(f"   نام مستعار: {user_data.get('nickname')}")
            print(f"   رشته: {user_data.get('study_track')}")
            print(f"   پایه: {user_data.get('grade_year')}")
        else:
            print("❌ کاربر یافت نشد")
            return
        
        # Test 2: Check profile tables
        print(f"\n2️⃣ بررسی جداول Profile System:")
        
        tables = ['user_profiles', 'user_statistics', 'user_levels', 'user_achievements', 'user_badges']
        
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
        
        # Test 3: Test profile service methods
        print(f"\n3️⃣ تست Profile Service:")
        
        # Simulate profile service calls
        try:
            # Check if user has profile
            profile_query = "SELECT * FROM user_profiles WHERE user_id = $1"
            profile_data = await conn.fetchrow(profile_query, user_id)
            
            if profile_data:
                print("   ✅ پروفایل موجود است")
            else:
                print("   ⚠️ پروفایل موجود نیست - باید از users table استفاده شود")
            
            # Check statistics
            stats_query = "SELECT * FROM user_statistics WHERE user_id = $1"
            stats_data = await conn.fetchrow(stats_query, user_id)
            
            if stats_data:
                print("   ✅ آمار موجود است")
                print(f"      زمان مطالعه: {stats_data.get('total_study_time', 0)} دقیقه")
                print(f"      Streak: {stats_data.get('current_streak', 0)} روز")
            else:
                print("   ⚠️ آمار موجود نیست")
            
            # Check level
            level_query = "SELECT * FROM user_levels WHERE user_id = $1"
            level_data = await conn.fetchrow(level_query, user_id)
            
            if level_data:
                print("   ✅ سطح موجود است")
                print(f"      سطح: {level_data.get('current_level', 1)}")
                print(f"      امتیاز: {level_data.get('total_points', 0)}")
            else:
                print("   ⚠️ سطح موجود نیست")
                
        except Exception as e:
            print(f"   ❌ خطا در تست Profile Service: {e}")
        
        # Test 4: Generate profile card data
        print(f"\n4️⃣ تست تولید Profile Card:")
        
        try:
            # Get user data
            display_name = user_data.get('real_name') or user_data.get('first_name') or "کاربر"
            nickname = user_data.get('nickname') or user_data.get('username') or f"user_{user_id}"
            study_track = user_data.get('study_track') or "تعریف نشده"
            grade_year = user_data.get('grade_year') or "تعریف نشده"
            
            # Get statistics
            total_time = stats_data.get('total_study_time', 0) if stats_data else 0
            current_streak = stats_data.get('current_streak', 0) if stats_data else 0
            total_sessions = stats_data.get('total_sessions', 0) if stats_data else 0
            
            # Get level
            current_level = level_data.get('current_level', 1) if level_data else 1
            total_points = level_data.get('total_points', 0) if level_data else 0
            level_title = level_data.get('level_title', 'مبتدی') if level_data else 'مبتدی'
            
            # Format study time
            hours = total_time // 60
            minutes = total_time % 60
            study_time_text = f"{hours} ساعت {minutes} دقیقه" if hours > 0 else f"{minutes} دقیقه"
            
            print("   ✅ Profile Card تولید شد:")
            print(f"      نام: {display_name}")
            print(f"      نام مستعار: @{nickname}")
            print(f"      رشته: {study_track}")
            print(f"      پایه: {grade_year}")
            print(f"      سطح: {current_level} ({level_title})")
            print(f"      امتیاز: {total_points:,}")
            print(f"      زمان مطالعه: {study_time_text}")
            print(f"      Streak: {current_streak} روز")
            print(f"      جلسات: {total_sessions} جلسه")
            
        except Exception as e:
            print(f"   ❌ خطا در تولید Profile Card: {e}")
        
        await conn.close()
        print("\n✅ تست Profile System کامل شد!")
        
    except Exception as e:
        print(f"❌ خطا در تست Profile System: {e}")

if __name__ == "__main__":
    asyncio.run(test_profile_system())


