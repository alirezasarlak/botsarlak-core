#!/usr/bin/env python3
"""
🌌 SarlakBot v3.0 - Database Backup System
Automated backup system for PostgreSQL database
"""

import os
import sys
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.config import config
from src.utils.logging import get_logger

logger = get_logger(__name__)


class DatabaseBackup:
    """Professional database backup system"""
    
    def __init__(self):
        self.db_config = config.database
        self.backup_dir = Path("/home/ali/botsarlak/backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup_filename(self, backup_type: str = "manual") -> str:
        """Create backup filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"sarlakdb_{backup_type}_{timestamp}.sql"
    
    async def create_backup(self, backup_type: str = "manual") -> Optional[str]:
        """Create database backup"""
        try:
            filename = self.create_backup_filename(backup_type)
            backup_path = self.backup_dir / filename
            
            logger.info(f"💾 Creating database backup: {filename}")
            
            # Set environment variables for pg_dump
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config.password
            
            # Build pg_dump command
            cmd = [
                'pg_dump',
                '-h', self.db_config.host,
                '-p', str(self.db_config.port),
                '-U', self.db_config.user,
                '-d', self.db_config.name,
                '--verbose',
                '--no-password',
                '--format=custom',
                '--compress=9',
                '--file', str(backup_path)
            ]
            
            # Execute backup
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Backup created successfully: {backup_path}")
                
                # Get file size
                file_size = backup_path.stat().st_size
                logger.info(f"📊 Backup size: {file_size / 1024 / 1024:.2f} MB")
                
                return str(backup_path)
            else:
                logger.error(f"❌ Backup failed: {result.stderr}")
                return None
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Backup command failed: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            return None
    
    async def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            if not Path(backup_path).exists():
                logger.error(f"❌ Backup file not found: {backup_path}")
                return False
            
            logger.info(f"🔄 Restoring database from: {backup_path}")
            
            # Set environment variables for pg_restore
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config.password
            
            # Build pg_restore command
            cmd = [
                'pg_restore',
                '-h', self.db_config.host,
                '-p', str(self.db_config.port),
                '-U', self.db_config.user,
                '-d', self.db_config.name,
                '--verbose',
                '--no-password',
                '--clean',
                '--if-exists',
                backup_path
            ]
            
            # Execute restore
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Database restored successfully from: {backup_path}")
                return True
            else:
                logger.error(f"❌ Restore failed: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Restore command failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            return False
    
    async def cleanup_old_backups(self, keep_days: int = 7) -> int:
        """Clean up old backup files"""
        try:
            logger.info(f"🧹 Cleaning up backups older than {keep_days} days")
            
            cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
            deleted_count = 0
            
            for backup_file in self.backup_dir.glob("sarlakdb_*.sql"):
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    deleted_count += 1
                    logger.info(f"🗑️ Deleted old backup: {backup_file.name}")
            
            logger.info(f"✅ Cleanup completed. Deleted {deleted_count} old backups")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return 0
    
    async def list_backups(self) -> list:
        """List all available backups"""
        try:
            backups = []
            for backup_file in self.backup_dir.glob("sarlakdb_*.sql"):
                stat = backup_file.stat()
                backups.append({
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"❌ Failed to list backups: {e}")
            return []
    
    async def verify_backup(self, backup_path: str) -> bool:
        """Verify backup file integrity"""
        try:
            if not Path(backup_path).exists():
                logger.error(f"❌ Backup file not found: {backup_path}")
                return False
            
            logger.info(f"🔍 Verifying backup: {backup_path}")
            
            # Set environment variables
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config.password
            
            # Use pg_restore --list to verify backup
            cmd = [
                'pg_restore',
                '--list',
                '--file', '/dev/null',
                backup_path
            ]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Backup verification successful: {backup_path}")
                return True
            else:
                logger.error(f"❌ Backup verification failed: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Backup verification command failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Backup verification failed: {e}")
            return False


async def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SarlakBot Database Backup System")
    parser.add_argument("action", choices=["backup", "restore", "list", "cleanup", "verify"],
                       help="Action to perform")
    parser.add_argument("--file", help="Backup file path (for restore/verify)")
    parser.add_argument("--type", default="manual", help="Backup type (manual, daily, weekly)")
    parser.add_argument("--keep-days", type=int, default=7, help="Days to keep backups (for cleanup)")
    
    args = parser.parse_args()
    
    backup_system = DatabaseBackup()
    
    if args.action == "backup":
        result = await backup_system.create_backup(args.type)
        if result:
            print(f"✅ Backup created: {result}")
            sys.exit(0)
        else:
            print("❌ Backup failed")
            sys.exit(1)
    
    elif args.action == "restore":
        if not args.file:
            print("❌ --file argument required for restore")
            sys.exit(1)
        
        success = await backup_system.restore_backup(args.file)
        if success:
            print("✅ Database restored successfully")
            sys.exit(0)
        else:
            print("❌ Restore failed")
            sys.exit(1)
    
    elif args.action == "list":
        backups = await backup_system.list_backups()
        if backups:
            print("📋 Available backups:")
            for backup in backups:
                size_mb = backup['size'] / 1024 / 1024
                print(f"  {backup['filename']} ({size_mb:.2f} MB) - {backup['created']}")
        else:
            print("📋 No backups found")
    
    elif args.action == "cleanup":
        deleted = await backup_system.cleanup_old_backups(args.keep_days)
        print(f"✅ Cleanup completed. Deleted {deleted} old backups")
    
    elif args.action == "verify":
        if not args.file:
            print("❌ --file argument required for verify")
            sys.exit(1)
        
        success = await backup_system.verify_backup(args.file)
        if success:
            print("✅ Backup verification successful")
            sys.exit(0)
        else:
            print("❌ Backup verification failed")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())



