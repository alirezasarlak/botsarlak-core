#!/usr/bin/env python3
"""
Test Onboarding Flow
Test the complete onboarding flow
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.handlers.start import StartHandler
from src.handlers.onboarding.handler import OnboardingHandler

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

async def test_onboarding_flow():
    try:
        print("🌌 Testing Onboarding Flow...")
        
        # Test 1: Start Onboarding Callback
        print("\n1️⃣ Testing Start Onboarding Callback")
        start_handler = StartHandler()
        update = MockUpdate(694245594, "start_onboarding")
        context = MockContext()
        
        try:
            await start_handler.start_onboarding_callback(update, context)
            print("✅ Start onboarding callback works")
        except Exception as e:
            print(f"❌ Start onboarding callback failed: {e}")
            return False
        
        # Test 2: Start Registration Callback (OnboardingHandler)
        print("\n2️⃣ Testing Start Registration Callback")
        onboarding_handler = OnboardingHandler()
        update = MockUpdate(694245594, "start_registration")
        
        try:
            # This should trigger the ConversationHandler
            await onboarding_handler.start_registration_callback(update, context)
            print("✅ Start registration callback works")
        except Exception as e:
            print(f"❌ Start registration callback failed: {e}")
            return False
        
        print("\n🎉 Onboarding flow test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_onboarding_flow())
    if success:
        print("\n✅ Onboarding flow is working correctly!")
    else:
        print("\n❌ Onboarding flow has issues.")

