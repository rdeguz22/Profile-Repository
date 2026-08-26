# Basketball Reference Scrubber

The foundation data layer for every basketball tool in this repo. It wraps
the (unofficial) NBA Stats API, adds caching/retry, and scrubs every
statistical metric category the API tracks at player granularity — box
score, advanced, hustle, and player-tracking data — behind one shared
client, plus a natural-language query interface, player comparison, a
custom table builder, trend charts, and permalink/embed generation on top.

```
scrubber.data.client.NBAStatsClient   <- the foundation everything else consumes
        │
        ├── scrubber.query      natural-language → structured Query → QueryResult
        ├── scrubber.comparison head-to-head player comparison (any of ~200 metrics)
        ├── scrubber.tables     declarative league-wide table builder
        ├── scrubber.viz        matplotlib trend charts (any measure type, not just box score)
        └── scrubber.share      stateless permalinks + iframe/markdown embed codes
```

Any new basketball tool added to this repo should sit on top of
`NBAStatsClient` (or `QueryEngine`) rather than calling `nba_api` or
`stats.nba.com` directly — that's the whole point of this being "the
foundation."

## Setup

```bash
cd "Basketball Reference Scrubber"
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Try it

```bash
python -m scrubber.cli "compare LeBron James vs Kevin Durant true shooting percentage"
python -m scrubber.cli "top 10 scorers in 2023-24"
python -m scrubber.cli "show every stat for the Lakers"
python examples/demo.py   # tours every module: query, comparison, full metrics table, hustle/tracking, trend, permalink
```

Run the test suite (fully mocked, no network required):

```bash
pytest -q
```

## Modules

### `scrubber.data` — the foundation
- `client.NBAStatsClient` — the whole surface area of the Stats API at
  player granularity:
  - `career_stats` / `game_log` / `league_leaders` — the traditional box
    score.
  - `league_dash_player_stats(measure_type=...)` — one metric category
    (Base/Advanced/Misc/Scoring/Usage/Defense) for the whole league in a
    season.
  - `full_player_stats(season)` — **every** one of those categories,
    merged into a single ~200-column table, one row per player. This is
    the "every statistical metric possible" method.
  - `hustle_stats(season)` — deflections, screen assists, charges drawn,
    contested shots, loose balls recovered — not in any box score.
  - `tracking_stats(season, pt_measure_type=...)` — player-tracking data
    (drives, touches, passing, speed/distance, contested-shot defense,
    catch-and-shoot, pull-up, ...); see `PT_MEASURE_TYPES` for all 12
    categories.
  - `career_trend(player, measure_type=...)` — one player's *entire*
    career, season by season, for any measure type in one call — what
    powers the trend visualizer for advanced metrics.
  - `team_roster` / `player_info`.
  Every call is disk-cached (SQLite, TTL-based) and retried with backoff.
- `catalog` — player/team name resolution (exact + fuzzy match, ranked
  for autocomplete) against `nba_api`'s bundled static dataset, so it
  works even with no network.
- `models` — plain `Player`/`Team` dataclasses used for identity; stats
  themselves are returned as `pandas.DataFrame`s, since that's the natural
  shared format for tables, comparisons, and charts.

### `scrubber.query` — natural language interface
`parse("compare LeBron James vs Kevin Durant true shooting percentage")`
returns a `ParsedQuery` (intent + players + stats + season + `all_metrics`
flag). It's a **rule-based** parser on purpose — deterministic and
dependency-free — recognizing `compare`, `leaderboard` ("top N ..."),
`trend`, `table`, and `career` intents, plus phrases like "every stat" /
"all metrics" that flip on the full merged table. `QueryEngine.run(parsed)`
executes it against `NBAStatsClient` and returns a `QueryResult` (a
DataFrame + metadata) that the other modules can consume directly.

`STAT_ALIASES` covers box-score stats *and* advanced/hustle/tracking
metrics ("true shooting percentage" → `TS_PCT`, "deflections" →
`DEFLECTIONS`, "drives" → `DRIVES`, ...).

The parser is intentionally isolated behind `parse(text) -> ParsedQuery` —
a future version can swap in an LLM-backed parser without touching
`QueryEngine` or anything downstream of it.

### `scrubber.comparison` — player comparison tool
`PlayerComparison.compare(["Stephen Curry", "Damian Lillard"], season="2023-24")`
is built on `full_player_stats`, so `stats` can be any of the ~200 merged
columns, not just a curated list. Returns a `ComparisonResult` with a stat
table (rows = players) and a `winners` dict (stat → player with the higher
value).

### `scrubber.tables` — custom table builder
`TableBuilder.build(TableSpec(season=..., columns=[...], team=..., min_games=...,
sort_by=..., limit=...))` builds an arbitrary league-wide table. Pass
`measure_type=ALL_METRICS` to pull the full merged table instead of one
category, with `to_csv`/`to_html` helpers.

### `scrubber.viz` — trend visualizer
`TrendVisualizer.plot(players, stat="TS_PCT", out_path=...)` renders a
season-by-season line chart (matplotlib, dark theme matching the rest of
this repo's tools) to a PNG file. Backed by `career_trend`, tried across
every measure type until the requested stat is found — so this works for
advanced metrics, not just the traditional box score.

### `scrubber.share` — permalinks and embed codes
- `encode_state`/`decode_state`/`build_permalink` — **stateless** permalinks:
  the URL token *is* the compressed, base64'd query state, so any future
  server can resolve one without a database.
- `PermalinkStore` — an opt-in SQLite-backed short-ID store, for when a
  stateless token is too long to be a nice URL.
- `embed.iframe_embed` / `embed.image_embed` / `embed.markdown_embed` —
  ready-to-paste embed snippets built from a permalink URL (or a chart
  image URL from `scrubber.viz`).

## Design notes / known limitations

- **The NBA Stats API is unofficial** and aggressively blocks non-browser
  traffic on some networks. This foundation is built on
  [`nba_api`](https://github.com/swar/nba_api), the standard open-source
  wrapper, which ships headers known to work; if `NBAApiError` shows up
  after retries, it usually means the current network is being blocked —
  try again from a normal residential connection.
- **"Four Factors" and "Opponent" measure types are team-only.** They
  exist as `MeasureType` values but the API rejects them at player
  granularity (confirmed live) — `NBAStatsClient.MEASURE_TYPES` and
  `full_player_stats` deliberately exclude them. `career_trend` further
  excludes `Defense` (also confirmed live), hence the narrower
  `CAREER_TREND_MEASURE_TYPES`.
- **The NL parser is rule-based, not ML-based.** It covers the query
  shapes this toolkit actually needs and is fully unit-tested and
  dependency-free. It's deliberately isolated behind one function
  (`query.parser.parse`) so it can be swapped for an LLM-backed parser
  later without changing any other module.
- **Permalinks are stateless by default** and don't require a running
  server — `PermalinkStore` is there for when a future web layer wants
  short, pretty URLs instead.
- **Caching** defaults to a project-local `.cache/` directory (gitignored)
  with a 24h TTL, both overridable via `SCRUBBER_CACHE_DIR` /
  `SCRUBBER_CACHE_TTL` env vars. `full_player_stats` makes 6 underlying
  calls (one per measure type); each is cached individually, so repeat
  calls for the same season are fast even if the merge itself re-runs.
