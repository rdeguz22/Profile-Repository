# HYROX Split Predictor

A dependency-free Python CLI: enter recent workout times (1km run pace, station times at your division's official load, optional physiology data) and get a projected finish time with a full per-station breakdown — computed **10 different ways**, so you can see where the methods agree and where they diverge.

## Use it

```bash
cd "HYROX Predictor"
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

hyrox-predictor                       # guided interactive prompt
hyrox-predictor --run1 4:20 --sled-push 2:15 --method m7   # scriptable, non-interactive
```

Pure standard library — no third-party runtime dependencies. Run with no arguments for a guided interactive prompt (press Enter to skip any optional field); pass `--run1` to skip straight to non-interactive/scriptable mode. Pass `--method <key>` (m1–m10) to also print the full breakdown for one specific methodology alongside the composite prediction. See `hyrox-predictor --help` for every flag.

Run the test suite:

```bash
pytest -q
```

## Project layout

```
src/hyrox_predictor/
  data.py            # benchmark tiers, official station weights — see "Data sources" below
  engine.py           # shared math: tier-position interpolation, Inputs/Result types, time parsing/formatting
  methodologies.py     # the 10 methodologies, each Inputs -> Result
  cli.py                 # interactive prompt + argparse entrypoint
tests/                    # 33 tests: engine math, all 10 methodologies, CLI
```

`engine.py` and `methodologies.py` have zero I/O — every methodology is a pure function of an `Inputs` dataclass, so the whole prediction engine is testable (and reusable from other Python code) independent of the CLI.

## Why pacing prediction is different for HYROX

A standard endurance-race predictor (e.g. a marathon calculator) only has to model one thing: pace decay over distance. HYROX interleaves **8 × 1km runs with 8 functional stations**, so a predictor has to model two additional effects a pure running calculator never sees:

1. **Compromised running** — your pace on runs 2–8 is never your fresh pace; each run starts from a pre-fatigued state induced by the station before it. A well-paced race rarely produces negative splits on individual runs — the goal is minimizing the fade, not eliminating it. Going out too fast on Run 1 doesn't just cost you that time back later "with interest" on Runs 5–8, it also produces slower station times because you arrive gassed.
2. **RoxZone (transition) time** — the walk/jog between the run finish and the station start, and from the station back onto the course. Across 8 transitions this is routinely 4–7 minutes, or roughly 5.5–7% of total finish time — and it scales with fitness level (elite athletes transition in ~28s per changeover; recreational athletes average ~52s).

This predictor's 10 methodologies exist because there isn't one "correct" way to fold those two effects into a single number — each methodology makes a different, disclosed assumption about which signal (your running, your station strength, your consistency, your body composition) matters most.

## Data sources

All benchmark data was gathered via live research for this project (see conversation history for the actual fetch results); nothing here is official HYROX data, and nothing is invented — every number below traces to one of these sources.

- **Official station format, order, distances, and division weights** (Open + Pro, men + women): [HYROX Stations: Order, Distances, Weights & Rules](https://hyroxfitness.com/training/hyrox-stations-guide/)
- **Target split times by finish-time goal**, built from an analysis of 700,000+ real HYROX race results — this is the core benchmark table the predictor interpolates against: [HYROX Target Split Times by Finish Goal](https://hyroxdatalab.com/articles/hyrox-target-split-times-by-goal)
- **RoxZone/transition time by performance level** (825-athlete Utrecht dataset): [HYROX RoxZone: Average Transition Times](https://hyroxdatalab.com/articles/roxzone-efficiency-analysis)
- **Pacing strategy** (even/negative/positive splits, "your worst run should be Run 5 or 6, not Run 7 or 8"): [HYROX Race-Day Strategy: Pacing, Transitions & Pro Tips](https://roxzone.training/blog/hyrox-race-day-strategy), [HYROX Pacing Strategy: The Complete Guide](https://www.findyouredge.app/news/hyrox-pacing-strategy-guide)
- **Peer-reviewed physiology**: VO2max, endurance training volume, and body fat % as the strongest correlates of finish time; heart rate/lactate patterns across the race: [*Acute physiological responses and performance determinants in Hyrox*](https://pmc.ncbi.nlm.nih.gov/articles/PMC11994925/) (PMC11994925)
- **Existing predictor methodology context** (5K time as strongest single predictor, running = 45–55% of total race time, progressive fatigue factoring): aggregated from public HYROX calculator descriptions (FitnessVolt, Kracey, RoxHype).

### The benchmark table, in brief

| Tier | Goal | Total run | Total stations | RoxZone |
|---|---|---|---|---|
| Elite | 60:00 | 31:45 | 23:30 | 4:30 |
| Advanced | 70:00 | 35:50 | 28:10 | 6:00 |
| Competitive | 80:00 | 39:45 | 33:15 | 7:00 |
| Intermediate | 90:00 | 45:00 | 36:00 | 9:00 |
| Solid | 105:00 | 50:35 | 44:25 | 10:00 |
| Beginner+ | 120:00 | 55:30 | 51:30 | 13:00 |

The predictor interpolates *between* these six tiers (and per-station, per-run splits within each) to produce a continuous prediction rather than snapping to the nearest bucket — see `RUN_SPLITS` / `STATION_SPLITS` / `ROXZONE_TOTAL` in `src/hyrox_predictor/data.py` for the full per-station numbers at every tier.

### Official station loads used for the input form

| Station | Distance | Open Men | Open Women | Pro Men | Pro Women |
|---|---|---|---|---|---|
| SkiErg | 1000m | bodyweight | bodyweight | bodyweight | bodyweight |
| Sled Push | 50m | 152kg | 102kg | 175kg | 125kg |
| Sled Pull | 50m | 103kg | 78kg | 125kg | 100kg |
| Burpee Broad Jumps | 80m | bodyweight | bodyweight | bodyweight | bodyweight |
| Rowing | 1000m | bodyweight | bodyweight | bodyweight | bodyweight |
| Farmers Carry | 200m | 2×24kg | 2×16kg | 2×32kg | 2×24kg |
| Sandbag Lunges | 100m | 20kg | 10kg | 30kg | 20kg |
| Wall Balls | 100 reps | 6kg / 10ft | 4kg / 9ft | 9kg / 10ft | 6kg / 9ft |

## The 10 methodologies

All ten share one building block: a **fractional "tier position"** from 0 (Elite) to 5 (Beginner+), computed by interpolating where an input time falls on the benchmark curve for that segment. What differs between methods is *what determines that position* — running alone, every input averaged, your worst input, a physiology estimate, etc. — and, for a few methods, what happens *after* the position is found.

1. **Station Benchmark Percentile Blend** — Converts every input you provided (run + any stations) to its own tier position and averages them. The most "trust all your data equally" method.
2. **Fresh-Pace Anchored Compromised-Running Model** — Anchors solely on your fresh 1km pace, since published analyses find running is the single strongest predictor of finish time (≈45–55% of total race time). Any station you didn't enter is assumed to match what's typical for that running tier.
3. **Macro Regression via Run-Share-of-Total** — Estimates total run time from your pace, then works backwards: `total = run_time / 0.50`, `station_time = total × 0.44`, `roxzone_time = total × 0.06`. A top-down macro estimate rather than bottom-up interpolation.
4. **Physiological / VO2max Model** — Built on the peer-reviewed finding that VO2max (ρ=-0.71), endurance training volume (ρ=-0.68), and body fat % (ρ=+0.67) are HYROX's strongest performance correlates. Estimates VO2max from run pace if you don't supply one.
5. **Load-to-Bodyweight Strength Model** — HYROX's sled/farmers-carry/sandbag loads are *fixed* regardless of athlete size, so the same load is relatively lighter for a heavier, stronger athlete. Adjusts only the load-bearing stations you didn't directly measure, scaled by `(reference_bodyweight / your_bodyweight) ^ k` per station (k = 0.15–0.35, station-dependent).
6. **RoxZone-Explicit Transition Model** — Most calculators fold RoxZone into a vague buffer. This derives it from your self-rated transition pace (fast/average/slow → 5.5%/6.3%/6.8% of race time) and distributes it unevenly across the 8 transitions, weighted by each station's typical intensity.
7. **Weakest-Link Bottleneck Model** — Real races are gated by your worst station, not your average — you can't bank time from a strong SkiErg to offset getting stuck on the sled. Blends your slowest implied tier position (70% weight) with your average position (30%).
8. **Monte Carlo Race Simulation** — Every other method returns one number; this one runs ~1,500 simulated races with per-segment Gaussian variance (±7–9% on runs/stations, ±18% on RoxZone — tighter if you supplied a real measured time) and reports a p10–p90 range plus the median, acknowledging race-day variability none of the deterministic methods capture.
9. **Nearest-Neighbor Archetype Match** — Instead of interpolating, snaps to whichever single benchmark tier's *whole profile* your inputs most closely resemble (minimum sum of relative squared error across every signal you gave), then reports that tier's real split sheet directly — "athletes who match your profile finish around…"
10. **Weighted Composite (recommended default)** — An ensemble of methods 1, 3, and 7 (40/30/30), so no single methodology's blind spot dominates the headline prediction. This is what's shown at the top of the results.

### Why the methods sometimes disagree a lot

Tested internally with a strong-runner / catastrophic-sled-pull profile: methods anchored on running alone (2, 3, 4, 5, 6, 8) predicted ~1:14–1:16, effectively diluting the one bad station into the average. The weakest-link model (7) and nearest-neighbor match (9) both correctly jumped to ~1:33, reflecting that this athlete's actual race is gated by that one station. **That divergence is a feature, not noise** — a tight spread across all 10 means your inputs paint a consistent picture; a wide spread flags something methodologically interesting about your profile (usually one disproportionately weak or strong station).

## Known limitations

- This is built from **public, aggregated race-result analysis**, not official HYROX timing data — treat outputs as informed estimates, not guarantees.
- The benchmark curve covers roughly 60–120 minute finishers; predictions for outside that range extrapolate from the nearest tier boundary and get less reliable the further out you go.
- Pro-division loads are used for the CLI's station weight labels, but the benchmark split tiers themselves come from Open-division race data (Pro splits weren't available in the sources used) — Pro athletes should treat predictions as directionally useful, not precisely calibrated.
- The VO2max-from-pace estimate (methodology 4) and the load-sensitivity exponents (methodology 5) are disclosed heuristics calibrated against this project's own benchmark tiers, not independently validated formulas.
