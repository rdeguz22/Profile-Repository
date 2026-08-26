from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Intent(str, Enum):
    COMPARE = "compare"
    LEADERBOARD = "leaderboard"
    TREND = "trend"
    TABLE = "table"
    CAREER = "career"
    UNKNOWN = "unknown"


DEFAULT_SEASON = "2024-25"

# Longest aliases are matched first (see query/parser.py) so multi-word
# phrases like "three pointers made" win over shorter substrings.
STAT_ALIASES: dict[str, str] = {
    "points": "PTS",
    "point": "PTS",
    "pts": "PTS",
    "scoring": "PTS",
    "rebounds": "REB",
    "rebound": "REB",
    "reb": "REB",
    "boards": "REB",
    "assists": "AST",
    "assist": "AST",
    "ast": "AST",
    "dimes": "AST",
    "steals": "STL",
    "steal": "STL",
    "stl": "STL",
    "blocks": "BLK",
    "block": "BLK",
    "blk": "BLK",
    "turnovers": "TOV",
    "turnover": "TOV",
    "tov": "TOV",
    "three pointers made": "FG3M",
    "three pointers": "FG3M",
    "threes": "FG3M",
    "3pm": "FG3M",
    "field goal percentage": "FG_PCT",
    "fg%": "FG_PCT",
    "free throw percentage": "FT_PCT",
    "ft%": "FT_PCT",
    "three point percentage": "FG3_PCT",
    "3p%": "FG3_PCT",
    "minutes": "MIN",
    "min": "MIN",
    "efficiency": "EFF",
    "eff": "EFF",
    "plus minus": "PLUS_MINUS",
    "+/-": "PLUS_MINUS",
    "games played": "GP",
    # Advanced (scrubber.data.client.NBAStatsClient.full_player_stats)
    "true shooting percentage": "TS_PCT",
    "true shooting": "TS_PCT",
    "ts%": "TS_PCT",
    "effective field goal percentage": "EFG_PCT",
    "efg%": "EFG_PCT",
    "usage rate": "USG_PCT",
    "usage percentage": "USG_PCT",
    "usage": "USG_PCT",
    "player impact estimate": "PIE",
    "pie": "PIE",
    "offensive rating": "OFF_RATING",
    "defensive rating": "DEF_RATING",
    "net rating": "NET_RATING",
    "pace": "PACE",
    "assist percentage": "AST_PCT",
    "rebound percentage": "REB_PCT",
    # Hustle (scrubber.data.client.NBAStatsClient.hustle_stats)
    "deflections": "DEFLECTIONS",
    "screen assists": "SCREEN_ASSISTS",
    "charges drawn": "CHARGES_DRAWN",
    "contested shots": "CONTESTED_SHOTS",
    "loose balls recovered": "LOOSE_BALLS_RECOVERED",
    "box outs": "BOX_OUTS",
    # Tracking (scrubber.data.client.NBAStatsClient.tracking_stats)
    "drives": "DRIVES",
    "touches": "TOUCHES",
}

# Phrases that select every metric category at once (see ParsedQuery.all_metrics
# and QueryEngine._run_table / full_player_stats).
ALL_METRICS_MARKERS = ("every stat", "all stats", "every metric", "all metrics", "everything")


@dataclass
class ParsedQuery:
    intent: Intent
    players: list[str] = field(default_factory=list)
    team: str | None = None
    stats: list[str] = field(default_factory=list)
    season: str | None = None
    per_mode: str = "PerGame"
    top_n: int | None = None
    all_metrics: bool = False  # "every stat" / "all metrics" — see ALL_METRICS_MARKERS
    raw_text: str = ""
