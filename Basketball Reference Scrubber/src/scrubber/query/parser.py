"""Rule-based natural-language parsing.

No ML/LLM dependency by design: this is a deterministic, testable v1 that
covers the query shapes the toolkit actually needs (compare / leaderboard /
trend / table / career). ``parse(text) -> ParsedQuery`` is the whole public
surface, so a future version can swap in an LLM-backed parser without
touching any caller — QueryEngine only ever sees a ParsedQuery.
"""

from __future__ import annotations

import re

from ..data import catalog
from .types import ALL_METRICS_MARKERS, STAT_ALIASES, Intent, ParsedQuery

SEASON_RE = re.compile(r"(?:19|20)\d{2}-\d{2}")
TOP_N_RE = re.compile(r"top\s+(\d+)")
NAME_RUN_RE = re.compile(r"(?:[A-Z][a-zA-Z.'-]+\s+){1,2}[A-Z][a-zA-Z.'-]+")
STOPWORDS_RE = re.compile(
    r"\b(compare|table|trend|top \d+|career|of|the|show|build|me|a|for|in)\b", re.IGNORECASE
)

COMPARE_MARKERS = (" vs ", " vs. ", " versus ", "compare ")
TREND_MARKERS = ("trend", "over time", "by season", "progression", "across seasons", "history of")
TABLE_MARKERS = ("table", "roster", "list of", "build a table")
LEADERBOARD_MARKERS = ("top ", "leaders", "leaderboard", "best ")
CAREER_MARKERS = ("career",)


def _detect_intent(lowered: str) -> Intent:
    if any(m in lowered for m in COMPARE_MARKERS):
        return Intent.COMPARE
    if TOP_N_RE.search(lowered) or any(m in lowered for m in LEADERBOARD_MARKERS):
        return Intent.LEADERBOARD
    if any(m in lowered for m in TREND_MARKERS):
        return Intent.TREND
    if any(m in lowered for m in TABLE_MARKERS):
        return Intent.TABLE
    if any(m in lowered for m in CAREER_MARKERS):
        return Intent.CAREER
    # "show every stat for the Lakers" has no other intent marker, but is
    # clearly asking for a table.
    if any(m in lowered for m in ALL_METRICS_MARKERS):
        return Intent.TABLE
    return Intent.UNKNOWN


def _extract_all_metrics(lowered: str) -> bool:
    return any(m in lowered for m in ALL_METRICS_MARKERS)


def _extract_season(text: str) -> str | None:
    match = SEASON_RE.search(text)
    return match.group(0) if match else None


def _extract_top_n(lowered: str) -> int | None:
    match = TOP_N_RE.search(lowered)
    return int(match.group(1)) if match else None


def _extract_stats(lowered: str) -> list[str]:
    found: list[str] = []
    for alias, code in sorted(STAT_ALIASES.items(), key=lambda kv: -len(kv[0])):
        if alias in lowered and code not in found:
            found.append(code)
    return found


def _extract_players(raw_text: str, intent: Intent, max_players: int = 6) -> list[str]:
    """Best-effort player extraction against the static player catalog.

    Compare queries split on comparison/list separators; everything else
    looks for Title-Case name runs (e.g. "Kevin Durant") in the original
    (non-lowercased) text.
    """
    if intent == Intent.COMPARE:
        segments = re.split(r"\s+vs\.?\s+|\s+versus\s+|,\s*| and ", raw_text, flags=re.IGNORECASE)
    else:
        segments = NAME_RUN_RE.findall(raw_text)

    resolved: list[str] = []
    for seg in segments:
        cleaned = STOPWORDS_RE.sub("", seg).strip()
        if not cleaned:
            continue
        # Prefer an embedded Title-Case name run over the whole segment:
        # a compare query like "... vs Damian Lillard true shooting
        # percentage" would otherwise fuzzy-match "Damian Lillard true
        # shooting percentage" as one string and fail to resolve at all.
        name_run = NAME_RUN_RE.search(cleaned)
        candidate = name_run.group(0) if name_run else cleaned
        player = catalog.find_player(candidate)
        if player and player.full_name not in resolved:
            resolved.append(player.full_name)
        if len(resolved) >= max_players:
            break
    return resolved


def parse(text: str) -> ParsedQuery:
    lowered = text.lower()
    intent = _detect_intent(lowered)
    return ParsedQuery(
        intent=intent,
        players=_extract_players(text, intent),
        stats=_extract_stats(lowered),
        season=_extract_season(text),
        top_n=_extract_top_n(lowered),
        all_metrics=_extract_all_metrics(lowered),
        raw_text=text,
    )
