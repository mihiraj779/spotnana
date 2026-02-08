"""
Connection rules and shared constants for flight search.
Responsibility: SkyPath Flight Connection Search.
"""

# Layover rules (minutes) — per instructions
MIN_LAYOVER_DOMESTIC_MIN = 45
MIN_LAYOVER_INTERNATIONAL_MIN = 90
MAX_LAYOVER_MIN = 6 * 60  # 6 hours

# Search constraints
MAX_STOPS = 2  # max 3 segments
DATE_FORMAT = "%Y-%m-%d"
