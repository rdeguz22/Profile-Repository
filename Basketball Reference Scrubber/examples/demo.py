"""End-to-end tour of the foundation: one shared NBAStatsClient feeding
the natural-language interface, player comparison, the "every metric"
table, hustle/tracking stats, the trend visualizer, and permalinks/embeds.

Run from the project root with the venv active:

    python examples/demo.py
"""

from __future__ import annotations

from pathlib import Path

from scrubber.comparison.compare import PlayerComparison
from scrubber.data.client import NBAStatsClient
from scrubber.query.engine import QueryEngine
from scrubber.query.parser import parse
from scrubber.share.embed import iframe_embed, markdown_embed
from scrubber.share.permalink import build_permalink, decode_state, encode_state
from scrubber.tables.builder import ALL_METRICS, TableBuilder, TableSpec
from scrubber.viz.trends import TrendVisualizer

OUTPUT_DIR = Path(__file__).parent / "output"
SEASON = "2023-24"


def main() -> None:
    client = NBAStatsClient()

    # 1. Natural language query interface
    print("=== Natural language query ===")
    parsed = parse("compare Stephen Curry vs Damian Lillard true shooting percentage")
    print(f"  intent={parsed.intent.value} players={parsed.players} stats={parsed.stats}")
    nl_result = QueryEngine(client=client).run(parsed)
    print(nl_result.data[["PLAYER_NAME", "SEASON_ID", "PTS"]].to_string(index=False))

    # 2. Player comparison — now backed by full_player_stats, so any of
    #    ~200 merged Base/Advanced/Misc/Scoring/Usage/Defense columns work.
    print("\n=== Player comparison (every metric available) ===")
    comparison = PlayerComparison(client=client)
    result = comparison.compare(["Stephen Curry", "Damian Lillard"], season=SEASON)
    print(result.table)
    print("Winners:", result.winners)

    # 3. Every statistical metric possible, in one table
    print("\n=== Full metrics table (ALL_METRICS sentinel) ===")
    builder = TableBuilder(client=client)
    full_table = builder.build(TableSpec(season=SEASON, measure_type=ALL_METRICS, min_games=40, limit=5))
    print(f"  {full_table.shape[1]} columns x {full_table.shape[0]} rows (showing 5)")
    print(full_table[["PLAYER_NAME", "PTS", "TS_PCT", "USG_PCT", "PIE"]].to_string(index=False))

    # 4. Hustle stats and player-tracking data — categories the box score
    #    doesn't carry at all.
    print("\n=== Hustle stats ===")
    hustle = client.hustle_stats(season=SEASON)
    print(hustle.sort_values("DEFLECTIONS", ascending=False)[["PLAYER_NAME", "DEFLECTIONS", "SCREEN_ASSISTS", "CHARGES_DRAWN"]].head(5).to_string(index=False))

    print("\n=== Tracking stats (Drives) ===")
    drives = client.tracking_stats(season=SEASON, pt_measure_type="Drives")
    print(drives.sort_values("DRIVES", ascending=False)[["PLAYER_NAME", "DRIVES"]].head(5).to_string(index=False))

    # 5. Trend visualizer — career_trend covers advanced metrics too, not
    #    just the traditional box score.
    print("\n=== Trend visualizer (advanced metric across a career) ===")
    viz = TrendVisualizer(client=client)
    trend_path = viz.plot(
        ["Stephen Curry"], stat="TS_PCT", out_path=OUTPUT_DIR / "curry_ts_pct_trend.png",
        title="Stephen Curry — True Shooting % by season",
    )
    print("Saved:", trend_path)

    # 6. Permalink + embed codes
    print("\n=== Permalink & embed ===")
    state = {"intent": "compare", "players": ["Stephen Curry", "Damian Lillard"], "season": SEASON}
    token = encode_state(state)
    url = build_permalink(state, base_url="https://bbref-scrubber.example.com")
    assert decode_state(token) == state
    print("Permalink:", url)
    print("Iframe embed:", iframe_embed(url))
    print("Markdown embed:", markdown_embed(url, image_url="https://bbref-scrubber.example.com/trend.png"))


if __name__ == "__main__":
    main()
