"""Basketball Reference Scrubber — foundation data layer for NBA stats tools.

Every other basketball tool in this repo is meant to consume
``scrubber.data.client.NBAStatsClient`` (directly, or via
``scrubber.query.engine.QueryEngine``) rather than talking to the NBA
Stats API on its own.
"""

__version__ = "0.1.0"
