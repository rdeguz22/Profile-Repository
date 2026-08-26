"""Player/team name resolution.

Backed by nba_api's bundled static datasets (no network call), so name
resolution works even when the live stats.nba.com endpoints don't.
"""

from __future__ import annotations

import difflib
from functools import lru_cache
from typing import Any

from nba_api.stats.static import players as _players_static
from nba_api.stats.static import teams as _teams_static

from .models import Player, Team


@lru_cache(maxsize=1)
def _all_players_raw() -> list[dict[str, Any]]:
    return _players_static.get_players()


@lru_cache(maxsize=1)
def _all_teams_raw() -> list[dict[str, Any]]:
    return _teams_static.get_teams()


def _to_player(p: dict[str, Any]) -> Player:
    return Player(
        id=p["id"],
        full_name=p["full_name"],
        first_name=p["first_name"],
        last_name=p["last_name"],
        is_active=p["is_active"],
    )


def _to_team(t: dict[str, Any]) -> Team:
    return Team(
        id=t["id"],
        full_name=t["full_name"],
        abbreviation=t["abbreviation"],
        nickname=t["nickname"],
        city=t["city"],
    )


def find_player(name: str) -> Player | None:
    """Resolve free-text to a Player: exact name match, then fuzzy match."""
    name_norm = name.strip().lower()
    if not name_norm:
        return None

    candidates = _all_players_raw()
    for p in candidates:
        if p["full_name"].lower() == name_norm:
            return _to_player(p)

    names = [p["full_name"] for p in candidates]
    close = difflib.get_close_matches(name, names, n=1, cutoff=0.75)
    if close:
        match = next(p for p in candidates if p["full_name"] == close[0])
        return _to_player(match)
    return None


def find_players(name_fragment: str, limit: int = 10) -> list[Player]:
    """Substring search across all players, most useful for autocomplete.

    Results are ranked (not just filtered): a fragment that starts a
    player's first or last name outranks a mid-string match, and active
    players outrank retired ones — otherwise a common surname like "Curry"
    can bury the player most people mean past a small `limit`.
    """
    frag = name_fragment.strip().lower()
    if not frag:
        return []
    matches = [p for p in _all_players_raw() if frag in p["full_name"].lower()]

    def sort_key(p: dict[str, Any]) -> tuple[int, int, str]:
        is_prefix = p["last_name"].lower().startswith(frag) or p["first_name"].lower().startswith(frag)
        return (0 if is_prefix else 1, 0 if p["is_active"] else 1, p["full_name"])

    matches.sort(key=sort_key)
    return [_to_player(p) for p in matches[:limit]]


def find_team(name: str) -> Team | None:
    """Resolve free-text to a Team by full name, abbreviation, or nickname."""
    name_norm = name.strip().lower()
    if not name_norm:
        return None

    for t in _all_teams_raw():
        if name_norm in {t["full_name"].lower(), t["abbreviation"].lower(), t["nickname"].lower()}:
            return _to_team(t)

    names = [t["full_name"] for t in _all_teams_raw()]
    close = difflib.get_close_matches(name, names, n=1, cutoff=0.7)
    if close:
        match = next(t for t in _all_teams_raw() if t["full_name"] == close[0])
        return _to_team(match)
    return None
