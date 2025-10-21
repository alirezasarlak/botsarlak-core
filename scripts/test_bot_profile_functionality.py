#!/usr/bin/env python3
"""
🌌 Test Bot Profile Functionality
Test the complete bot profile system end-to-end
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import db_manager
from src.services.profile_service import profile_service
from src.handlers.profile.profile_handler_v3 import ProfileHandlerV3
from src.utils.logging import get_logger

logger = get_logger(__name__)

class MockUpdate:
    """Mock Telegram Update for testing"""
    def __init__(self, user_id, callback_data=None):
        self.effective_user = MockUser(user_id)
        self.callback_query = MockCallbackQuery(callback_data) if callback_data else None
        self.message = MockMessage(user_id)

class MockUser:
    """Mock Telegram User"""
    def __init__(self, user_id):
        self.id = user_id
        self.first_name = "Test"
        self.username = "test_user"

class MockCallbackQuery:
    """Mock Telegram CallbackQuery"""
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
    """Mock Telegram Message"""
    def __init__(self, user_id):
        self.from_user = MockUser(user_id)
        self.reply_text = self._mock_reply_text
    
    async def _mock_reply_text(self, text, reply_markup=None, parse_mode=None):
        print(f"📱 Bot Response: {text[:100]}...")
        if reply_markup:
            print(f"🔘 Keyboard: {len(reply_markup.inline_keyboard)} rows")
        return True

class MockContext:
    """Mock Telegram Context"""
    pass

async def test_profile_functionality():
    """Test complete profile functionality"""
    try:
        print("🌌 Testing Bot Profile Functionality...")
        
        # Initialize profile handler
        profile_handler = ProfileHandlerV3()
        
        # Test user ID
        test_user_id = 694245594
        
        print(f"\n1️⃣ Testing Profile Command")
        
        # Test /profile command
        update = MockUpdate(test_user_id)
        context = MockContext()
        
        try:
            await profile_handler.profile_command(update, context)
            print("✅ Profile command works!")
        except Exception as e:
            print(f"❌ Profile command failed: {e}")
        
        print(f"\n2️⃣ Testing Profile View Callback")
        
        # Test profile_view callback
        update = MockUpdate(test_user_id, "profile_view")
        
        try:
            await profile_handler.profile_callback(update, context)
            print("✅ Profile view callback works!")
        except Exception as e:
            print(f"❌ Profile view callback failed: {e}")
        
        print(f"\n3️⃣ Testing Menu Profile Callback")
        
        # Test menu_profile callback
        update = MockUpdate(test_user_id, "menu_profile")
        
        try:
            await profile_handler.menu_profile_callback(update, context)
            print("✅ Menu profile callback works!")
        except Exception as e:
            print(f"❌ Menu profile callback failed: {e}")
        
        print(f"\n4️⃣ Testing Profile Statistics")
        
        # Test profile statistics
        update = MockUpdate(test_user_id, "profile_stats")
        
        try:
            await profile_handler.profile_callback(update, context)
            print("✅ Profile statistics works!")
        except Exception as e:
            print(f"❌ Profile statistics failed: {e}")
        
        print(f"\n5️⃣ Testing Profile Achievements")
        
        # Test profile achievements
        update = MockUpdate(test_user_id, "profile_achievements")
        
        try:
            await profile_handler.profile_callback(update, context)
            print("✅ Profile achievements works!")
        except Exception as e:
            print(f"❌ Profile achievements failed: {e}")
        
        print(f"\n6️⃣ Testing Profile Service Integration")
        
        # Test profile service
        summary = await profile_service.get_profile_summary(test_user_id)
        if summary:
            print("✅ Profile service integration works!")
            profile = summary.get('profile')
            if profile:
                print(f"   - Profile: {profile.display_name}")
            stats = summary.get('statistics')
            if stats:
                print(f"   - Statistics: {stats.total_study_time} minutes")
            level = summary.get('level')
            if level:
                print(f"   - Level: {level.current_level}")
        else:
            print("❌ Profile service integration failed")
        
        print(f"\n🎉 Bot Profile Functionality Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Bot profile functionality test failed: {e}")
        return False

async def main():
    """Main test function"""
    try:
        # Initialize database connection
        await db_manager.initialize()
        
        # Run tests
        success = await test_profile_functionality()
        
        if success:
            print("\n✅ All bot profile tests passed! System is ready.")
        else:
            print("\n❌ Some tests failed. Check the logs for details.")
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        logger.error(f"Test setup failed: {e}")
    finally:
        # Close database connection
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())

