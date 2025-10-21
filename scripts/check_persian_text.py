#!/usr/bin/env python3
"""
Persian Text Validation Script for SarlakBot
--------------------------------------------
✅ Validates Persian text formatting, encoding, and structure in all Python files.
✅ Detects:
   • Non-UTF8 encoding
   • Inappropriate words
   • Mixed Persian/English sequences without proper spacing
   • Wrong punctuation usage (English punctuations in Persian text)
   • Missing or malformed half-space characters (‌)
   • Unreadable Unicode or corrupted Persian text
"""

import re
import sys
from pathlib import Path


class PersianTextValidator:
    """Validator for Persian text in Python files"""

    def __init__(self):
        # Persian & Arabic character ranges (Unicode blocks)
        self.persian_chars = re.compile(
            r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
        )

        # Common profanity & inappropriate terms (expandable)
        self.inappropriate_words = {
            "کص",
            "کیر",
            "جنده",
            "خایه",
            "کونی",
            "لاشی",
            "ننه",
            "بابات",
            "خارکصه",
            "کصکش",
            "حرامزاده",
            "مادرجنده",
            "خایه‌مال",
        }

        # Patterns
        self.mixed_pattern = re.compile(r"[\u0600-\u06FF][a-zA-Z]|[a-zA-Z][\u0600-\u06FF]")
        self.english_punct_pattern = re.compile(r"[\u0600-\u06FF][.,;:!?]")
        self.malformed_halfspace = re.compile(r"[\u200c]{2,}|[^\u200c]\u200c[a-zA-Z0-9]")
        self.unicode_error_pattern = re.compile(r"(\\u[0-9a-fA-F]{4})")

    def validate_file(self, file_path: Path) -> list[tuple[int, str, str]]:
        """Validate Persian text in a file."""
        errors = []

        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append((0, "ENCODING", "File encoding is not UTF-8"))
            return errors

        lines = text.splitlines()

        for i, line in enumerate(lines, 1):
            # Skip comments and docstrings
            if line.strip().startswith(("#", '"""', "'''")):
                continue

            # Persian text presence
            if self.persian_chars.search(line):
                # Profanity check
                for bad_word in self.inappropriate_words:
                    if bad_word in line:
                        errors.append((i, "INAPPROPRIATE", f"Offensive word: {bad_word}"))

                # English punctuation used after Persian letters
                if self.english_punct_pattern.search(line):
                    errors.append((i, "PUNCTUATION", "English punctuation used in Persian text"))

                # Mixed Persian/English text without spacing
                if self.mixed_pattern.search(line):
                    errors.append((i, "MIXED_TEXT", "Mixed Persian/English text without spacing"))

                # Check malformed half-space
                if self.malformed_halfspace.search(line):
                    errors.append((i, "HALFSPACE", "Malformed or missing half-space character"))

                # Detect explicit Unicode sequences (bad encoding)
                if self.unicode_error_pattern.search(line):
                    errors.append((i, "UNICODE", "Possible corrupted Unicode escape sequence"))

        return errors


def print_error_summary(file_path: str, errors: list[tuple[int, str, str]]):
    """Display formatted errors for a file"""
    print(f"\n❌ Persian text validation failed for: {file_path}")
    for line_num, error_type, message in errors:
        print(f"  Line {line_num:<4} | [{error_type}] {message}")
    print(f"  → Total issues in {file_path}: {len(errors)}")


def main():
    """Main entry point for Persian text pre-commit hook."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_persian_text.py <file1> [file2] ...")
        sys.exit(1)

    validator = PersianTextValidator()
    total_errors = 0
    total_files = 0

    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.exists() or not path.suffix == ".py":
            continue

        total_files += 1
        errors = validator.validate_file(path)

        if errors:
            print_error_summary(str(path), errors)
            total_errors += len(errors)
        else:
            print(f"✅ {path} — OK")

    print("\n📊 Summary:")
    print(f"  • Files checked: {total_files}")
    print(f"  • Total issues:  {total_errors}")

    if total_errors > 0:
        print("\n❌ Persian text validation failed.")
        sys.exit(1)
    else:
        print("\n✅ All files passed Persian text validation.")
        sys.exit(0)


if __name__ == "__main__":
    main()
