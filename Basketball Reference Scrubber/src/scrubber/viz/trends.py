from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: never try to open a GUI window
import matplotlib.pyplot as plt
import pandas as pd

from ..data.client import NBAStatsClient

PALETTE = ["#38bdf8", "#f97316", "#a3e635", "#f472b6", "#facc15"]
BG_COLOR = "#0f172a"
GRID_COLOR = "#1e293b"
TEXT_COLOR = "#f1f5f9"
MUTED_COLOR = "#94a3b8"


class TrendVisualizer:
    """Plots a stat's trajectory across seasons for one or more players.

    Backed by NBAStatsClient.career_trend, tried across every measure
    type in CAREER_TREND_MEASURE_TYPES until one contains the requested
    stat — so this covers box-score stats (Base) as well as advanced
    metrics (TS_PCT, USG_PCT, ...), not just the traditional stat sheet.
    """

    def __init__(self, client: NBAStatsClient | None = None):
        self.client = client or NBAStatsClient()

    def _career_trend_with_stat(self, player: str, stat: str) -> pd.DataFrame | None:
        for measure_type in self.client.CAREER_TREND_MEASURE_TYPES:
            df = self.client.career_trend(player, measure_type=measure_type)
            if stat in df.columns:
                return df
        return None

    def build_dataframe(self, players: list[str], stat: str) -> pd.DataFrame:
        frames = []
        for name in players:
            career = self._career_trend_with_stat(name, stat)
            if career is None or "GROUP_VALUE" not in career.columns:
                continue
            ordered = career.sort_values("GROUP_VALUE")
            frames.append(pd.DataFrame({"SEASON_ID": ordered["GROUP_VALUE"], stat: ordered[stat], "PLAYER": name}))
        if not frames:
            return pd.DataFrame(columns=["SEASON_ID", stat, "PLAYER"])
        return pd.concat(frames, ignore_index=True)

    def plot(self, players: list[str], stat: str, out_path: str | Path, title: str | None = None) -> Path:
        df = self.build_dataframe(players, stat)
        out_path = Path(out_path)

        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
        fig.patch.set_facecolor(BG_COLOR)
        ax.set_facecolor(BG_COLOR)

        for i, name in enumerate(players):
            sub = df[df["PLAYER"] == name]
            if sub.empty:
                continue
            ax.plot(sub["SEASON_ID"], sub[stat], marker="o", color=PALETTE[i % len(PALETTE)], label=name, linewidth=2)

        ax.set_title(title or f"{stat} by season", color=TEXT_COLOR, fontsize=13, fontweight="bold")
        ax.tick_params(colors=MUTED_COLOR, labelrotation=45)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)
        ax.grid(color=GRID_COLOR, linewidth=0.6)
        if players:
            ax.legend(facecolor=GRID_COLOR, edgecolor="none", labelcolor=TEXT_COLOR)

        fig.tight_layout()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, facecolor=fig.get_facecolor())
        plt.close(fig)
        return out_path
