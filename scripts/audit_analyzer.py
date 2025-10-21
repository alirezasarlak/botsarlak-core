#!/usr/bin/env python3
"""
SarlakBot v6 Full - Audit Analyzer
Automated code quality and security analysis
"""

import os
import sys
import json
import subprocess
import datetime
from pathlib import Path
from typing import Dict, List, Any

class AuditAnalyzer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.reports_dir = self.project_root / "audit-reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def run_audit_checks(self) -> Dict[str, Any]:
        """Run comprehensive audit checks"""
        print("🧠 Starting SarlakBot v6 Full Audit Analysis...")
        
        results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "project": "SarlakBot v6 Full",
            "version": "6.1.0",
            "checks": {}
        }
        
        # Code quality checks
        results["checks"]["black"] = self._check_black()
        results["checks"]["ruff"] = self._check_ruff()
        results["checks"]["mypy"] = self._check_mypy()
        results["checks"]["pytest"] = self._check_pytest()
        
        # Security checks
        results["checks"]["security"] = self._check_security()
        
        # Performance checks
        results["checks"]["performance"] = self._check_performance()
        
        # Documentation checks
        results["checks"]["documentation"] = self._check_documentation()
        
        return results
    
    def _check_black(self) -> Dict[str, Any]:
        """Check code formatting with Black"""
        try:
            result = subprocess.run(
                ["black", "--check", "--diff", "."],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return {
                "status": "pass" if result.returncode == 0 else "fail",
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_ruff(self) -> Dict[str, Any]:
        """Check linting with Ruff"""
        try:
            result = subprocess.run(
                ["ruff", "check", ".", "--statistics"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return {
                "status": "pass" if result.returncode == 0 else "warn",
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_mypy(self) -> Dict[str, Any]:
        """Check type annotations with MyPy"""
        try:
            result = subprocess.run(
                ["mypy", "app/", "--ignore-missing-imports"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return {
                "status": "pass" if result.returncode == 0 else "warn",
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_pytest(self) -> Dict[str, Any]:
        """Run tests with pytest"""
        try:
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return {
                "status": "pass" if result.returncode == 0 else "fail",
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_security(self) -> Dict[str, Any]:
        """Basic security checks"""
        security_issues = []
        
        # Check for hardcoded secrets
        for file_path in self.project_root.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if any(secret in content.lower() for secret in ['password', 'token', 'key', 'secret']):
                        if not any(env_var in content for env_var in ['os.getenv', 'os.environ']):
                            security_issues.append(f"Potential hardcoded secret in {file_path}")
            except Exception:
                continue
        
        return {
            "status": "pass" if not security_issues else "warn",
            "issues": security_issues
        }
    
    def _check_performance(self) -> Dict[str, Any]:
        """Basic performance checks"""
        performance_issues = []
        
        # Check for large files
        for file_path in self.project_root.rglob("*.py"):
            if file_path.stat().st_size > 10000:  # 10KB
                performance_issues.append(f"Large file detected: {file_path}")
        
        return {
            "status": "pass" if not performance_issues else "warn",
            "issues": performance_issues
        }
    
    def _check_documentation(self) -> Dict[str, Any]:
        """Check documentation completeness"""
        doc_issues = []
        
        # Check for missing docstrings in main modules
        main_modules = ["app/bot.py", "app/config.py", "app/db.py"]
        for module in main_modules:
            module_path = self.project_root / module
            if module_path.exists():
                try:
                    with open(module_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'def ' in content and '"""' not in content:
                            doc_issues.append(f"Missing docstrings in {module}")
                except Exception:
                    continue
        
        return {
            "status": "pass" if not doc_issues else "warn",
            "issues": doc_issues
        }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate markdown audit report"""
        report = f"""# 🧠 SarlakBot v6 Full - Audit Report

**Generated:** {results['timestamp']}  
**Project:** {results['project']}  
**Version:** {results['version']}

## 📊 Audit Summary

"""
        
        for check_name, check_result in results["checks"].items():
            status_emoji = {
                "pass": "✅",
                "warn": "⚠️",
                "fail": "❌",
                "error": "🔥"
            }.get(check_result.get("status", "error"), "❓")
            
            report += f"### {status_emoji} {check_name.title()}\n"
            report += f"**Status:** {check_result.get('status', 'unknown')}\n\n"
            
            if check_result.get("issues"):
                report += "**Issues:**\n"
                for issue in check_result["issues"]:
                    report += f"- {issue}\n"
                report += "\n"
            
            if check_result.get("output"):
                report += "**Output:**\n```\n"
                report += check_result["output"][:500]  # Limit output
                report += "\n```\n\n"
        
        return report
    
    def save_report(self, results: Dict[str, Any], report: str):
        """Save audit results"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.reports_dir / f"audit_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save markdown report
        md_file = self.reports_dir / f"audit_report_{timestamp}.md"
        with open(md_file, 'w') as f:
            f.write(report)
        
        print(f"📊 Audit results saved to: {json_file}")
        print(f"📝 Audit report saved to: {md_file}")

def main():
    analyzer = AuditAnalyzer()
    results = analyzer.run_audit_checks()
    report = analyzer.generate_report(results)
    analyzer.save_report(results, report)
    
    print("🧠 Audit analysis completed!")
    print(f"📊 Overall status: {'✅ PASS' if all(check.get('status') in ['pass', 'warn'] for check in results['checks'].values()) else '❌ FAIL'}")

if __name__ == "__main__":
    main()
