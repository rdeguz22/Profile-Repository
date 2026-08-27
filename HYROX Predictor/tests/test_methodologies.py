import random

import pytest

from hyrox_predictor import data as D
from hyrox_predictor.engine import Inputs
from hyrox_predictor.methodologies import METHODS, method1, method2, method5, method7, method8, method9, method10


def minimal_inputs(run1=260.0):
    return Inputs(sex="male", division="open", run1=run1)


def full_inputs():
    return Inputs(
        sex="male", division="open", bodyweight_kg=82, run1=240,
        stations={
            "ski": 255, "sled_push": 135, "sled_pull": 225, "burpee": 225,
            "row": 255, "farmers": 115, "lunges": 215, "wallballs": 275,
        },
        vo2max=52, training_hours=8, body_fat_pct=12, transition_speed="fast",
    )


def weak_link_inputs():
    return Inputs(
        sex="female", division="open", bodyweight_kg=58, run1=230,
        stations={
            "ski": 260, "sled_push": 130, "sled_pull": 600, "burpee": 220,
            "row": 260, "farmers": 110, "lunges": 210, "wallballs": 270,
        },
    )


@pytest.mark.parametrize("key,name,fn,blurb", METHODS)
def test_every_methodology_runs_and_returns_sane_total(key, name, fn, blurb):
    result = fn(minimal_inputs())
    assert len(result.runs) == 8
    assert set(result.stations) == set(D.STATION_KEYS)
    assert result.roxzone_total > 0
    # a minimal, plausible finish window: nobody predicts a sub-20min or 5hr HYROX
    assert 1800 < result.total < 18000


def test_provided_run1_is_always_kept_exactly():
    inp = minimal_inputs(run1=245)
    for _, _, fn, _ in METHODS:
        result = fn(inp)
        assert result.runs[0] == 245


def test_method1_uses_provided_station_times_directly():
    inp = full_inputs()
    result = method1(inp)
    for k, v in inp.stations.items():
        assert result.stations[k] == v


def test_method5_requires_bodyweight_to_adjust_load_stations():
    inp_no_bw = Inputs(sex="male", division="open", run1=260)
    inp_with_bw = Inputs(sex="male", division="open", run1=260, bodyweight_kg=110)  # much heavier than reference

    without = method5(inp_no_bw)
    with_bw = method5(inp_with_bw)
    baseline = method2(inp_no_bw)

    # no bodyweight given -> falls back to the plain fresh-pace prediction
    assert without.stations["sled_push"] == baseline.stations["sled_push"]
    # heavier-than-reference athlete predicted faster (lower time) on load-bearing stations
    assert with_bw.stations["sled_push"] < baseline.stations["sled_push"]
    # non-load-bearing stations are untouched by bodyweight
    assert with_bw.stations["ski"] == baseline.stations["ski"]


def test_method9_returns_a_valid_tier_label():
    result = method9(minimal_inputs())
    assert result.extras["tier_label"] in D.TIER_LABELS


def test_method8_p10_le_median_le_p90():
    rng = random.Random(42)
    result = method8(full_inputs(), n_sims=500, rng=rng)
    assert result.extras["p10"] <= result.total <= result.extras["p90"]


def test_weakest_link_diverges_upward_on_bad_station():
    """Regression guard for the core behavioral claim of methodology 7:
    a catastrophic single station should push its prediction well above
    the running-anchored baseline, more than the multi-input blend does."""
    inp = weak_link_inputs()
    baseline = method2(inp).total
    blended = method1(inp).total
    bottleneck = method7(inp).total

    assert bottleneck > blended > baseline
    # the bottleneck model should be substantially slower, not marginally
    assert bottleneck - baseline > 600


def test_method10_is_a_weighted_blend_of_1_3_and_7():
    from hyrox_predictor.methodologies import method3

    inp = full_inputs()
    m1, m3, m7 = method1(inp), method3(inp), method7(inp)
    composite = method10(inp)
    expected_total = m1.total * 0.4 + m3.total * 0.3 + m7.total * 0.3
    assert composite.total == pytest.approx(expected_total, rel=1e-6)
