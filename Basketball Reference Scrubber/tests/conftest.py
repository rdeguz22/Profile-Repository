"""Shared test fixtures.

The live NBA Stats API is not reachable from every environment this repo
runs in (it aggressively blocks non-browser / datacenter traffic), so
these tests fake the one chokepoint every client method calls through —
NBAStatsClient._call_endpoint — with small, realistic fixture DataFrames.
That exercises resolution, caching plumbing, and every downstream module
(comparison, tables, viz, query engine) without needing the network.
"""

from __future__ import annotations

import pandas as pd
import pytest

from scrubber.data.client import NBAStatsClient

LEBRON_ID = 2544
DURANT_ID = 201142

CAREER_BY_PLAYER = {
    LEBRON_ID: pd.DataFrame(
        [
            {
                "SEASON_ID": "2022-23",
                "PLAYER_ID": LEBRON_ID,
                "TEAM_ABBREVIATION": "LAL",
                "GP": 55,
                "PTS": 28.9,
                "REB": 8.3,
                "AST": 6.8,
                "FG_PCT": 0.50,
                "FG3_PCT": 0.32,
                "FT_PCT": 0.70,
                "FG3M": 2.2,
            },
            {
                "SEASON_ID": "2023-24",
                "PLAYER_ID": LEBRON_ID,
                "TEAM_ABBREVIATION": "LAL",
                "GP": 71,
                "PTS": 25.7,
                "REB": 7.3,
                "AST": 8.3,
                "FG_PCT": 0.54,
                "FG3_PCT": 0.41,
                "FT_PCT": 0.75,
                "FG3M": 2.1,
            },
        ]
    ),
    DURANT_ID: pd.DataFrame(
        [
            {
                "SEASON_ID": "2023-24",
                "PLAYER_ID": DURANT_ID,
                "TEAM_ABBREVIATION": "PHX",
                "GP": 75,
                "PTS": 27.1,
                "REB": 6.6,
                "AST": 5.0,
                "FG_PCT": 0.52,
                "FG3_PCT": 0.41,
                "FT_PCT": 0.86,
                "FG3M": 2.0,
            }
        ]
    ),
}

# league_dash_player_stats fixtures, one per MeasureType, so
# full_player_stats' merge-across-measure-types logic is actually
# exercised (Advanced-only columns like TS_PCT must survive the merge).
LEAGUE_DASH_BY_MEASURE_TYPE = {
    "Base": pd.DataFrame(
        [
            {"PLAYER_ID": LEBRON_ID, "PLAYER_NAME": "LeBron James", "TEAM_ABBREVIATION": "LAL", "GP": 71, "PTS": 25.7, "REB": 7.3, "AST": 8.3},
            {"PLAYER_ID": DURANT_ID, "PLAYER_NAME": "Kevin Durant", "TEAM_ABBREVIATION": "PHX", "GP": 75, "PTS": 27.1, "REB": 6.6, "AST": 5.0},
        ]
    ),
    "Advanced": pd.DataFrame(
        [
            {"PLAYER_ID": LEBRON_ID, "TS_PCT": 0.63, "USG_PCT": 0.31, "PIE": 0.18},
            {"PLAYER_ID": DURANT_ID, "TS_PCT": 0.64, "USG_PCT": 0.30, "PIE": 0.17},
        ]
    ),
    "Misc": pd.DataFrame(
        [
            {"PLAYER_ID": LEBRON_ID, "PTS_PAINT": 10.2},
            {"PLAYER_ID": DURANT_ID, "PTS_PAINT": 9.5},
        ]
    ),
    "Scoring": pd.DataFrame(
        [
            {"PLAYER_ID": LEBRON_ID, "PCT_PTS_2PT": 0.70},
            {"PLAYER_ID": DURANT_ID, "PCT_PTS_2PT": 0.65},
        ]
    ),
    "Usage": pd.DataFrame(
        [
            {"PLAYER_ID": LEBRON_ID, "PCT_FGA": 0.25},
            {"PLAYER_ID": DURANT_ID, "PCT_FGA": 0.24},
        ]
    ),
    "Defense": pd.DataFrame(
        [
            {"PLAYER_ID": LEBRON_ID, "DEF_RATING": 110.0},
            {"PLAYER_ID": DURANT_ID, "DEF_RATING": 112.0},
        ]
    ),
}

# career_trend fixtures, one per measure type, rows newest-season-first
# (matching the real API) so tests can verify chronological sorting.
CAREER_TREND_BY_MEASURE_TYPE = {
    "Base": pd.DataFrame(
        [
            {"GROUP_VALUE": "2023-24", "PTS": 25.7, "REB": 7.3},
            {"GROUP_VALUE": "2022-23", "PTS": 28.9, "REB": 8.3},
        ]
    ),
    "Advanced": pd.DataFrame(
        [
            {"GROUP_VALUE": "2023-24", "TS_PCT": 0.63},
            {"GROUP_VALUE": "2022-23", "TS_PCT": 0.58},
        ]
    ),
    "Misc": pd.DataFrame(columns=["GROUP_VALUE"]),
    "Scoring": pd.DataFrame(columns=["GROUP_VALUE"]),
    "Usage": pd.DataFrame(columns=["GROUP_VALUE"]),
}

FIXTURES = {
    "leagueleaders": pd.DataFrame(
        [
            {"RANK": 1, "PLAYER": "Luka Doncic", "TEAM": "DAL", "PTS": 33.9},
            {"RANK": 2, "PLAYER": "Joel Embiid", "TEAM": "PHI", "PTS": 34.7},
        ]
    ),
    "commonteamroster": pd.DataFrame([{"PLAYER": "LeBron James", "PLAYER_ID": LEBRON_ID, "POSITION": "F"}]),
    "commonplayerinfo": pd.DataFrame([{"TEAM_ID": 1610612747, "TEAM_ABBREVIATION": "LAL", "POSITION": "F"}]),
    "playergamelog": pd.DataFrame([{"GAME_DATE": "2024-01-01", "PTS": 30, "REB": 8, "AST": 9}]),
    "leaguehustlestatsplayer": pd.DataFrame(
        [
            {"PLAYER_ID": LEBRON_ID, "PLAYER_NAME": "LeBron James", "DEFLECTIONS": 1.1, "SCREEN_ASSISTS": 0.9},
            {"PLAYER_ID": DURANT_ID, "PLAYER_NAME": "Kevin Durant", "DEFLECTIONS": 0.8, "SCREEN_ASSISTS": 0.4},
        ]
    ),
    "leaguedashptstats": pd.DataFrame(
        [
            {"PLAYER_ID": LEBRON_ID, "PLAYER_NAME": "LeBron James", "DRIVES": 12.4},
            {"PLAYER_ID": DURANT_ID, "PLAYER_NAME": "Kevin Durant", "DRIVES": 8.1},
        ]
    ),
}


class FakeCallRecorder:
    def __init__(self):
        self.calls: list[tuple[str, dict, str | None]] = []

    def __call__(self, namespace, endpoint_cls, params, frame_name=None):
        self.calls.append((namespace, params, frame_name))
        if namespace == "playercareerstats":
            return CAREER_BY_PLAYER.get(params["player_id"], pd.DataFrame()).copy()
        if namespace == "leaguedashplayerstats":
            measure_type = params.get("measure_type_detailed_defense", "Base")
            return LEAGUE_DASH_BY_MEASURE_TYPE.get(measure_type, pd.DataFrame()).copy()
        if namespace == "playerdashboardbyyearoveryear":
            measure_type = params.get("measure_type_detailed", "Base")
            return CAREER_TREND_BY_MEASURE_TYPE.get(measure_type, pd.DataFrame()).copy()
        return FIXTURES.get(namespace, pd.DataFrame()).copy()


@pytest.fixture
def fake_client(monkeypatch):
    client = NBAStatsClient()
    recorder = FakeCallRecorder()
    monkeypatch.setattr(client, "_call_endpoint", recorder)
    client._recorder = recorder  # type: ignore[attr-defined]
    return client
