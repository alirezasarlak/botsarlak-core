#!/usr/bin/env python3
"""
Test Bot Callbacks
Test if the bot callbacks are working correctly
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        self.last_name = None
        self.language_code = "fa"
        self.is_bot = False

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

async def test_callbacks():
    try:
        print("🌌 Testing Bot Callbacks...")
        
        # Test 1: Start Handler
        print("\n1️⃣ Testing Start Handler")
        start_handler = StartHandler()
        update = MockUpdate(694245594, message_text="/start")
        context = MockContext()
        
        try:
            await start_handler.start_command(update, context)
            print("✅ Start command works")
        except Exception as e:
            print(f"❌ Start command failed: {e}")
            return False
        
        # Test 2: Start Onboarding Callback
        print("\n2️⃣ Testing Start Onboarding Callback")
        update = MockUpdate(694245594, "start_onboarding")
        
        try:
            await start_handler.start_onboarding_callback(update, context)
            print("✅ Start onboarding callback works")
        except Exception as e:
            print(f"❌ Start onboarding callback failed: {e}")
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
        
        print("\n🎉 All callback tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_callbacks())
    if success:
        print("\n✅ Bot callbacks are working correctly!")
    else:
        print("\n❌ Bot callbacks have issues.")

