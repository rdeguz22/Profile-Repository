from scrubber.comparison.compare import PlayerComparison


def test_compare_two_players_picks_correct_winners(fake_client):
    comparison = PlayerComparison(client=fake_client)
    result = comparison.compare(
        ["LeBron James", "Kevin Durant"], season="2023-24", stats=["PTS", "REB", "TS_PCT"]
    )
    assert result.winners["PTS"] == "Kevin Durant"  # 27.1 > 25.7 (Base)
    assert result.winners["REB"] == "LeBron James"  # 7.3 > 6.6 (Base)
    assert result.winners["TS_PCT"] == "Kevin Durant"  # 0.64 > 0.63 (Advanced)
    assert list(result.table.index) == ["LeBron James", "Kevin Durant"]


def test_compare_calls_full_player_stats_once_per_measure_type(fake_client):
    comparison = PlayerComparison(client=fake_client)
    comparison.compare(["LeBron James", "Kevin Durant"], season="2023-24")
    namespaces = [call[0] for call in fake_client._recorder.calls]
    # full_player_stats fans out across every player-level measure type
    assert namespaces.count("leaguedashplayerstats") == len(fake_client.MEASURE_TYPES)
