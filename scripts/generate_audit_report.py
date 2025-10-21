#!/usr/bin/env python3
"""
SarlakBot v6 Full - Audit Report Generator
Generates comprehensive audit reports and documentation updates
"""

import datetime
import json
from pathlib import Path
from typing import Any, Dict


class AuditReportGenerator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.reports_dir = self.project_root / "audit-reports"
        self.docs_dir = self.project_root / "docs"
        self.docs_dir.mkdir(exist_ok=True)

    def generate_comprehensive_report(self):
        """Generate comprehensive audit report"""
        print("📝 Generating comprehensive audit report...")

        # Find latest audit results
        latest_results = self._find_latest_audit_results()
        if not latest_results:
            print("❌ No audit results found!")
            return

        # Generate comprehensive report
        report = self._create_comprehensive_report(latest_results)

        # Save report
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.docs_dir / f"AUTO_AUDIT_REPORT_{timestamp}.md"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📊 Comprehensive report saved to: {report_file}")

        # Update main documentation
        self._update_main_documentation(latest_results)

    def _find_latest_audit_results(self) -> Dict[str, Any]:
        """Find the latest audit results JSON file"""
        if not self.reports_dir.exists():
            return None

        json_files = list(self.reports_dir.glob("audit_results_*.json"))
        if not json_files:
            return None

        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)

        try:
            with open(latest_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading audit results: {e}")
            return None

    def _create_comprehensive_report(self, results: Dict[str, Any]) -> str:
        """Create comprehensive audit report"""
        report = f"""# 🧠 SarlakBot v6 Full - Comprehensive Audit Report

**Generated:** {results['timestamp']}  
**Project:** {results['project']}  
**Version:** {results['version']}

## 📋 Executive Summary

This comprehensive audit report provides a detailed analysis of the SarlakBot v6 Full codebase, including code quality, security, performance, and documentation assessments.

## 🔍 Detailed Analysis

"""

        # Code Quality Section
        report += "### 🎨 Code Quality Analysis\n\n"
        for check_name, check_result in results["checks"].items():
            if check_name in ["black", "ruff", "mypy", "pytest"]:
                status_emoji = {
                    "pass": "✅",
                    "warn": "⚠️",
                    "fail": "❌",
                    "error": "🔥",
                }.get(check_result.get("status", "error"), "❓")

                report += f"#### {status_emoji} {check_name.title()}\n"
                report += f"**Status:** {check_result.get('status', 'unknown')}\n\n"

                if check_result.get("output"):
                    report += "**Details:**\n```\n"
                    report += check_result["output"][:1000]  # Limit output
                    report += "\n```\n\n"

        # Security Section
        if "security" in results["checks"]:
            report += "### 🔒 Security Analysis\n\n"
            security_result = results["checks"]["security"]
            report += f"**Status:** {security_result.get('status', 'unknown')}\n\n"

            if security_result.get("issues"):
                report += "**Security Issues Found:**\n"
                for issue in security_result["issues"]:
                    report += f"- {issue}\n"
                report += "\n"

        # Performance Section
        if "performance" in results["checks"]:
            report += "### ⚡ Performance Analysis\n\n"
            perf_result = results["checks"]["performance"]
            report += f"**Status:** {perf_result.get('status', 'unknown')}\n\n"

            if perf_result.get("issues"):
                report += "**Performance Issues Found:**\n"
                for issue in perf_result["issues"]:
                    report += f"- {issue}\n"
                report += "\n"

        # Documentation Section
        if "documentation" in results["checks"]:
            report += "### 📚 Documentation Analysis\n\n"
            doc_result = results["checks"]["documentation"]
            report += f"**Status:** {doc_result.get('status', 'unknown')}\n\n"

            if doc_result.get("issues"):
                report += "**Documentation Issues Found:**\n"
                for issue in doc_result["issues"]:
                    report += f"- {issue}\n"
                report += "\n"

        # Recommendations
        report += "## 💡 Recommendations\n\n"
        report += self._generate_recommendations(results)

        # Next Steps
        report += "## 🚀 Next Steps\n\n"
        report += self._generate_next_steps(results)

        return report

    def _generate_recommendations(self, results: Dict[str, Any]) -> str:
        """Generate recommendations based on audit results"""
        recommendations = []

        for check_name, check_result in results["checks"].items():
            if check_result.get("status") == "fail":
                if check_name == "black":
                    recommendations.append("🔧 Run `black .` to fix formatting issues")
                elif check_name == "pytest":
                    recommendations.append("🧪 Fix failing tests before deployment")
                elif check_name == "ruff":
                    recommendations.append(
                        "🔍 Run `ruff check . --fix` to auto-fix linting issues"
                    )
                elif check_name == "mypy":
                    recommendations.append("🏷️ Add type annotations to fix MyPy errors")

            elif check_result.get("status") == "warn":
                if check_name == "security":
                    recommendations.append(
                        "🔒 Review potential security issues and add proper environment variable handling"
                    )
                elif check_name == "performance":
                    recommendations.append(
                        "⚡ Consider refactoring large files for better maintainability"
                    )
                elif check_name == "documentation":
                    recommendations.append(
                        "📚 Add docstrings to improve code documentation"
                    )

        if not recommendations:
            recommendations.append("✅ All checks passed! Continue with development.")

        return "\n".join(f"- {rec}" for rec in recommendations) + "\n\n"

    def _generate_next_steps(self, results: Dict[str, Any]) -> str:
        """Generate next steps based on audit results"""
        next_steps = [
            "📊 Review this audit report thoroughly",
            "🔧 Address any critical issues identified",
            "🧪 Run tests locally before committing",
            "📝 Update documentation if needed",
            "🚀 Deploy only after all checks pass",
        ]

        return "\n".join(f"- {step}" for step in next_steps) + "\n\n"

    def _update_main_documentation(self, results: Dict[str, Any]):
        """Update main documentation files"""
        print("📝 Updating main documentation...")

        # Update CHANGELOG.md
        self._update_changelog(results)

        # Update VERSION_HISTORY.md
        self._update_version_history(results)

    def _update_changelog(self, results: Dict[str, Any]):
        """Update CHANGELOG.md with audit results"""
        changelog_file = self.project_root / "CHANGELOG.md"

        if changelog_file.exists():
            with open(changelog_file, encoding="utf-8") as f:
                content = f.read()

            # Add audit entry
            audit_entry = f"""
## [Audit] - {results['timestamp']}

### 🧠 Automated Audit Results
- **Code Quality:** {self._get_overall_status(results)}
- **Security:** {results['checks'].get('security', {}).get('status', 'unknown')}
- **Performance:** {results['checks'].get('performance', {}).get('status', 'unknown')}
- **Documentation:** {results['checks'].get('documentation', {}).get('status', 'unknown')}

"""

            # Insert after the first heading
            lines = content.split("\n")
            insert_index = 1
            for i, line in enumerate(lines):
                if line.startswith("## [") and i > 0:
                    insert_index = i
                    break

            lines.insert(insert_index, audit_entry)

            with open(changelog_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

    def _update_version_history(self, results: Dict[str, Any]):
        """Update VERSION_HISTORY.md with audit results"""
        version_file = self.project_root / "VERSION_HISTORY.md"

        if version_file.exists():
            with open(version_file, encoding="utf-8") as f:
                content = f.read()

            # Add audit section
            audit_section = f"""
### 🧠 Audit Results ({results['timestamp']})
- **Overall Status:** {self._get_overall_status(results)}
- **Code Quality Checks:** {len([k for k, v in results['checks'].items() if k in ['black', 'ruff', 'mypy', 'pytest']])} completed
- **Security Issues:** {len(results['checks'].get('security', {}).get('issues', []))}
- **Performance Issues:** {len(results['checks'].get('performance', {}).get('issues', []))}
- **Documentation Issues:** {len(results['checks'].get('documentation', {}).get('issues', []))}

"""

            # Append to the end
            content += audit_section

            with open(version_file, "w", encoding="utf-8") as f:
                f.write(content)

    def _get_overall_status(self, results: Dict[str, Any]) -> str:
        """Get overall status from audit results"""
        statuses = [
            check.get("status", "unknown") for check in results["checks"].values()
        ]

        if all(status == "pass" for status in statuses):
            return "✅ PASS"
        elif any(status == "fail" for status in statuses):
            return "❌ FAIL"
        elif any(status == "warn" for status in statuses):
            return "⚠️ WARN"
        else:
            return "❓ UNKNOWN"


def main():
    generator = AuditReportGenerator()
    generator.generate_comprehensive_report()
    print("📝 Comprehensive audit report generation completed!")


if __name__ == "__main__":
    main()
