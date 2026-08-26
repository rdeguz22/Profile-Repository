from scrubber.query.parser import parse
from scrubber.query.types import Intent


def test_compare_intent():
    q = parse("compare LeBron James vs Kevin Durant career points")
    assert q.intent == Intent.COMPARE
    assert "LeBron James" in q.players
    assert "Kevin Durant" in q.players
    assert "PTS" in q.stats


def test_leaderboard_intent_with_season_and_top_n():
    q = parse("top 10 scorers in 2023-24")
    assert q.intent == Intent.LEADERBOARD
    assert q.top_n == 10
    assert q.season == "2023-24"


def test_trend_intent_extracts_multiword_stat():
    q = parse("trend of Stephen Curry three pointers made")
    assert q.intent == Intent.TREND
    assert "Stephen Curry" in q.players
    assert "FG3M" in q.stats


def test_table_intent():
    q = parse("build a table of the Lakers roster")
    assert q.intent == Intent.TABLE


def test_unknown_intent_for_gibberish():
    q = parse("asdf qwer zxcv")
    assert q.intent == Intent.UNKNOWN


def test_advanced_stat_alias():
    q = parse("compare LeBron James vs Kevin Durant true shooting percentage")
    assert "TS_PCT" in q.stats


def test_compare_extracts_second_player_despite_trailing_stat_phrase():
    """Regression: trailing lowercase words after the second name used to
    break fuzzy player resolution entirely (see query/parser.py)."""
    q = parse("compare Stephen Curry vs Damian Lillard true shooting percentage")
    assert q.players == ["Stephen Curry", "Damian Lillard"]


def test_hustle_stat_alias():
    q = parse("top 10 in deflections")
    assert "DEFLECTIONS" in q.stats


def test_all_metrics_phrase_sets_flag_and_table_intent():
    q = parse("show every stat for the Lakers")
    assert q.all_metrics is True
    assert q.intent == Intent.TABLE


def test_all_metrics_false_by_default():
    q = parse("top 10 scorers")
    assert q.all_metrics is False
