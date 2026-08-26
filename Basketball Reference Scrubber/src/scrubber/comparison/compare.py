from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..data.client import NBAStatsClient

DEFAULT_STATS = [
    "PTS",
    "REB",
    "AST",
    "STL",
    "BLK",
    "FG_PCT",
    "FG3_PCT",
    "FT_PCT",
    "TS_PCT",
    "USG_PCT",
    "PIE",
]


@dataclass
class ComparisonResult:
    players: list[str]
    season: str
    table: pd.DataFrame  # rows = players, columns = stats
    winners: dict[str, str]  # stat -> player with the higher value


class PlayerComparison:
    """Head-to-head player comparison for one season.

    Built on NBAStatsClient.full_player_stats, so `stats` can be any of
    the ~200 merged Base/Advanced/Misc/Scoring/Usage/Defense columns —
    not just the curated DEFAULT_STATS list.
    """

    def __init__(self, client: NBAStatsClient | None = None):
        self.client = client or NBAStatsClient()

    def compare(self, players: list[str], season: str, stats: list[str] | None = None) -> ComparisonResult:
        stats = stats or DEFAULT_STATS
        full = self.client.full_player_stats(season=season)
        rows = []
        for name in players:
            resolved = self.client.resolve_player(name)
            match = full[full["PLAYER_ID"] == resolved.id] if "PLAYER_ID" in full.columns else pd.DataFrame()
            series = match.iloc[0] if not match.empty else pd.Series(dtype=float)
            rows.append({"PLAYER": resolved.full_name, **{s: series.get(s) for s in stats}})

        table = pd.DataFrame(rows).set_index("PLAYER")

        winners: dict[str, str] = {}
        for stat in stats:
            if stat not in table.columns:
                continue
            col = table[stat].dropna()
            if col.empty:
                continue
            winners[stat] = col.idxmax()

        return ComparisonResult(players=players, season=season, table=table, winners=winners)
