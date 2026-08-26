"""The foundation: a caching, retrying wrapper over the NBA Stats API.

Every other module in this package (and, per the brief, every other
basketball tool in this repo) is meant to go through NBAStatsClient rather
than calling nba_api or stats.nba.com directly. That keeps caching, retry
behavior, and player/team name resolution in exactly one place.
"""

from __future__ import annotations

import time
from typing import Any

import pandas as pd
from nba_api.stats.endpoints import (
    commonplayerinfo,
    commonteamroster,
    leaguedashplayerstats,
    leaguedashptstats,
    leaguehustlestatsplayer,
    leagueleaders,
    playercareerstats,
    playerdashboardbyyearoveryear,
    playergamelog,
)

from ..cache import DiskCache
from ..config import SETTINGS, Settings
from ..exceptions import NBAApiError, PlayerNotFoundError, TeamNotFoundError
from . import catalog
from .models import Player, Team


class NBAStatsClient:
    # Every league-wide "MeasureType" the Stats API tracks at player
    # granularity. full_player_stats() fetches all of these and merges
    # them into one wide table. ("Four Factors" and "Opponent" exist as
    # MeasureType values too, but the API only tracks them at team
    # granularity — requesting them per-player fails, confirmed live.)
    MEASURE_TYPES = ["Base", "Advanced", "Misc", "Scoring", "Usage", "Defense"]

    # career_trend() (PlayerDashboardByYearOverYear) additionally rejects
    # "Defense" at single-player granularity, confirmed live — its valid
    # set is one narrower than the league-wide MEASURE_TYPES above.
    CAREER_TREND_MEASURE_TYPES = ["Base", "Advanced", "Misc", "Scoring", "Usage"]

    # Every player-tracking ("PtMeasureType") category — movement/touch
    # data the box score doesn't have at all (drives, touches, passing,
    # contested shots, etc).
    PT_MEASURE_TYPES = [
        "Drives",
        "Defense",
        "CatchShoot",
        "Passing",
        "Possessions",
        "PullUpShot",
        "Rebounding",
        "Efficiency",
        "SpeedDistance",
        "ElbowTouch",
        "PostTouch",
        "PaintTouch",
    ]

    def __init__(self, settings: Settings = SETTINGS, cache: DiskCache | None = None):
        self.settings = settings
        self.cache = cache or DiskCache(settings.cache_dir / "nba_stats_cache.sqlite3")

    # ---- identity resolution ------------------------------------------------

    def resolve_player(self, player: str | int) -> Player:
        if isinstance(player, int):
            match = next((p for p in catalog._all_players_raw() if p["id"] == player), None)
            if match is None:
                raise PlayerNotFoundError(f"No player with id {player}")
            return catalog._to_player(match)
        found = catalog.find_player(player)
        if found is None:
            raise PlayerNotFoundError(f"Could not resolve player name: {player!r}")
        return found

    def resolve_team(self, team: str | int) -> Team:
        if isinstance(team, int):
            match = next((t for t in catalog._all_teams_raw() if t["id"] == team), None)
            if match is None:
                raise TeamNotFoundError(f"No team with id {team}")
            return catalog._to_team(match)
        found = catalog.find_team(team)
        if found is None:
            raise TeamNotFoundError(f"Could not resolve team name: {team!r}")
        return found

    # ---- low-level request helper --------------------------------------------

    def _call_endpoint(
        self,
        namespace: str,
        endpoint_cls: Any,
        params: dict[str, Any],
        frame_name: str | None = None,
    ) -> pd.DataFrame:
        """Cache-first call to one nba_api endpoint class, with retries.

        `namespace` identifies the endpoint for cache-key purposes;
        `frame_name` picks which result set to pull out of the endpoint's
        (possibly multi-table) normalized response.
        """
        key = self.cache.make_key(namespace, params)
        cached_value = self.cache.get(key, self.settings.cache_ttl_seconds)
        if cached_value is not None:
            return pd.DataFrame(cached_value)

        last_error: Exception | None = None
        for attempt in range(1, self.settings.max_retries + 1):
            try:
                endpoint = endpoint_cls(timeout=self.settings.request_timeout, **params)
                frames = endpoint.get_normalized_dict()
                data = frames[frame_name] if frame_name else next(iter(frames.values()))
                self.cache.set(key, data)
                return pd.DataFrame(data)
            except Exception as exc:  # nba_api surfaces plain requests/HTTP errors
                last_error = exc
                if attempt < self.settings.max_retries:
                    time.sleep(self.settings.retry_backoff**attempt)
        raise NBAApiError(f"Failed calling {namespace} after {self.settings.max_retries} attempts") from last_error

    # ---- public data methods --------------------------------------------------

    def player_info(self, player: str | int) -> Player:
        p = self.resolve_player(player)
        df = self._call_endpoint(
            "commonplayerinfo",
            commonplayerinfo.CommonPlayerInfo,
            {"player_id": p.id},
            frame_name="CommonPlayerInfo",
        )
        if df.empty:
            return p
        row = df.iloc[0]
        team_id = row.get("TEAM_ID")
        return Player(
            id=p.id,
            full_name=p.full_name,
            first_name=p.first_name,
            last_name=p.last_name,
            is_active=p.is_active,
            team_id=int(team_id) if team_id else None,
            team_abbreviation=row.get("TEAM_ABBREVIATION"),
            position=row.get("POSITION"),
        )

    def career_stats(self, player: str | int, per_mode: str = "PerGame") -> pd.DataFrame:
        """Season-by-season regular-season totals for one player."""
        p = self.resolve_player(player)
        return self._call_endpoint(
            "playercareerstats",
            playercareerstats.PlayerCareerStats,
            {"player_id": p.id, "per_mode36": per_mode},
            frame_name="SeasonTotalsRegularSeason",
        )

    def game_log(self, player: str | int, season: str, season_type: str = "Regular Season") -> pd.DataFrame:
        """Game-by-game log for one player in one season."""
        p = self.resolve_player(player)
        return self._call_endpoint(
            "playergamelog",
            playergamelog.PlayerGameLog,
            {"player_id": p.id, "season": season, "season_type_all_star": season_type},
            frame_name="PlayerGameLog",
        )

    def league_leaders(
        self,
        season: str,
        stat_category: str = "PTS",
        per_mode: str = "PerGame",
        season_type: str = "Regular Season",
    ) -> pd.DataFrame:
        """League-wide ranking for a single stat category."""
        return self._call_endpoint(
            "leagueleaders",
            leagueleaders.LeagueLeaders,
            {
                "season": season,
                "stat_category_abbreviation": stat_category,
                "per_mode48": per_mode,
                "season_type_all_star": season_type,
            },
            frame_name="LeagueLeaders",
        )

    def league_dash_player_stats(
        self,
        season: str,
        per_mode: str = "PerGame",
        measure_type: str = "Base",
        season_type: str = "Regular Season",
    ) -> pd.DataFrame:
        """The full league stat table for one season — the widest, most
        flexible dataset in the client; table builder and comparisons
        both lean on this."""
        return self._call_endpoint(
            "leaguedashplayerstats",
            leaguedashplayerstats.LeagueDashPlayerStats,
            {
                "season": season,
                "per_mode_detailed": per_mode,
                "measure_type_detailed_defense": measure_type,
                "season_type_all_star": season_type,
            },
            frame_name="LeagueDashPlayerStats",
        )

    def full_player_stats(
        self, season: str, per_mode: str = "PerGame", season_type: str = "Regular Season"
    ) -> pd.DataFrame:
        """Every league-wide box-score metric the Stats API tracks for a
        season, in one wide table: Base + Advanced + Misc + Four Factors +
        Scoring + Opponent + Usage + Defense, merged on PLAYER_ID. This is
        the "every statistical metric possible" table — hundreds of
        columns, one row per player.
        """
        combined: pd.DataFrame | None = None
        for measure_type in self.MEASURE_TYPES:
            df = self.league_dash_player_stats(
                season=season, per_mode=per_mode, measure_type=measure_type, season_type=season_type
            )
            if df.empty:
                continue
            if combined is None:
                combined = df
                continue
            new_cols = [c for c in df.columns if c == "PLAYER_ID" or c not in combined.columns]
            combined = combined.merge(df[new_cols], on="PLAYER_ID", how="outer")
        return combined if combined is not None else pd.DataFrame()

    def hustle_stats(
        self, season: str, per_mode: str = "PerGame", season_type: str = "Regular Season"
    ) -> pd.DataFrame:
        """League-wide hustle stats: deflections, screen assists, charges
        drawn, contested shots, loose balls recovered — none of which
        appear anywhere in the box-score measure types above."""
        return self._call_endpoint(
            "leaguehustlestatsplayer",
            leaguehustlestatsplayer.LeagueHustleStatsPlayer,
            {"season": season, "per_mode_time": per_mode, "season_type_all_star": season_type},
            frame_name="HustleStatsPlayer",
        )

    def tracking_stats(
        self,
        season: str,
        pt_measure_type: str = "Drives",
        per_mode: str = "PerGame",
        season_type: str = "Regular Season",
    ) -> pd.DataFrame:
        """League-wide player-tracking data for one category (see
        PT_MEASURE_TYPES) — movement/touch data like drives, touches,
        passing, and contested-shot defense that box scores don't carry
        at all."""
        return self._call_endpoint(
            "leaguedashptstats",
            leaguedashptstats.LeagueDashPtStats,
            {
                "season": season,
                "pt_measure_type": pt_measure_type,
                "per_mode_simple": per_mode,
                "player_or_team": "Player",
                "season_type_all_star": season_type,
            },
            frame_name="LeagueDashPtStats",
        )

    def career_trend(
        self,
        player: str | int,
        measure_type: str = "Base",
        per_mode: str = "PerGame",
        season_type: str = "Regular Season",
    ) -> pd.DataFrame:
        """A single player's entire season-by-season history for any
        measure type in CAREER_TREND_MEASURE_TYPES, in one call — unlike
        career_stats (Base/box-score only), this is what powers trend
        charts for advanced metrics.
        """
        p = self.resolve_player(player)
        return self._call_endpoint(
            "playerdashboardbyyearoveryear",
            playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear,
            {
                "player_id": p.id,
                "measure_type_detailed": measure_type,
                "per_mode_detailed": per_mode,
                "season_type_playoffs": season_type,
            },
            frame_name="ByYearPlayerDashboard",
        )

    def team_roster(self, team: str | int, season: str) -> pd.DataFrame:
        t = self.resolve_team(team)
        return self._call_endpoint(
            "commonteamroster",
            commonteamroster.CommonTeamRoster,
            {"team_id": t.id, "season": season},
            frame_name="CommonTeamRoster",
        )
