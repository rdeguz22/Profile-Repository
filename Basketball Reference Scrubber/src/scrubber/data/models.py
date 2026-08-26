from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Player:
    id: int
    full_name: str
    first_name: str
    last_name: str
    is_active: bool
    team_id: int | None = None
    team_abbreviation: str | None = None
    position: str | None = None


@dataclass(frozen=True)
class Team:
    id: int
    full_name: str
    abbreviation: str
    nickname: str
    city: str
