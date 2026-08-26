"""Executes a ParsedQuery against the data layer.

This is the seam between the natural-language interface and the rest of
the toolkit: comparisons, the table builder, and the trend visualizer can
each be driven directly, or by handing them a QueryResult produced here
from a plain-English question.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from ..data.client import NBAStatsClient
from ..exceptions import QueryError
from .types import DEFAULT_SEASON, Intent, ParsedQuery


@dataclass
class QueryResult:
    intent: Intent
    data: pd.DataFrame
    meta: dict[str, Any]


class QueryEngine:
    def __init__(self, client: NBAStatsClient | None = None):
        self.client = client or NBAStatsClient()

    def run(self, query: ParsedQuery) -> QueryResult:
        season = query.season or DEFAULT_SEASON
        handlers = {
            Intent.COMPARE: self._run_compare,
            Intent.LEADERBOARD: self._run_leaderboard,
            Intent.TREND: self._run_trend,
            Intent.TABLE: self._run_table,
            Intent.CAREER: self._run_career,
        }
        handler = handlers.get(query.intent)
        if handler is None:
            raise QueryError(f"Could not determine intent for: {query.raw_text!r}")
        return handler(query, season)

    def _run_compare(self, query: ParsedQuery, season: str) -> QueryResult:
        if len(query.players) < 2:
            raise QueryError("A comparison needs at least two players")
        rows = []
        for name in query.players:
            career = self.client.career_stats(name)
            row = career[career["SEASON_ID"] == season] if "SEASON_ID" in career.columns else pd.DataFrame()
            if row.empty and not career.empty:
                row = career.tail(1)
            rows.append(row.assign(PLAYER_NAME=name))
        combined = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
        return QueryResult(intent=query.intent, data=combined, meta={"season": season, "players": query.players})

    def _run_leaderboard(self, query: ParsedQuery, season: str) -> QueryResult:
        stat = query.stats[0] if query.stats else "PTS"
        df = self.client.league_leaders(season=season, stat_category=stat)
        top_n = query.top_n or 10
        return QueryResult(intent=query.intent, data=df.head(top_n), meta={"season": season, "stat": stat, "top_n": top_n})

    def _run_trend(self, query: ParsedQuery, season: str) -> QueryResult:
        if not query.players:
            raise QueryError("A trend needs at least one player")
        name = query.players[0]
        df = self.client.career_stats(name)
        return QueryResult(intent=query.intent, data=df, meta={"player": name, "stats": query.stats})

    def _run_table(self, query: ParsedQuery, season: str) -> QueryResult:
        if query.all_metrics:
            # "every stat" / "all metrics" — the full merged Base +
            # Advanced + Misc + Scoring + Usage + Defense table, columns
            # untouched, since the whole point is not to narrow it down.
            df = self.client.full_player_stats(season=season)
            return QueryResult(intent=query.intent, data=df, meta={"season": season, "all_metrics": True})

        df = self.client.league_dash_player_stats(season=season)
        if query.stats:
            keep = ["PLAYER_ID", "PLAYER_NAME", "TEAM_ABBREVIATION"] + [s for s in query.stats if s in df.columns]
            keep = list(dict.fromkeys(c for c in keep if c in df.columns))
            df = df[keep]
        return QueryResult(intent=query.intent, data=df, meta={"season": season})

    def _run_career(self, query: ParsedQuery, season: str) -> QueryResult:
        if not query.players:
            raise QueryError("A career lookup needs a player name")
        name = query.players[0]
        df = self.client.career_stats(name)
        return QueryResult(intent=query.intent, data=df, meta={"player": name})
