"""Benchmark data — see README.md for full sourcing.

Target split times by finish-time goal are derived from HyroxDataLab's
public analysis of 700,000+ HYROX race results. Official station
weights/distances are from HYROX's published station guide. RoxZone
totals are from a separate 825-athlete transition-time analysis.
"""

from __future__ import annotations

STATION_KEYS = ["ski", "sled_push", "sled_pull", "burpee", "row", "farmers", "lunges", "wallballs"]
STATION_NAMES = ["SkiErg", "Sled Push", "Sled Pull", "Burpee Broad Jumps", "Rowing", "Farmers Carry", "Sandbag Lunges", "Wall Balls"]
STATION_DIST = ["1000m", "50m", "50m", "80m", "1000m", "200m", "100m", "100 reps"]
LOAD_BEARING = {"ski": False, "sled_push": True, "sled_pull": True, "burpee": False, "row": False, "farmers": True, "lunges": True, "wallballs": False}

TIER_LABELS = ["Elite", "Advanced", "Competitive", "Intermediate", "Solid", "Beginner+"]

# seconds, per 1km leg, runs 1-8, one row per tier (fastest tier first)
RUN_SPLITS = [
    [210, 230, 240, 240, 240, 240, 245, 260],
    [230, 260, 270, 270, 275, 275, 280, 295],
    [255, 290, 300, 300, 305, 305, 315, 320],
    [300, 320, 340, 340, 345, 345, 350, 360],
    [315, 365, 380, 380, 390, 390, 400, 420],
    [330, 405, 420, 420, 430, 430, 440, 460],
]

# seconds, columns match STATION_KEYS order, one row per tier
STATION_SPLITS = [
    [240, 100, 170, 180, 240, 90, 170, 220],
    [260, 130, 220, 220, 260, 110, 210, 270],
    [280, 160, 250, 255, 280, 130, 240, 315],
    [300, 190, 290, 300, 300, 150, 280, 360],
    [330, 230, 340, 360, 330, 170, 330, 420],
    [360, 260, 390, 420, 360, 190, 380, 480],
]

# total RoxZone (all 8 transitions), seconds, one per tier
ROXZONE_TOTAL = [270, 360, 420, 540, 600, 780]

# Official station loads (kg). Sled = total load; farmers is per-hand.
WEIGHTS = {
    "open": {
        "male": {"sled_push": 152, "sled_pull": 103, "farmers": 24, "lunges": 20, "wallball": 6},
        "female": {"sled_push": 102, "sled_pull": 78, "farmers": 16, "lunges": 10, "wallball": 4},
    },
    "pro": {
        "male": {"sled_push": 175, "sled_pull": 125, "farmers": 32, "lunges": 30, "wallball": 9},
        "female": {"sled_push": 125, "sled_pull": 100, "farmers": 24, "lunges": 20, "wallball": 6},
    },
}

REFERENCE_BODYWEIGHT = {"male": 85, "female": 65}

# Bodyweight-sensitivity exponents for load-bearing stations (methodology 5)
LOAD_SENSITIVITY = {"sled_push": 0.35, "sled_pull": 0.30, "farmers": 0.15, "lunges": 0.20}
