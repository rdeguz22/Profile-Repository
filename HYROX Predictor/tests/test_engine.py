from hyrox_predictor.engine import (
    fmt,
    get_column,
    interp_row,
    interp_scalar,
    parse_time,
    position_for_value,
)


def test_get_column():
    table = [[1, 2, 3], [4, 5, 6]]
    assert get_column(table, 1) == [2, 5]


def test_position_for_value_at_boundaries():
    col = [100, 200, 300]
    assert position_for_value(col, 50) == 0
    assert position_for_value(col, 300) == 2
    assert position_for_value(col, 400) == 2


def test_position_for_value_interpolates():
    col = [100, 200, 300]
    assert position_for_value(col, 150) == 0.5
    assert position_for_value(col, 250) == 1.5


def test_interp_row_at_exact_tier():
    table = [[10, 20], [30, 40]]
    assert interp_row(table, 0) == [10, 20]
    assert interp_row(table, 1) == [30, 40]


def test_interp_row_interpolates():
    table = [[10, 20], [30, 40]]
    assert interp_row(table, 0.5) == [20, 30]


def test_interp_scalar():
    assert interp_scalar([100, 200], 0.25) == 125


def test_fmt_under_an_hour():
    assert fmt(125) == "2:05"


def test_fmt_over_an_hour():
    assert fmt(4805) == "1:20:05"


def test_fmt_rounds_and_clamps_negative():
    assert fmt(-5) == "0:00"
    assert fmt(59.6) == "1:00"


def test_parse_time_mmss():
    assert parse_time("4:20") == 260


def test_parse_time_plain_seconds():
    assert parse_time("90") == 90


def test_parse_time_blank_is_none():
    assert parse_time("") is None
    assert parse_time(None) is None
    assert parse_time("   ") is None
