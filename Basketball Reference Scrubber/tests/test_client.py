import pytest

from scrubber.exceptions import PlayerNotFoundError


def test_career_stats_resolves_player_and_calls_correct_namespace(fake_client):
    df = fake_client.career_stats("LeBron James")
    assert not df.empty
    namespace, params, frame_name = fake_client._recorder.calls[-1]
    assert namespace == "playercareerstats"
    assert params["player_id"] == 2544
    assert frame_name == "SeasonTotalsRegularSeason"


def test_league_leaders(fake_client):
    df = fake_client.league_leaders(season="2023-24", stat_category="PTS")
    assert len(df) == 2
    namespace, params, _ = fake_client._recorder.calls[-1]
    assert namespace == "leagueleaders"
    assert params["stat_category_abbreviation"] == "PTS"


def test_league_dash_player_stats(fake_client):
    df = fake_client.league_dash_player_stats(season="2023-24")
    assert set(df["PLAYER_NAME"]) == {"LeBron James", "Kevin Durant"}


def test_unknown_player_raises(fake_client):
    with pytest.raises(PlayerNotFoundError):
        fake_client.career_stats("Zzzzznotarealplayer")


def test_full_player_stats_merges_every_measure_type(fake_client):
    df = fake_client.full_player_stats(season="2023-24")
    # one row per player, columns from every measure type present
    assert len(df) == 2
    for col in ["PTS", "REB", "TS_PCT", "USG_PCT", "PIE", "PTS_PAINT", "PCT_PTS_2PT", "PCT_FGA", "DEF_RATING"]:
        assert col in df.columns
    namespaces = [call[0] for call in fake_client._recorder.calls]
    assert namespaces.count("leaguedashplayerstats") == len(fake_client.MEASURE_TYPES)


def test_full_player_stats_no_duplicate_columns(fake_client):
    df = fake_client.full_player_stats(season="2023-24")
    assert not df.columns.duplicated().any()


def test_hustle_stats(fake_client):
    df = fake_client.hustle_stats(season="2023-24")
    assert "DEFLECTIONS" in df.columns
    namespace, _params, frame_name = fake_client._recorder.calls[-1]
    assert namespace == "leaguehustlestatsplayer"
    assert frame_name == "HustleStatsPlayer"


def test_tracking_stats_forces_player_scope(fake_client):
    df = fake_client.tracking_stats(season="2023-24", pt_measure_type="Drives")
    assert "DRIVES" in df.columns
    _, params, _ = fake_client._recorder.calls[-1]
    assert params["player_or_team"] == "Player"
    assert params["pt_measure_type"] == "Drives"


def test_career_trend_resolves_player_and_calls_correct_namespace(fake_client):
    df = fake_client.career_trend("LeBron James", measure_type="Advanced")
    assert "TS_PCT" in df.columns
    namespace, params, frame_name = fake_client._recorder.calls[-1]
    assert namespace == "playerdashboardbyyearoveryear"
    assert params["player_id"] == 2544
    assert params["measure_type_detailed"] == "Advanced"
    assert frame_name == "ByYearPlayerDashboard"
