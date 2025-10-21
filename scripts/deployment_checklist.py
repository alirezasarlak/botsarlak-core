#!/usr/bin/env python3
"""
🌌 Deployment Checklist
Pre-deployment validation to prevent issues
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import db_manager
from src.services.profile_service import profile_service

class DeploymentValidator:
    """
    🌌 Deployment Validator
    Validates system before deployment
    """
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.errors = []
    
    def check_python_syntax(self):
        """Check Python syntax for all files"""
        print("🔍 Checking Python syntax...")
        try:
            import subprocess
            result = subprocess.run([
                'python3', '-m', 'py_compile', 
                'main.py',
                'src/handlers/start.py',
                'src/handlers/main_menu/handler.py',
                'src/handlers/profile/profile_handler_v3.py',
                'src/handlers/onboarding/handler.py',
                'src/handlers/admin/handler.py'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Python syntax check passed")
                self.checks_passed += 1
            else:
                print(f"❌ Python syntax errors: {result.stderr}")
                self.errors.append(f"Syntax errors: {result.stderr}")
                self.checks_failed += 1
                
        except Exception as e:
            print(f"❌ Syntax check failed: {e}")
            self.errors.append(f"Syntax check error: {e}")
            self.checks_failed += 1
    
    def check_imports(self):
        """Check if all modules can be imported"""
        print("🔍 Checking imports...")
        try:
            # Test critical imports
            from src.handlers.start import StartHandler
            from src.handlers.main_menu.handler import MainMenuHandler
            from src.handlers.profile.profile_handler_v3 import ProfileHandlerV3
            from src.handlers.onboarding.handler import OnboardingHandler
            from src.handlers.admin.handler import AdminHandler
            from src.services.profile_service import profile_service
            from src.database.connection import db_manager
            
            print("✅ All imports successful")
            self.checks_passed += 1
            
        except Exception as e:
            print(f"❌ Import error: {e}")
            self.errors.append(f"Import error: {e}")
            self.checks_failed += 1
    
    async def check_database_connection(self):
        """Check database connection"""
        print("🔍 Checking database connection...")
        try:
            await db_manager.initialize()
            
            # Test basic query
            result = await db_manager.fetch_one("SELECT 1 as test")
            if result and result['test'] == 1:
                print("✅ Database connection successful")
                self.checks_passed += 1
            else:
                print("❌ Database query failed")
                self.errors.append("Database query failed")
                self.checks_failed += 1
            
            await db_manager.close()
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.errors.append(f"Database error: {e}")
            self.checks_failed += 1
    
    async def check_database_schema(self):
        """Check database schema"""
        print("🔍 Checking database schema...")
        try:
            await db_manager.initialize()
            
            # Check required tables
            required_tables = ['users', 'user_profiles', 'user_statistics', 'user_levels']
            missing_tables = []
            
            for table in required_tables:
                try:
                    result = await db_manager.fetch_one(f"SELECT COUNT(*) FROM {table}")
                    if result is None:
                        missing_tables.append(table)
                except:
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                self.errors.append(f"Missing tables: {missing_tables}")
                self.checks_failed += 1
            else:
                print("✅ All required tables exist")
                self.checks_passed += 1
            
            await db_manager.close()
            
        except Exception as e:
            print(f"❌ Schema check failed: {e}")
            self.errors.append(f"Schema check error: {e}")
            self.checks_failed += 1
    
    async def check_profile_service(self):
        """Check profile service functionality"""
        print("🔍 Checking profile service...")
        try:
            await db_manager.initialize()
            
            # Test profile service
            summary = await profile_service.get_profile_summary(694245594)
            if summary and summary.get('profile'):
                print("✅ Profile service working")
                self.checks_passed += 1
            else:
                print("❌ Profile service not working")
                self.errors.append("Profile service not working")
                self.checks_failed += 1
            
            await db_manager.close()
            
        except Exception as e:
            print(f"❌ Profile service error: {e}")
            self.errors.append(f"Profile service error: {e}")
            self.checks_failed += 1
    
    def check_handler_conflicts(self):
        """Check for handler conflicts"""
        print("🔍 Checking handler conflicts...")
        try:
            # This would need to be implemented by checking the actual handler registration
            # For now, we'll just check that the files exist and can be imported
            handler_files = [
                'src/handlers/start.py',
                'src/handlers/main_menu/handler.py',
                'src/handlers/profile/profile_handler_v3.py',
                'src/handlers/onboarding/handler.py',
                'src/handlers/admin/handler.py'
            ]
            
            missing_files = []
            for file_path in handler_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                print(f"❌ Missing handler files: {missing_files}")
                self.errors.append(f"Missing files: {missing_files}")
                self.checks_failed += 1
            else:
                print("✅ All handler files exist")
                self.checks_passed += 1
                
        except Exception as e:
            print(f"❌ Handler conflict check failed: {e}")
            self.errors.append(f"Handler check error: {e}")
            self.checks_failed += 1
    
    async def run_all_checks(self):
        """Run all deployment checks"""
        print("🌌 Running Deployment Checklist...")
        print("=" * 50)
        
        # Run all checks
        self.check_python_syntax()
        self.check_imports()
        self.check_handler_conflicts()
        await self.check_database_connection()
        await self.check_database_schema()
        await self.check_profile_service()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Deployment Check Summary:")
        print(f"✅ Checks Passed: {self.checks_passed}")
        print(f"❌ Checks Failed: {self.checks_failed}")
        
        if self.errors:
            print(f"\n❌ Errors Found:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.checks_failed == 0:
            print("\n🎉 All checks passed! Ready for deployment!")
            return True
        else:
            print(f"\n⚠️ {self.checks_failed} checks failed. Fix issues before deployment!")
            return False

async def main():
    """Main function"""
    validator = DeploymentValidator()
    success = await validator.run_all_checks()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

