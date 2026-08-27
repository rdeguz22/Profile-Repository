"""The 10 methodologies. Each takes an Inputs and returns a Result.

See README.md for the reasoning and research citation behind each one.
"""

from __future__ import annotations

import random

from . import data as D
from .engine import (
    Inputs,
    Result,
    build_from_position,
    clamp,
    get_column,
    interp_row,
    interp_scalar,
    position_for_value,
    run_anchor_position,
    total_of,
)


def _collect_positions(inp: Inputs) -> list[float]:
    positions = [run_anchor_position(inp)]
    for i, k in enumerate(D.STATION_KEYS):
        value = inp.stations.get(k)
        if value is not None:
            positions.append(position_for_value(get_column(D.STATION_SPLITS, i), value))
    return positions


def method1(inp: Inputs) -> Result:
    """Station Benchmark Percentile Blend — average the tier-position
    implied by EVERY input the athlete provided (run + any stations),
    not just running."""
    positions = _collect_positions(inp)
    pos = sum(positions) / len(positions)
    runs, stations, roxzone_total, _ = build_from_position(pos, inp)
    return Result(runs, stations, roxzone_total, total_of(runs, stations, roxzone_total))


def method2(inp: Inputs) -> Result:
    """Fresh-Pace Anchored Compromised-Running Model — running is the
    single strongest predictor of HYROX finish time, so anchor purely on
    1km pace and apply the population's average fatigue-decay shape."""
    pos = run_anchor_position(inp)
    runs, stations, roxzone_total, _ = build_from_position(pos, inp)
    return Result(runs, stations, roxzone_total, total_of(runs, stations, roxzone_total))


def method3(inp: Inputs) -> Result:
    """Macro Regression via Run-Share-of-Total — running is ~45-55% of a
    HYROX finish; back out station + RoxZone time from that ratio instead
    of interpolating them directly."""
    pos = run_anchor_position(inp)
    runs = interp_row(D.RUN_SPLITS, pos)
    runs[0] = inp.run1
    run_total = sum(runs)

    run_share, rox_share = 0.50, 0.06
    station_share = 1 - run_share - rox_share
    predicted_total = run_total / run_share
    station_target = predicted_total * station_share
    roxzone_total = predicted_total * rox_share

    bench_shape = interp_row(D.STATION_SPLITS, pos)
    stations: dict[str, float] = {}
    sum_provided = 0.0
    for i, k in enumerate(D.STATION_KEYS):
        value = inp.stations.get(k)
        if value is not None:
            stations[k] = value
            sum_provided += value
    remaining = max(0.0, station_target - sum_provided)
    unprovided_idx = [i for i, k in enumerate(D.STATION_KEYS) if inp.stations.get(k) is None]
    shape_sum = sum(bench_shape[i] for i in unprovided_idx) or 1.0
    for i in unprovided_idx:
        stations[D.STATION_KEYS[i]] = remaining * (bench_shape[i] / shape_sum)

    return Result(runs, stations, roxzone_total, total_of(runs, stations, roxzone_total))


def method4(inp: Inputs) -> Result:
    """Physiological / VO2max Model — grounded in the peer-reviewed
    finding that VO2max (rho=-0.71), endurance training volume
    (rho=-0.68), and body fat % (rho=+0.67) are the strongest correlates
    of HYROX finish time (PMC11994925)."""
    vo2 = inp.vo2max
    if vo2 is None:
        vo2 = clamp(60 - (inp.run1 - 210) * 25 / 120, 25, 70)
    pos = clamp((60 - vo2) * 5 / 25, 0, 5)
    if inp.training_hours is not None:
        pos += clamp(-(inp.training_hours - 6) * 0.05, -1, 1)
    if inp.body_fat_pct is not None:
        pos += clamp((inp.body_fat_pct - 15) * 0.04, -0.6, 1.2)
    pos = clamp(pos, 0, 5)
    runs, stations, roxzone_total, _ = build_from_position(pos, inp)
    return Result(runs, stations, roxzone_total, total_of(runs, stations, roxzone_total), {"vo2_used": vo2})


def method5(inp: Inputs) -> Result:
    """Load-to-Bodyweight Strength Model — HYROX loads (sled, farmers
    carry, sandbag) are fixed regardless of the athlete's size, so the
    same load is relatively lighter for a heavier/stronger athlete.
    Adjusts only the load-bearing stations the athlete didn't directly
    measure."""
    pos = run_anchor_position(inp)
    runs, stations, roxzone_total, _ = build_from_position(pos, inp)
    if inp.bodyweight_kg:
        ref_bw = D.REFERENCE_BODYWEIGHT[inp.sex]
        rel_factor = ref_bw / inp.bodyweight_kg
        for k, exponent in D.LOAD_SENSITIVITY.items():
            if inp.stations.get(k) is None:
                stations[k] = stations[k] * (rel_factor**exponent)
    return Result(runs, stations, roxzone_total, total_of(runs, stations, roxzone_total))


def method6(inp: Inputs) -> Result:
    """Explicit RoxZone / Transition Model — treats RoxZone as its own
    variable driven by a transition-pace rating, distributed unevenly
    across the 8 transitions (heavier stations => longer recovery before
    the next run)."""
    pos = run_anchor_position(inp)
    runs, stations, _roxzone_total, _ = build_from_position(pos, inp)
    pct_map = {"fast": 0.055, "average": 0.063, "slow": 0.068}
    pct = pct_map.get(inp.transition_speed, 0.063)
    non_rox = sum(runs) + sum(stations.values())
    roxzone_total = pct * non_rox / (1 - pct)
    shape = interp_row(D.STATION_SPLITS, pos)
    shape_sum = sum(shape)
    transitions = [roxzone_total * v / shape_sum for v in shape]
    return Result(runs, stations, roxzone_total, total_of(runs, stations, roxzone_total), {"transitions": transitions})


def method7(inp: Inputs) -> Result:
    """Weakest-Link Bottleneck Model — real races are gated by your worst
    station, not your average fitness. Blends the slowest implied tier
    position (70%) with the average (30%) instead of averaging outright."""
    positions = _collect_positions(inp)
    blend = clamp(0.7 * max(positions) + 0.3 * (sum(positions) / len(positions)), 0, 5)
    runs, stations, roxzone_total, _ = build_from_position(blend, inp)
    return Result(runs, stations, roxzone_total, total_of(runs, stations, roxzone_total))


def method8(inp: Inputs, n_sims: int = 1500, rng: random.Random | None = None) -> Result:
    """Monte Carlo Race Simulation — every other methodology gives one
    number; this one acknowledges race-day variance (nerves, sled
    friction, queuing at stations) and simulates races to report a
    realistic p10-p50-p90 range instead of a false-precision point
    estimate."""
    rng = rng or random.Random()
    pos = run_anchor_position(inp)
    mean_runs, mean_stations, mean_roxzone, _ = build_from_position(pos, inp)

    totals = []
    for _ in range(n_sims):
        t = 0.0
        for v in mean_runs:
            t += max(0.0, rng.gauss(v, v * 0.07))
        for k, v in mean_stations.items():
            sd_pct = 0.04 if inp.stations.get(k) is not None else 0.09
            t += max(0.0, rng.gauss(v, v * sd_pct))
        t += max(0.0, rng.gauss(mean_roxzone, mean_roxzone * 0.18))
        totals.append(t)
    totals.sort()
    p10 = totals[int(0.10 * n_sims)]
    p50 = totals[int(0.50 * n_sims)]
    p90 = totals[int(0.90 * n_sims)]
    return Result(mean_runs, mean_stations, mean_roxzone, p50, {"p10": p10, "p90": p90})


def method9(inp: Inputs) -> Result:
    """Nearest-Neighbor Archetype Match — instead of continuous
    interpolation, snap to whichever single tier's full benchmark profile
    the athlete's inputs most closely resemble (smallest relative squared
    error across every provided signal), then report that tier directly."""
    best_tier, best_score = 0, float("inf")
    for t in range(len(D.RUN_SPLITS)):
        score = ((inp.run1 - D.RUN_SPLITS[t][0]) / D.RUN_SPLITS[t][0]) ** 2
        for i, k in enumerate(D.STATION_KEYS):
            value = inp.stations.get(k)
            if value is not None:
                score += ((value - D.STATION_SPLITS[t][i]) / D.STATION_SPLITS[t][i]) ** 2
        if score < best_score:
            best_score, best_tier = score, t

    runs = list(D.RUN_SPLITS[best_tier])
    runs[0] = inp.run1
    stations = {}
    for i, k in enumerate(D.STATION_KEYS):
        value = inp.stations.get(k)
        stations[k] = value if value is not None else D.STATION_SPLITS[best_tier][i]
    roxzone_total = D.ROXZONE_TOTAL[best_tier]
    return Result(runs, stations, roxzone_total, total_of(runs, stations, roxzone_total), {"tier_label": D.TIER_LABELS[best_tier]})


def method10(inp: Inputs) -> Result:
    """Weighted Composite (recommended) — ensembles methods 1, 3, and 7
    (multi-input blend / macro run-share regression / weakest-link) so no
    single methodology's blind spot dominates the headline number."""
    m1, m3, m7 = method1(inp), method3(inp), method7(inp)
    w1, w3, w7 = 0.4, 0.3, 0.3
    runs = [m1.runs[i] * w1 + m3.runs[i] * w3 + m7.runs[i] * w7 for i in range(8)]
    stations = {k: m1.stations[k] * w1 + m3.stations[k] * w3 + m7.stations[k] * w7 for k in D.STATION_KEYS}
    roxzone_total = m1.roxzone_total * w1 + m3.roxzone_total * w3 + m7.roxzone_total * w7
    return Result(runs, stations, roxzone_total, total_of(runs, stations, roxzone_total))


METHODS: list[tuple[str, str, callable, str]] = [
    ("m1", "Station Benchmark Blend", method1,
     "Every input you gave — the run and any stations — is converted to a percentile tier and averaged."),
    ("m2", "Fresh-Pace Anchor", method2,
     "Anchored purely on your fresh 1km pace, since running is the strongest single predictor of finish time (~45-55% of total race time)."),
    ("m3", "Run-Share Regression", method3,
     "Backs out station and RoxZone time from running's known ~50% share of a HYROX finish, rather than interpolating them directly."),
    ("m4", "Physiological (VO2max)", method4,
     "Grounded in a peer-reviewed study: VO2max, endurance training volume, and body fat % as the strongest correlates of finish time."),
    ("m5", "Load-to-Bodyweight", method5,
     "HYROX loads are fixed regardless of your size — adjusts load-bearing stations you didn't measure using your bodyweight."),
    ("m6", "RoxZone Explicit", method6,
     "Models transition time from your self-rated pace, split unevenly across the 8 transitions by station intensity."),
    ("m7", "Weakest-Link Bottleneck", method7,
     "Weights your slowest implied tier position 70%, average 30% — races are gated by your worst station, not your average."),
    ("m8", "Monte Carlo Simulation", method8,
     "Simulates ~1,500 races with realistic segment-to-segment variance; reports a p10-p90 range instead of one number."),
    ("m9", "Nearest-Neighbor Archetype", method9,
     "Snaps to whichever single benchmark tier's whole profile most closely resembles your inputs, then reports that tier's real splits."),
    ("m10", "Weighted Composite", method10,
     "Recommended default: an ensemble of methods 1, 3, and 7 (40/30/30), so no single blind spot dominates."),
]
