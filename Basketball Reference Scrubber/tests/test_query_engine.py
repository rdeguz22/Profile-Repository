import pytest

from scrubber.exceptions import QueryError
from scrubber.query.engine import QueryEngine
from scrubber.query.types import Intent, ParsedQuery


def test_compare_query(fake_client):
    engine = QueryEngine(client=fake_client)
    query = ParsedQuery(intent=Intent.COMPARE, players=["LeBron James", "Kevin Durant"], season="2023-24")
    result = engine.run(query)
    assert set(result.data["PLAYER_NAME"]) == {"LeBron James", "Kevin Durant"}


def test_compare_requires_two_players(fake_client):
    engine = QueryEngine(client=fake_client)
    query = ParsedQuery(intent=Intent.COMPARE, players=["LeBron James"])
    with pytest.raises(QueryError):
        engine.run(query)


def test_leaderboard_query_respects_top_n(fake_client):
    engine = QueryEngine(client=fake_client)
    query = ParsedQuery(intent=Intent.LEADERBOARD, top_n=1, season="2023-24")
    result = engine.run(query)
    assert len(result.data) == 1


def test_unknown_intent_raises(fake_client):
    engine = QueryEngine(client=fake_client)
    query = ParsedQuery(intent=Intent.UNKNOWN, raw_text="asdf")
    with pytest.raises(QueryError):
        engine.run(query)


def test_table_query_with_all_metrics_merges_every_measure_type(fake_client):
    engine = QueryEngine(client=fake_client)
    query = ParsedQuery(intent=Intent.TABLE, season="2023-24", all_metrics=True)
    result = engine.run(query)
    assert result.meta["all_metrics"] is True
    for col in ["PTS", "TS_PCT", "DEF_RATING"]:
        assert col in result.data.columns
