from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from ..data.client import NBAStatsClient

# Sentinel measure_type: pull every metric category (Base + Advanced +
# Misc + Scoring + Usage + Defense) merged into one table, instead of
# just one.
ALL_METRICS = "All"


@dataclass
class TableSpec:
    season: str
    columns: list[str] = field(default_factory=list)
    per_mode: str = "PerGame"
    measure_type: str = "Base"  # or ALL_METRICS for every category merged
    team: str | None = None
    min_games: int | None = None
    sort_by: str | None = None
    ascending: bool = False
    limit: int | None = None


class TableBuilder:
    """Builds an arbitrary league-wide stat table from a declarative TableSpec.

    A thin layer over NBAStatsClient.league_dash_player_stats (or, when
    `measure_type=ALL_METRICS`, over full_player_stats): pick a season,
    pick columns, filter by team/games played, sort, cap rows.
    """

    BASE_COLUMNS = ["PLAYER_NAME", "TEAM_ABBREVIATION"]

    def __init__(self, client: NBAStatsClient | None = None):
        self.client = client or NBAStatsClient()

    def build(self, spec: TableSpec) -> pd.DataFrame:
        if spec.measure_type == ALL_METRICS:
            df = self.client.full_player_stats(season=spec.season, per_mode=spec.per_mode)
        else:
            df = self.client.league_dash_player_stats(
                season=spec.season, per_mode=spec.per_mode, measure_type=spec.measure_type
            )

        if spec.team:
            team = self.client.resolve_team(spec.team)
            df = df[df["TEAM_ABBREVIATION"] == team.abbreviation]

        if spec.min_games is not None and "GP" in df.columns:
            df = df[df["GP"] >= spec.min_games]

        columns = spec.columns or [c for c in df.columns if c not in self.BASE_COLUMNS]
        keep = list(dict.fromkeys(c for c in self.BASE_COLUMNS + columns if c in df.columns))
        df = df[keep]

        if spec.sort_by and spec.sort_by in df.columns:
            df = df.sort_values(spec.sort_by, ascending=spec.ascending)

        if spec.limit:
            df = df.head(spec.limit)

        return df.reset_index(drop=True)

    def to_csv(self, df: pd.DataFrame, path: str) -> None:
        df.to_csv(path, index=False)

    def to_html(self, df: pd.DataFrame) -> str:
        return df.to_html(index=False, classes="scrubber-table", border=0)
