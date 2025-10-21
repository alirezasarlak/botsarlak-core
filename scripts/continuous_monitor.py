#!/usr/bin/env python3
"""
SarlakBot v6 Full - Continuous Monitoring Script
Monitors code changes and triggers audit loop automatically
"""

import os
import sys
import time
import subprocess
import datetime
from pathlib import Path
from typing import List, Dict, Any
import hashlib

class ContinuousMonitor:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.monitor_file = self.project_root / ".cursor-metrics.log"
        self.last_check = None
        self.file_hashes = {}
        
    def start_monitoring(self):
        """Start continuous monitoring"""
        print("🔄 Starting continuous monitoring for SarlakBot v6 Full...")
        print("📊 Monitoring code changes and triggering audit loop...")
        
        try:
            while True:
                self._check_for_changes()
                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
    
    def _check_for_changes(self):
        """Check for file changes and trigger audit if needed"""
        current_time = datetime.datetime.now()
        
        # Get list of Python files
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not str(f).startswith(str(self.project_root / ".venv"))]
        
        changes_detected = False
        
        for file_path in python_files:
            try:
                # Calculate file hash
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                # Check if file has changed
                if str(file_path) in self.file_hashes:
                    if self.file_hashes[str(file_path)] != file_hash:
                        changes_detected = True
                        self._log_change(file_path, "modified")
                else:
                    changes_detected = True
                    self._log_change(file_path, "new")
                
                self.file_hashes[str(file_path)] = file_hash
                
            except Exception as e:
                print(f"⚠️ Error checking {file_path}: {e}")
        
        if changes_detected:
            print(f"🔄 Changes detected at {current_time}")
            self._trigger_audit_loop()
        
        self.last_check = current_time
    
    def _log_change(self, file_path: Path, change_type: str):
        """Log file changes"""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] {change_type.upper()}: {file_path.relative_to(self.project_root)}\n"
        
        with open(self.monitor_file, 'a') as f:
            f.write(log_entry)
        
        print(f"📝 {change_type}: {file_path.name}")
    
    def _trigger_audit_loop(self):
        """Trigger the audit loop"""
        print("🧠 Triggering audit loop...")
        
        try:
            # Run quick checks
            self._run_quick_checks()
            
            # Run full audit if needed
            if self._should_run_full_audit():
                self._run_full_audit()
            
        except Exception as e:
            print(f"❌ Audit loop error: {e}")
    
    def _run_quick_checks(self):
        """Run quick development checks"""
        print("⚡ Running quick checks...")
        
        try:
            # Black formatting check
            result = subprocess.run(
                ["black", "--check", "."],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode != 0:
                print("🎨 Code formatting issues detected")
                self._log_audit_result("black", "fail", result.stdout)
            else:
                self._log_audit_result("black", "pass", "Formatting OK")
            
            # Ruff linting check
            result = subprocess.run(
                ["ruff", "check", ".", "--statistics"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode != 0:
                print("🔍 Linting issues detected")
                self._log_audit_result("ruff", "warn", result.stdout)
            else:
                self._log_audit_result("ruff", "pass", "Linting OK")
            
        except Exception as e:
            print(f"⚠️ Quick checks error: {e}")
    
    def _should_run_full_audit(self) -> bool:
        """Determine if full audit should run"""
        # Run full audit every 10 minutes or if critical issues detected
        if not self.last_check:
            return True
        
        time_diff = datetime.datetime.now() - self.last_check
        return time_diff.total_seconds() > 600  # 10 minutes
    
    def _run_full_audit(self):
        """Run full audit analysis"""
        print("🧠 Running full audit analysis...")
        
        try:
            # Run audit analyzer
            result = subprocess.run(
                [sys.executable, "scripts/audit_analyzer.py"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print("✅ Full audit completed successfully")
                self._log_audit_result("full_audit", "pass", "Full audit completed")
            else:
                print("❌ Full audit failed")
                self._log_audit_result("full_audit", "fail", result.stderr)
            
            # Generate report
            subprocess.run(
                [sys.executable, "scripts/generate_audit_report.py"],
                cwd=self.project_root
            )
            
        except Exception as e:
            print(f"❌ Full audit error: {e}")
    
    def _log_audit_result(self, check_name: str, status: str, output: str):
        """Log audit results"""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] AUDIT {check_name.upper()}: {status.upper()}\n"
        
        if output:
            log_entry += f"Output: {output[:200]}...\n"
        
        log_entry += "\n"
        
        with open(self.monitor_file, 'a') as f:
            f.write(log_entry)
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        stats = {
            "monitor_file": str(self.monitor_file),
            "files_monitored": len(self.file_hashes),
            "last_check": self.last_check.isoformat() if self.last_check else None
        }
        
        if self.monitor_file.exists():
            with open(self.monitor_file, 'r') as f:
                content = f.read()
                stats["log_entries"] = content.count('\n')
                stats["recent_activity"] = content.split('\n')[-10:]  # Last 10 lines
        
        return stats

def main():
    monitor = ContinuousMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--stats":
        # Show monitoring statistics
        stats = monitor.get_monitoring_stats()
        print("📊 Monitoring Statistics:")
        print(f"📁 Monitor file: {stats['monitor_file']}")
        print(f"📝 Files monitored: {stats['files_monitored']}")
        print(f"⏰ Last check: {stats['last_check']}")
        print(f"📋 Log entries: {stats['log_entries']}")
        
        if stats['recent_activity']:
            print("\n🔄 Recent activity:")
            for line in stats['recent_activity']:
                if line.strip():
                    print(f"  {line}")
    else:
        # Start monitoring
        monitor.start_monitoring()

if __name__ == "__main__":
    main()
