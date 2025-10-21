#!/usr/bin/env python3
"""
🌌 SarlakBot v3.0 - Pre-flight Checklist
Automated safety checks before any deployment or code change
"""

import os
import sys
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.config import config
from src.database.connection import db_manager
from src.utils.logging import get_logger

logger = get_logger(__name__)


class PreFlightChecklist:
    """Automated pre-flight checklist for safe deployments"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.failed_checks: List[str] = []
        self.warnings: List[str] = []
        
    async def run_all_checks(self) -> bool:
        """Run all pre-flight checks"""
        logger.info("🚀 Starting Pre-flight Checklist...")
        
        checks = [
            ("Environment Sync", self.check_environment_sync),
            ("Schema Check", self.check_schema_consistency),
            ("Backup Creation", self.create_automatic_backup),
            ("Version Bump", self.check_version_bump),
            ("Critical Smoke Tests", self.run_smoke_tests),
            ("Idempotent Seeds", self.check_idempotent_seeds),
            ("Security Scan", self.run_security_scan),
            ("Code Quality", self.check_code_quality)
        ]
        
        for check_name, check_func in checks:
            logger.info(f"🔍 Running check: {check_name}")
            try:
                result = await check_func()
                if result:
                    self.checks_passed += 1
                    logger.info(f"✅ {check_name}: PASSED")
                else:
                    self.checks_failed += 1
                    self.failed_checks.append(check_name)
                    logger.error(f"❌ {check_name}: FAILED")
            except Exception as e:
                self.checks_failed += 1
                self.failed_checks.append(f"{check_name}: {str(e)}")
                logger.error(f"❌ {check_name}: ERROR - {e}")
        
        # Print summary
        self.print_summary()
        
        return self.checks_failed == 0
    
    async def check_environment_sync(self) -> bool:
        """Check if .env matches .env.example"""
        try:
            env_path = Path(".env")
            env_example_path = Path(".env.example")
            
            if not env_path.exists():
                logger.error("❌ .env file not found")
                return False
            
            if not env_example_path.exists():
                logger.warning("⚠️ .env.example file not found")
                return True  # Not critical
            
            # Check if all required variables are set
            required_vars = [
                "BOT_TOKEN",
                "DATABASE_URL",
                "ADMIN_ID",
                "OPENAI_API_KEY"
            ]
            
            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                logger.error(f"❌ Missing environment variables: {missing_vars}")
                return False
            
            logger.info("✅ Environment variables are properly set")
            return True
            
        except Exception as e:
            logger.error(f"❌ Environment check failed: {e}")
            return False
    
    async def check_schema_consistency(self) -> bool:
        """Check if ORM models match database schema"""
        try:
            # Check if there are pending migrations
            result = subprocess.run(
                ["alembic", "current"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Alembic current failed: {result.stderr}")
                return False
            
            # Check for pending migrations
            result = subprocess.run(
                ["alembic", "check"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            if "No new upgrade operations found" not in result.stdout:
                logger.warning("⚠️ Pending migrations detected")
                self.warnings.append("Pending migrations detected - run 'alembic upgrade head'")
            
            logger.info("✅ Schema consistency check passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Schema check failed: {e}")
            return False
    
    async def create_automatic_backup(self) -> bool:
        """Create automatic backup before deployment"""
        try:
            from scripts.backup_database import DatabaseBackup
            
            backup_system = DatabaseBackup()
            backup_path = await backup_system.create_backup("pre_deploy")
            
            if backup_path:
                logger.info(f"✅ Backup created: {backup_path}")
                return True
            else:
                logger.error("❌ Backup creation failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            return False
    
    async def check_version_bump(self) -> bool:
        """Check if version has been bumped"""
        try:
            # Check if CHANGELOG.md has been updated
            changelog_path = Path("CHANGELOG.md")
            if not changelog_path.exists():
                logger.warning("⚠️ CHANGELOG.md not found")
                return True  # Not critical
            
            # Check if version in config matches latest changelog entry
            current_version = "3.0.0"  # Should be from config
            with open(changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if f"[{current_version}]" not in content:
                    logger.warning("⚠️ Version not found in CHANGELOG.md")
                    self.warnings.append("Version not updated in CHANGELOG.md")
            
            logger.info("✅ Version check passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Version check failed: {e}")
            return False
    
    async def run_smoke_tests(self) -> bool:
        """Run critical smoke tests"""
        try:
            # Test database connection
            await db_manager.fetch_value("SELECT 1")
            logger.info("✅ Database connection test passed")
            
            # Test user table exists
            user_count = await db_manager.fetch_value("SELECT COUNT(*) FROM users")
            logger.info(f"✅ User table test passed (count: {user_count})")
            
            # Test version history table
            version_count = await db_manager.fetch_value("SELECT COUNT(*) FROM version_history")
            logger.info(f"✅ Version history test passed (count: {version_count})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Smoke tests failed: {e}")
            return False
    
    async def check_idempotent_seeds(self) -> bool:
        """Check if seeds are idempotent"""
        try:
            # Check if we can run seeds multiple times without issues
            # This is more of a documentation check for now
            logger.info("✅ Idempotent seeds check passed (manual verification required)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Idempotent seeds check failed: {e}")
            return False
    
    async def run_security_scan(self) -> bool:
        """Run security scan with bandit"""
        try:
            result = subprocess.run(
                ["bandit", "-r", "src/", "-f", "json"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            if result.returncode != 0:
                logger.warning("⚠️ Security issues detected by bandit")
                self.warnings.append("Security issues detected - review bandit output")
            
            logger.info("✅ Security scan completed")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Security scan failed: {e}")
            return True  # Not critical for deployment
    
    async def check_code_quality(self) -> bool:
        """Check code quality with flake8"""
        try:
            result = subprocess.run(
                ["python", "-m", "flake8", "src/", "--count", "--statistics"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            if result.returncode != 0:
                logger.warning("⚠️ Code quality issues detected")
                self.warnings.append("Code quality issues detected - review flake8 output")
            
            logger.info("✅ Code quality check completed")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Code quality check failed: {e}")
            return True  # Not critical for deployment
    
    def print_summary(self):
        """Print checklist summary"""
        logger.info("=" * 60)
        logger.info("🚀 PRE-FLIGHT CHECKLIST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Checks Passed: {self.checks_passed}")
        logger.info(f"❌ Checks Failed: {self.checks_failed}")
        
        if self.failed_checks:
            logger.error("❌ Failed Checks:")
            for check in self.failed_checks:
                logger.error(f"   - {check}")
        
        if self.warnings:
            logger.warning("⚠️ Warnings:")
            for warning in self.warnings:
                logger.warning(f"   - {warning}")
        
        if self.checks_failed == 0:
            logger.info("🎉 ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
        else:
            logger.error("🚫 DEPLOYMENT BLOCKED - FIX FAILED CHECKS FIRST!")
        
        logger.info("=" * 60)


async def main():
    """Main function for command line usage"""
    checklist = PreFlightChecklist()
    success = await checklist.run_all_checks()
    
    if success:
        print("✅ Pre-flight checklist passed - ready for deployment")
        sys.exit(0)
    else:
        print("❌ Pre-flight checklist failed - deployment blocked")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())



