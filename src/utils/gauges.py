"""
🌌 SarlakBot v2.4.0 - Progress Bar Utilities
MERGE-SAFE: Progress visualization utilities
"""

def bar(pct: int, width: int = 10) -> str:
    """
    Create a progress bar with percentage
    Args:
        pct: Percentage (0-100)
        width: Bar width in characters
    Returns:
        Progress bar string with percentage
    """
    pct = max(0, min(100, int(pct)))
    filled = int(round((pct/100)*width))
    return "▮"*filled + "▯"*(width-filled) + f" {pct}%"




