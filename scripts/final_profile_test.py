#!/usr/bin/env python3
"""
Final Profile System Test
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import db_manager
from src.services.profile_service import profile_service
from src.handlers.profile.profile_handler_v3 import ProfileHandlerV3

class MockUpdate:
    def __init__(self, user_id, callback_data=None):
        self.effective_user = MockUser(user_id)
        self.callback_query = MockCallbackQuery(callback_data) if callback_data else None
        self.message = MockMessage(user_id)

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
    def __init__(self, user_id):
        self.from_user = MockUser(user_id)
        self.reply_text = self._mock_reply_text
    
    async def _mock_reply_text(self, text, reply_markup=None, parse_mode=None):
        print(f"📱 Bot Response: {text[:100]}...")
        if reply_markup:
            print(f"🔘 Keyboard: {len(reply_markup.inline_keyboard)} rows")
        return True

class MockContext:
    pass

async def test_final():
    try:
        print("🌌 Final Profile System Test...")
        
        # Initialize database
        await db_manager.initialize()
        
        # Test profile service
        summary = await profile_service.get_profile_summary(694245594)
        if summary and summary.get('profile'):
            profile = summary['profile']
            print(f"✅ Profile Service: {profile.display_name}")
            print(f"   - Statistics: {summary.get('statistics') is not None}")
            print(f"   - Level: {summary.get('level') is not None}")
            print(f"   - Achievements: {len(summary.get('achievements', []))}")
            print(f"   - Badges: {len(summary.get('badges', []))}")
        else:
            print("❌ Profile Service failed")
            return False
        
        # Test profile handler
        profile_handler = ProfileHandlerV3()
        
        # Test /profile command
        update = MockUpdate(694245594)
        context = MockContext()
        
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
        
        # Test menu_profile callback
        update = MockUpdate(694245594, "menu_profile")
        
        try:
            await profile_handler.menu_profile_callback(update, context)
            print("✅ menu_profile callback works")
        except Exception as e:
            print(f"❌ menu_profile callback failed: {e}")
            return False
        
        print("\n🎉 All tests passed! Profile system is fully operational!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        await db_manager.close()

if __name__ == "__main__":
    success = asyncio.run(test_final())
    if success:
        print("\n✅ Profile system is ready for production!")
    else:
        print("\n❌ Profile system has issues that need to be fixed.")

