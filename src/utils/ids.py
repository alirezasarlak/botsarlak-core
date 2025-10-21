"""
🌌 SarlakBot v2.4.0 - Public Profile ID Utilities
MERGE-SAFE: Public profile ID encoding/decoding
"""

import string
from typing import Optional

_ALPHABET = string.digits + string.ascii_uppercase  # base36

def _to_base36(n: int) -> str:
    """Convert integer to base36 string"""
    if n == 0: 
        return "0"
    s = []
    while n > 0:
        n, r = divmod(n, 36)
        s.append(_ALPHABET[r])
    return "".join(reversed(s))

def _checksum(n: int) -> str:
    """Generate checksum for user ID"""
    return _to_base36((n * 97) % 1296).zfill(2)  # 2 chars

def encode_user_id(tg_id: int) -> str:
    """
    Encode Telegram user ID to public profile ID
    Format: SB-{base36}-{chk}
    """
    b36 = _to_base36(tg_id)
    return f"SB-{b36}-{_checksum(tg_id)}"

def decode_public_id(pid: str) -> Optional[int]:
    """
    Decode public profile ID to Telegram user ID
    Expects format: SB-{base36}-{chk}
    Returns None if invalid
    """
    try:
        _, b36, chk = pid.split("-")
        n = int(b36, 36)
        return n if _checksum(n) == chk else None
    except Exception:
        return None




