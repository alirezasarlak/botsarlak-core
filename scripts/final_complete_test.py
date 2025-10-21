#!/usr/bin/env python3
"""
Final Complete Test - End-to-End Profile System
Tests the complete flow: Start -> Menu -> Profile
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import db_manager
from src.services.profile_service import profile_service
from src.handlers.start import StartHandler
from src.handlers.main_menu.handler import MainMenuHandler
from src.handlers.profile.profile_handler_v3 import ProfileHandlerV3

class MockUpdate:
    def __init__(self, user_id, callback_data=None, message_text=None):
        self.effective_user = MockUser(user_id)
        self.callback_query = MockCallbackQuery(callback_data) if callback_data else None
        self.message = MockMessage(user_id, message_text) if message_text else None

class MockUser:
    def __init__(self, user_id):
        self.id = user_id
        self.first_name = "Test"
        self.username = "test_user"

class MockCallbackQuery:
    def __init__(self, callback_data):
        self.data = callback_data
        self.from_user = MockUser(694245594)
        self.edit_message_text = self._mock_edit_message_text
        self.answer = self._mock_answer
    
    async def _mock_edit_message_text(self, text, reply_markup=None, parse_mode=None):
        print(f"📱 Bot Response: {text[:100]}...")
        if reply_markup:
            print(f"🔘 Keyboard: {len(reply_markup.inline_keyboard)} rows")
        return True
    
    async def _mock_answer(self, text=None):
        return True

class MockMessage:
    def __init__(self, user_id, text=None):
        self.from_user = MockUser(user_id)
        self.text = text
        self.reply_text = self._mock_reply_text
    
    async def _mock_reply_text(self, text, reply_markup=None, parse_mode=None):
        print(f"📱 Bot Response: {text[:100]}...")
        if reply_markup:
            print(f"🔘 Keyboard: {len(reply_markup.inline_keyboard)} rows")
        return True

class MockContext:
    pass

async def test_complete_flow():
    try:
        print("🌌 Final Complete Test - End-to-End Profile System")
        print("=" * 60)
        
        # Initialize database
        await db_manager.initialize()
        
        # Test 1: Profile Service
        print("\n1️⃣ Testing Profile Service")
        summary = await profile_service.get_profile_summary(694245594)
        if summary and summary.get('profile'):
            profile = summary['profile']
            print(f"✅ Profile Service: {profile.display_name}")
            print(f"   - Statistics: {summary.get('statistics') is not None}")
            print(f"   - Level: {summary.get('level') is not None}")
        else:
            print("❌ Profile Service failed")
            return False
        
        # Test 2: Start Handler
        print("\n2️⃣ Testing Start Handler")
        start_handler = StartHandler()
        update = MockUpdate(694245594, message_text="/start")
        context = MockContext()
        
        try:
            await start_handler.start_command(update, context)
            print("✅ Start command works")
        except Exception as e:
            print(f"❌ Start command failed: {e}")
            return False
        
        # Test 3: Main Menu Handler
        print("\n3️⃣ Testing Main Menu Handler")
        main_menu_handler = MainMenuHandler()
        update = MockUpdate(694245594, "menu_profile")
        
        try:
            await main_menu_handler._show_profile_section(update.callback_query)
            print("✅ Main menu profile section works")
        except Exception as e:
            print(f"❌ Main menu profile section failed: {e}")
            return False
        
        # Test 4: Profile Handler
        print("\n4️⃣ Testing Profile Handler")
        profile_handler = ProfileHandlerV3()
        
        # Test /profile command
        update = MockUpdate(694245594, message_text="/profile")
        try:
            await profile_handler.profile_command(update, context)
            print("✅ /profile command works")
        except Exception as e:
            print(f"❌ /profile command failed: {e}")
            return False
        
        # Test profile_view callback
        update = MockUpdate(694245594, "profile_view")
        try:
            await profile_handler.profile_callback(update, context)
            print("✅ profile_view callback works")
        except Exception as e:
            print(f"❌ profile_view callback failed: {e}")
            return False
        
        # Test profile_stats callback
        update = MockUpdate(694245594, "profile_stats")
        try:
            await profile_handler.profile_callback(update, context)
            print("✅ profile_stats callback works")
        except Exception as e:
            print(f"❌ profile_stats callback failed: {e}")
            return False
        
        # Test profile_achievements callback
        update = MockUpdate(694245594, "profile_achievements")
        try:
            await profile_handler.profile_callback(update, context)
            print("✅ profile_achievements callback works")
        except Exception as e:
            print(f"❌ profile_achievements callback failed: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Profile System is Fully Operational!")
        print("=" * 60)
        
        print("\n✅ Complete Flow Test Results:")
        print("   - Profile Service: ✅ Working")
        print("   - Start Handler: ✅ Working")
        print("   - Main Menu Handler: ✅ Working")
        print("   - Profile Handler: ✅ Working")
        print("   - All Callbacks: ✅ Working")
        
        print("\n🚀 System is ready for production!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        await db_manager.close()

if __name__ == "__main__":
    success = asyncio.run(test_complete_flow())
    if success:
        print("\n🎯 Profile system is fully functional and ready!")
    else:
        print("\n❌ Profile system has issues that need to be fixed.")

