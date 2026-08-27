"""Interactive (or scriptable) CLI for the HYROX split predictor."""

from __future__ import annotations

import argparse
import sys

from . import data as D
from .engine import Inputs, Result, fmt, parse_time
from .methodologies import METHODS


def prompt_inputs() -> Inputs:
    print("HYROX Split Predictor — interactive setup")
    print("Press Enter to skip any optional field.\n")

    sex = input("Sex [male/female] (male): ").strip().lower() or "male"
    if sex not in ("male", "female"):
        sex = "male"
    division = input("Division [open/pro] (open): ").strip().lower() or "open"
    if division not in ("open", "pro"):
        division = "open"

    bw_raw = input("Bodyweight kg (optional): ").strip()
    bodyweight = float(bw_raw) if bw_raw else None

    run1 = None
    while run1 is None:
        raw = input("Recent 1km run time, fresh (required, e.g. 4:20): ").strip()
        run1 = parse_time(raw)
        if run1 is None:
            print("  This field is required.")

    weights = D.WEIGHTS[division][sex]
    labels = {
        "ski": "", "sled_push": f"{weights['sled_push']}kg", "sled_pull": f"{weights['sled_pull']}kg",
        "burpee": "", "row": "", "farmers": f"2x{weights['farmers']}kg",
        "lunges": f"{weights['lunges']}kg", "wallballs": f"{weights['wallball']}kg",
    }
    print("\nStation times (optional, at your official load — blank fills from your running-tier benchmark):")
    stations: dict[str, float | None] = {}
    for i, k in enumerate(D.STATION_KEYS):
        tag = f" @ {labels[k]}" if labels[k] else ""
        raw = input(f"  {D.STATION_NAMES[i]} ({D.STATION_DIST[i]}{tag}): ").strip()
        stations[k] = parse_time(raw)

    print("\nOptional physiology (used by the VO2max methodology):")
    vo2_raw = input("  VO2max ml/kg/min (blank = estimate from run pace): ").strip()
    vo2max = float(vo2_raw) if vo2_raw else None
    th_raw = input("  Endurance training hrs/week (optional): ").strip()
    training_hours = float(th_raw) if th_raw else None
    bf_raw = input("  Body fat % (optional): ").strip()
    body_fat = float(bf_raw) if bf_raw else None
    transition_speed = input("  RoxZone pace [fast/average/slow] (average): ").strip().lower() or "average"
    if transition_speed not in ("fast", "average", "slow"):
        transition_speed = "average"

    return Inputs(
        sex=sex, division=division, bodyweight_kg=bodyweight, run1=run1, stations=stations,
        vo2max=vo2max, training_hours=training_hours, body_fat_pct=body_fat,
        transition_speed=transition_speed,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hyrox-predictor",
        description="Enter recent workout times, get a projected HYROX race time computed 10 different ways. "
                     "Run with no arguments for a guided interactive prompt.",
    )
    p.add_argument("--sex", choices=["male", "female"], default="male")
    p.add_argument("--division", choices=["open", "pro"], default="open")
    p.add_argument("--bodyweight", type=float, default=None, help="kg")
    p.add_argument("--run1", type=str, default=None, help="Fresh 1km time, e.g. 4:20")
    p.add_argument("--ski", type=str, default=None)
    p.add_argument("--sled-push", type=str, default=None, dest="sled_push")
    p.add_argument("--sled-pull", type=str, default=None, dest="sled_pull")
    p.add_argument("--burpee", type=str, default=None)
    p.add_argument("--row", type=str, default=None)
    p.add_argument("--farmers", type=str, default=None)
    p.add_argument("--lunges", type=str, default=None)
    p.add_argument("--wallballs", type=str, default=None)
    p.add_argument("--vo2max", type=float, default=None)
    p.add_argument("--training-hours", type=float, default=None, dest="training_hours")
    p.add_argument("--body-fat", type=float, default=None, dest="body_fat")
    p.add_argument("--transition-speed", choices=["fast", "average", "slow"], default="average", dest="transition_speed")
    p.add_argument("--method", choices=[key for key, *_ in METHODS], default=None,
                    help="Also show the full breakdown for one specific methodology")
    return p


def inputs_from_args(args: argparse.Namespace) -> Inputs:
    stations = {
        "ski": parse_time(args.ski),
        "sled_push": parse_time(args.sled_push),
        "sled_pull": parse_time(args.sled_pull),
        "burpee": parse_time(args.burpee),
        "row": parse_time(args.row),
        "farmers": parse_time(args.farmers),
        "lunges": parse_time(args.lunges),
        "wallballs": parse_time(args.wallballs),
    }
    return Inputs(
        sex=args.sex, division=args.division, bodyweight_kg=args.bodyweight,
        run1=parse_time(args.run1), stations=stations, vo2max=args.vo2max,
        training_hours=args.training_hours, body_fat_pct=args.body_fat,
        transition_speed=args.transition_speed,
    )


def race_order_rows(runs: list[float], stations: dict[str, float]) -> list[tuple[str, float, float]]:
    rows = []
    cum = 0.0
    for i in range(8):
        cum += runs[i]
        rows.append((f"Run {i + 1}", runs[i], cum))
        k = D.STATION_KEYS[i]
        cum += stations[k]
        rows.append((D.STATION_NAMES[i], stations[k], cum))
    return rows


def print_breakdown(result: Result) -> None:
    rows = race_order_rows(result.runs, result.stations)
    print(f"{'Segment':<26}{'Split':>10}{'Cumulative':>12}")
    print("-" * 48)
    for label, split, cum in rows:
        print(f"{label:<26}{fmt(split):>10}{fmt(cum):>12}")
    print(f"{'RoxZone (8 transitions)':<26}{fmt(result.roxzone_total):>10}{'':>12}")
    print("-" * 48)
    print(f"{'TOTAL':<26}{fmt(result.total):>10}")


def print_comparison(results: dict[str, Result]) -> None:
    totals = [(name, results[key].total) for key, name, _, _ in METHODS]
    max_t = max(t for _, t in totals)
    name_width = max(len(name) for name, _ in totals) + 2
    for name, t in totals:
        bar_len = int(t / max_t * 36)
        print(f"{name:<{name_width}}{'#' * bar_len:<38}{fmt(t):>10}")
    times = [t for _, t in totals]
    print(f"\nSpread across all 10 methods: {fmt(min(times))} to {fmt(max(times))} ({fmt(max(times) - min(times))} range)")
    print("Narrower spread = higher-confidence prediction.")


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.run1 is not None:
        inp = inputs_from_args(args)
    else:
        inp = prompt_inputs()

    if not inp.run1 or inp.run1 <= 0:
        print("A recent 1km run time is required.", file=sys.stderr)
        return 1

    results = {key: fn(inp) for key, _, fn, _ in METHODS}
    composite = results["m10"]

    print("\n" + "=" * 48)
    print("RECOMMENDED PREDICTION — Weighted Composite")
    print("=" * 48)
    print_breakdown(composite)

    print("\n" + "=" * 48)
    print("ALL 10 METHODOLOGIES")
    print("=" * 48)
    print_comparison(results)

    if args.method:
        name = next(n for k, n, _, _ in METHODS if k == args.method)
        blurb = next(b for k, _, _, b in METHODS if k == args.method)
        result = results[args.method]
        print("\n" + "=" * 48)
        print(name.upper())
        print("=" * 48)
        print(blurb)
        print()
        print_breakdown(result)
        if "p10" in result.extras:
            print(f"\n(p10-p90 range: {fmt(result.extras['p10'])} - {fmt(result.extras['p90'])})")
        if "tier_label" in result.extras:
            print(f"Closest archetype: {result.extras['tier_label']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
