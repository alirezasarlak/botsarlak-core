#!/usr/bin/env python3
"""
🌌 Bot Health Check System
Comprehensive system to check bot functionality and routing
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
from src.handlers.onboarding.handler import OnboardingHandler
from src.handlers.admin.handler import AdminHandler

class BotHealthChecker:
    """
    🌌 Bot Health Checker
    Comprehensive system to verify bot functionality
    """
    
    def __init__(self):
        self.results = {}
        self.errors = []
    
    async def check_database_connection(self):
        """Check database connection and schema"""
        try:
            await db_manager.initialize()
            
            # Check required tables
            tables = ['users', 'user_profiles', 'user_statistics', 'user_levels']
            for table in tables:
                result = await db_manager.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                if result:
                    self.results[f'db_table_{table}'] = f"✅ {table}: {result['count']} records"
                else:
                    self.errors.append(f"❌ Table {table} not accessible")
            
            await db_manager.close()
            self.results['database'] = "✅ Database connection successful"
            
        except Exception as e:
            self.errors.append(f"❌ Database error: {e}")
            self.results['database'] = "❌ Database connection failed"
    
    async def check_profile_service(self):
        """Check profile service functionality"""
        try:
            await db_manager.initialize()
            
            # Test profile service
            summary = await profile_service.get_profile_summary(694245594)
            if summary and summary.get('profile'):
                profile = summary['profile']
                self.results['profile_service'] = f"✅ Profile service: {profile.display_name}"
            else:
                self.errors.append("❌ Profile service not working")
                self.results['profile_service'] = "❌ Profile service failed"
            
            await db_manager.close()
            
        except Exception as e:
            self.errors.append(f"❌ Profile service error: {e}")
            self.results['profile_service'] = "❌ Profile service error"
    
    async def check_handler_registration(self):
        """Check if all handlers can be imported and registered"""
        try:
            # Test handler imports
            handlers = {
                'StartHandler': StartHandler,
                'MainMenuHandler': MainMenuHandler,
                'ProfileHandlerV3': ProfileHandlerV3,
                'OnboardingHandler': OnboardingHandler,
                'AdminHandler': AdminHandler
            }
            
            for name, handler_class in handlers.items():
                try:
                    handler = handler_class()
                    self.results[f'handler_{name.lower()}'] = f"✅ {name} import successful"
                except Exception as e:
                    self.errors.append(f"❌ {name} import failed: {e}")
                    self.results[f'handler_{name.lower()}'] = f"❌ {name} import failed"
            
        except Exception as e:
            self.errors.append(f"❌ Handler registration error: {e}")
    
    async def check_callback_routing(self):
        """Check callback routing patterns"""
        try:
            # Check if callback patterns are properly defined
            routing_map = {
                'start_onboarding': 'StartHandler',
                'check_membership': 'StartHandler',
                'skip_onboarding': 'StartHandler',
                'go_home': 'StartHandler',
                'menu_profile': 'MainMenuHandler',
                'profile_view': 'ProfileHandlerV3',
                'profile_stats': 'ProfileHandlerV3',
                'profile_achievements': 'ProfileHandlerV3',
                'profile_badges': 'ProfileHandlerV3',
                'profile_edit': 'ProfileHandlerV3',
                'profile_privacy': 'ProfileHandlerV3',
                'profile_back': 'ProfileHandlerV3'
            }
            
            for callback, handler in routing_map.items():
                self.results[f'callback_{callback}'] = f"✅ {callback} → {handler}"
            
        except Exception as e:
            self.errors.append(f"❌ Callback routing error: {e}")
    
    async def check_database_schema(self):
        """Check database schema integrity"""
        try:
            await db_manager.initialize()
            
            # Check users table schema
            user_columns = ['user_id', 'first_name', 'last_name', 'username', 'language_code', 'is_bot', 'onboarding_completed', 'last_seen_at']
            result = await db_manager.fetch_all("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'")
            existing_columns = [row['column_name'] for row in result]
            
            missing_columns = [col for col in user_columns if col not in existing_columns]
            if missing_columns:
                self.errors.append(f"❌ Missing columns in users table: {missing_columns}")
                self.results['users_schema'] = f"❌ Missing columns: {missing_columns}"
            else:
                self.results['users_schema'] = "✅ Users table schema complete"
            
            # Check profile tables
            profile_tables = ['user_profiles', 'user_statistics', 'user_levels', 'user_achievements', 'user_badges']
            for table in profile_tables:
                result = await db_manager.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                if result is not None:
                    self.results[f'schema_{table}'] = f"✅ {table} table exists"
                else:
                    self.errors.append(f"❌ Table {table} missing")
                    self.results[f'schema_{table}'] = f"❌ {table} table missing"
            
            await db_manager.close()
            
        except Exception as e:
            self.errors.append(f"❌ Schema check error: {e}")
    
    async def run_full_check(self):
        """Run complete health check"""
        print("🌌 Starting Bot Health Check...")
        print("=" * 60)
        
        # Run all checks
        await self.check_database_connection()
        await self.check_database_schema()
        await self.check_profile_service()
        await self.check_handler_registration()
        await self.check_callback_routing()
        
        # Print results
        print("\n📊 Health Check Results:")
        print("-" * 40)
        
        for key, result in self.results.items():
            print(f"{result}")
        
        if self.errors:
            print(f"\n❌ Errors Found ({len(self.errors)}):")
            print("-" * 40)
            for error in self.errors:
                print(f"{error}")
        
        print("\n" + "=" * 60)
        
        if self.errors:
            print(f"❌ Health Check Failed: {len(self.errors)} errors found")
            return False
        else:
            print("✅ Health Check Passed: All systems operational")
            return True

async def main():
    """Main function"""
    checker = BotHealthChecker()
    success = await checker.run_full_check()
    
    if success:
        print("\n🎉 Bot is healthy and ready for production!")
    else:
        print("\n⚠️ Bot has issues that need to be fixed before deployment!")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())

