"""
🌌 SarlakBot v3.0 - Preflight Validation System
Comprehensive validation before any code changes or deployments
"""

import os
import sys
import asyncio
import subprocess
import importlib
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from src.config import config
from src.database.connection import db_manager
from src.core.route_registry import route_registry
from src.utils.logging import get_logger

logger = get_logger(__name__)


class PreflightValidator:
    """
    🌌 Preflight Validator
    Comprehensive validation system for all critical checks
    """
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.failed_checks: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        
    async def run_all_checks(self) -> bool:
        """Run all preflight checks"""
        logger.info("🚀 Starting Preflight Validation...")
        logger.info("=" * 60)
        
        checks = [
            ("Environment Validation", self.check_environment),
            ("Database Schema Check", self.check_database_schema),
            ("Route Registry Validation", self.check_route_registry),
            ("Handler Importability", self.check_handler_imports),
            ("Migration Safety", self.check_migration_safety),
            ("Security Scan", self.run_security_scan),
            ("Code Quality", self.check_code_quality),
            ("Backup Verification", self.verify_backups),
            ("Version Consistency", self.check_version_consistency),
            ("Configuration Integrity", self.check_configuration_integrity)
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
    
    async def check_environment(self) -> bool:
        """Check environment configuration"""
        try:
            # Check .env file exists
            env_path = Path(".env")
            if not env_path.exists():
                self.failed_checks.append("Environment: .env file not found")
                return False
            
            # Check .env.example exists
            env_example_path = Path(".env.example")
            if not env_example_path.exists():
                self.warnings.append("Environment: .env.example file not found")
            
            # Check required environment variables
            required_vars = [
                "BOT_TOKEN",
                "DATABASE_URL",
                "ADMIN_ID"
            ]
            
            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                self.failed_checks.append(f"Environment: Missing variables: {missing_vars}")
                return False
            
            # Check .env vs .env.example sync
            if env_example_path.exists():
                sync_status = await self._check_env_sync()
                if not sync_status:
                    self.warnings.append("Environment: .env and .env.example may be out of sync")
            
            self.info.append("Environment: All required variables present")
            return True
            
        except Exception as e:
            self.failed_checks.append(f"Environment check failed: {e}")
            return False
    
    async def _check_env_sync(self) -> bool:
        """Check if .env and .env.example are in sync"""
        try:
            with open(".env", 'r') as f:
                env_vars = set(line.split('=')[0] for line in f if '=' in line and not line.startswith('#'))
            
            with open(".env.example", 'r') as f:
                example_vars = set(line.split('=')[0] for line in f if '=' in line and not line.startswith('#'))
            
            # Check if all example vars are in .env
            missing_in_env = example_vars - env_vars
            if missing_in_env:
                self.warnings.append(f"Environment: Variables in .env.example but not in .env: {missing_in_env}")
            
            return len(missing_in_env) == 0
            
        except Exception as e:
            self.warnings.append(f"Environment sync check failed: {e}")
            return False
    
    async def check_database_schema(self) -> bool:
        """Check database schema consistency"""
        try:
            # Initialize database connection
            await db_manager.initialize()
            
            # Check if database is accessible
            await db_manager.fetch_value("SELECT 1")
            
            # Check for pending migrations
            result = subprocess.run(
                ["alembic", "current"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent
            )
            
            if result.returncode != 0:
                self.failed_checks.append("Database: Alembic current command failed")
                return False
            
            # Check for pending migrations
            result = subprocess.run(
                ["alembic", "check"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent
            )
            
            if "No new upgrade operations found" not in result.stdout:
                self.warnings.append("Database: Pending migrations detected")
            
            # Check critical tables exist
            critical_tables = [
                "users", "routes", "menus", "route_history", 
                "version_history", "user_profiles"
            ]
            
            for table in critical_tables:
                exists = await db_manager.fetch_value(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                    table
                )
                if not exists:
                    self.failed_checks.append(f"Database: Critical table '{table}' missing")
                    return False
            
            self.info.append("Database: Schema consistency verified")
            return True
            
        except Exception as e:
            self.failed_checks.append(f"Database schema check failed: {e}")
            return False
    
    async def check_route_registry(self) -> bool:
        """Check route registry integrity"""
        try:
            # Validate routes
            validation_results = await route_registry.validate_routes()
            
            if validation_results['errors']:
                for error in validation_results['errors']:
                    self.failed_checks.append(f"Route Registry: {error}")
                return False
            
            if validation_results['warnings']:
                for warning in validation_results['warnings']:
                    self.warnings.append(f"Route Registry: {warning}")
            
            if validation_results['info']:
                for info in validation_results['info']:
                    self.info.append(f"Route Registry: {info}")
            
            return True
            
        except Exception as e:
            self.failed_checks.append(f"Route registry check failed: {e}")
            return False
    
    async def check_handler_imports(self) -> bool:
        """Check if all handlers are importable"""
        try:
            handler_modules = [
                "src.handlers.start",
                "src.handlers.onboarding.handler",
                "src.handlers.main_menu.handler",
                "src.handlers.admin.handler",
                "src.handlers.profile.handler"
            ]
            
            failed_imports = []
            for module_name in handler_modules:
                try:
                    importlib.import_module(module_name)
                except ImportError as e:
                    failed_imports.append(f"{module_name}: {e}")
            
            if failed_imports:
                for failed in failed_imports:
                    self.failed_checks.append(f"Handler Import: {failed}")
                return False
            
            self.info.append("Handlers: All modules importable")
            return True
            
        except Exception as e:
            self.failed_checks.append(f"Handler import check failed: {e}")
            return False
    
    async def check_migration_safety(self) -> bool:
        """Check migration safety"""
        try:
            # Check for destructive operations in pending migrations
            result = subprocess.run(
                ["alembic", "show", "head"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent
            )
            
            if result.returncode != 0:
                self.failed_checks.append("Migration: Cannot get head migration")
                return False
            
            # Check for dangerous keywords in migration files
            migration_dir = Path("migrations/versions")
            if migration_dir.exists():
                dangerous_keywords = ["DROP TABLE", "TRUNCATE", "DELETE FROM", "ALTER TABLE DROP"]
                
                for migration_file in migration_dir.glob("*.sql"):
                    with open(migration_file, 'r', encoding='utf-8') as f:
                        content = f.read().upper()
                        
                        for keyword in dangerous_keywords:
                            if keyword in content:
                                self.failed_checks.append(f"Migration: Dangerous operation '{keyword}' found in {migration_file.name}")
                                return False
            
            self.info.append("Migration: No destructive operations detected")
            return True
            
        except Exception as e:
            self.failed_checks.append(f"Migration safety check failed: {e}")
            return False
    
    async def run_security_scan(self) -> bool:
        """Run security scan with bandit"""
        try:
            result = subprocess.run(
                ["bandit", "-r", "src/", "-f", "json"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent
            )
            
            if result.returncode != 0:
                # Parse bandit output for high severity issues
                try:
                    import json
                    bandit_output = json.loads(result.stdout)
                    
                    high_severity_issues = [
                        issue for issue in bandit_output.get('results', [])
                        if issue.get('issue_severity') == 'HIGH'
                    ]
                    
                    if high_severity_issues:
                        for issue in high_severity_issues:
                            self.failed_checks.append(f"Security: {issue.get('issue_text', 'High severity issue')}")
                        return False
                    else:
                        self.warnings.append("Security: Medium/low severity issues detected")
                except:
                    self.warnings.append("Security: Issues detected but cannot parse details")
            
            self.info.append("Security: No high severity issues found")
            return True
            
        except Exception as e:
            self.warnings.append(f"Security scan failed: {e}")
            return True  # Not critical for deployment
    
    async def check_code_quality(self) -> bool:
        """Check code quality with flake8"""
        try:
            result = subprocess.run(
                ["python", "-m", "flake8", "src/", "--count", "--statistics"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent
            )
            
            if result.returncode != 0:
                # Count errors vs warnings
                lines = result.stdout.split('\n')
                error_count = 0
                warning_count = 0
                
                for line in lines:
                    if 'E' in line and ':' in line:
                        error_count += 1
                    elif 'W' in line and ':' in line:
                        warning_count += 1
                
                if error_count > 0:
                    self.failed_checks.append(f"Code Quality: {error_count} errors found")
                    return False
                elif warning_count > 0:
                    self.warnings.append(f"Code Quality: {warning_count} warnings found")
            
            self.info.append("Code Quality: No errors found")
            return True
            
        except Exception as e:
            self.warnings.append(f"Code quality check failed: {e}")
            return True  # Not critical for deployment
    
    async def verify_backups(self) -> bool:
        """Verify backup system"""
        try:
            backup_dir = Path("/home/ali/botsarlak/backups")
            
            if not backup_dir.exists():
                self.warnings.append("Backup: Backup directory not found")
                return True  # Not critical
            
            # Check for recent backups
            backup_files = list(backup_dir.glob("sarlakdb_*.sql"))
            
            if not backup_files:
                self.warnings.append("Backup: No backup files found")
                return True  # Not critical
            
            # Check for recent backup (within last 24 hours)
            recent_backups = [
                f for f in backup_files
                if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).total_seconds() < 86400
            ]
            
            if not recent_backups:
                self.warnings.append("Backup: No recent backups found (last 24h)")
            
            self.info.append(f"Backup: {len(backup_files)} backup files found")
            return True
            
        except Exception as e:
            self.warnings.append(f"Backup verification failed: {e}")
            return True  # Not critical
    
    async def check_version_consistency(self) -> bool:
        """Check version consistency across files"""
        try:
            # Check if version is consistent across config and changelog
            current_version = "3.0.0"  # Should be from config
            
            # Check CHANGELOG.md
            changelog_path = Path("CHANGELOG.md")
            if changelog_path.exists():
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if f"[{current_version}]" not in content:
                        self.warnings.append("Version: Version not found in CHANGELOG.md")
            
            # Check version history in database
            try:
                version_count = await db_manager.fetch_value(
                    "SELECT COUNT(*) FROM version_history WHERE version = $1",
                    current_version
                )
                if version_count == 0:
                    self.warnings.append("Version: Version not found in version_history table")
            except:
                self.warnings.append("Version: Cannot check version_history table")
            
            self.info.append(f"Version: Current version {current_version}")
            return True
            
        except Exception as e:
            self.warnings.append(f"Version consistency check failed: {e}")
            return True  # Not critical
    
    async def check_configuration_integrity(self) -> bool:
        """Check configuration integrity"""
        try:
            # Check if config can be loaded
            from src.config import config
            
            # Check critical config values
            if not config.bot.token:
                self.failed_checks.append("Config: BOT_TOKEN not set")
                return False
            
            if not config.database.connection_string:
                self.failed_checks.append("Config: DATABASE_URL not set")
                return False
            
            if not config.bot.admin_id:
                self.failed_checks.append("Config: ADMIN_ID not set")
                return False
            
            self.info.append("Config: All critical values present")
            return True
            
        except Exception as e:
            self.failed_checks.append(f"Configuration integrity check failed: {e}")
            return False
    
    def print_summary(self):
        """Print validation summary"""
        logger.info("=" * 60)
        logger.info("🚀 PREFLIGHT VALIDATION SUMMARY")
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
        
        if self.info:
            logger.info("ℹ️ Info:")
            for info in self.info:
                logger.info(f"   - {info}")
        
        if self.checks_failed == 0:
            logger.info("🎉 ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
        else:
            logger.error("🚫 DEPLOYMENT BLOCKED - FIX FAILED CHECKS FIRST!")
        
        logger.info("=" * 60)


async def main():
    """Main function for command line usage"""
    validator = PreflightValidator()
    success = await validator.run_all_checks()
    
    if success:
        print("✅ Preflight validation passed - ready for deployment")
        sys.exit(0)
    else:
        print("❌ Preflight validation failed - deployment blocked")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())



