"""Shared math and types every methodology builds on.

The core idea: every input (a run time, a station time) maps to a
fractional "tier position" in [0, 5] by interpolating where it falls on
the benchmark curve for that segment (0 = Elite, 5 = Beginner+). What
differs between the 10 methodologies in methodologies.py is *what
determines that position* and what happens after it's found.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import data as D


@dataclass
class Inputs:
    sex: str = "male"
    division: str = "open"
    bodyweight_kg: float | None = None
    run1: float = 0.0
    stations: dict[str, float | None] = field(default_factory=lambda: {k: None for k in D.STATION_KEYS})
    vo2max: float | None = None
    training_hours: float | None = None
    body_fat_pct: float | None = None
    transition_speed: str = "average"


@dataclass
class Result:
    runs: list[float]
    stations: dict[str, float]
    roxzone_total: float
    total: float
    extras: dict = field(default_factory=dict)


def get_column(table: list[list[float]], index: int) -> list[float]:
    return [row[index] for row in table]


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def position_for_value(col: list[float], value: float) -> float:
    """Inverse-lookup: where does `value` fall on this ascending 6-point curve?"""
    if value <= col[0]:
        return 0.0
    if value >= col[-1]:
        return float(len(col) - 1)
    for i in range(len(col) - 1):
        if col[i] <= value <= col[i + 1]:
            return i + (value - col[i]) / (col[i + 1] - col[i])
    return float(len(col) - 1)


def interp_row(table: list[list[float]], position: float) -> list[float]:
    lo = int(math.floor(position))
    hi = min(len(table) - 1, math.ceil(position))
    if lo == hi:
        return list(table[lo])
    frac = position - lo
    return [v + (table[hi][i] - v) * frac for i, v in enumerate(table[lo])]


def interp_scalar(arr: list[float], position: float) -> float:
    lo = int(math.floor(position))
    hi = min(len(arr) - 1, math.ceil(position))
    if lo == hi:
        return arr[lo]
    frac = position - lo
    return arr[lo] + (arr[hi] - arr[lo]) * frac


def total_of(runs: list[float], stations: dict[str, float], roxzone_total: float) -> float:
    return sum(runs) + sum(stations.values()) + roxzone_total


def run_anchor_position(inp: Inputs) -> float:
    return position_for_value(get_column(D.RUN_SPLITS, 0), inp.run1)


def build_from_position(position: float, inp: Inputs) -> tuple[list[float], dict[str, float], float, float]:
    """The shared position-anchored predictor: interpolate runs/stations/
    roxzone at a fractional tier position, but always keep the athlete's
    own measured times wherever they gave one."""
    position = clamp(position, 0, 5)
    runs = interp_row(D.RUN_SPLITS, position)
    runs[0] = inp.run1
    bench_stations = interp_row(D.STATION_SPLITS, position)
    stations = {}
    for i, k in enumerate(D.STATION_KEYS):
        provided = inp.stations.get(k)
        stations[k] = provided if provided is not None else bench_stations[i]
    roxzone_total = interp_scalar(D.ROXZONE_TOTAL, position)
    return runs, stations, roxzone_total, position


def fmt(seconds: float) -> str:
    seconds = max(0, round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def parse_time(raw: str | None) -> float | None:
    """Parse 'M:SS', 'MM:SS', or a plain seconds string. Blank -> None."""
    if raw is None:
        return None
    raw = raw.strip()
    if not raw:
        return None
    if ":" in raw:
        minutes, seconds = raw.split(":", 1)
        return float(minutes) * 60 + float(seconds)
    return float(raw)
