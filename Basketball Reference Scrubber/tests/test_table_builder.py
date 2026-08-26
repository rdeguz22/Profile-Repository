from scrubber.tables.builder import ALL_METRICS, TableBuilder, TableSpec


def test_build_table_sorted_and_limited(fake_client):
    builder = TableBuilder(client=fake_client)
    spec = TableSpec(season="2023-24", columns=["PTS", "REB"], sort_by="PTS", limit=1)
    df = builder.build(spec)
    assert len(df) == 1
    assert df.iloc[0]["PLAYER_NAME"] == "Kevin Durant"  # higher PTS in fixture


def test_build_table_default_columns_includes_all(fake_client):
    builder = TableBuilder(client=fake_client)
    spec = TableSpec(season="2023-24")
    df = builder.build(spec)
    assert "PLAYER_NAME" in df.columns
    assert "PTS" in df.columns
    assert len(df) == 2


def test_to_html_renders_table(fake_client):
    builder = TableBuilder(client=fake_client)
    df = builder.build(TableSpec(season="2023-24", columns=["PTS"]))
    html = builder.to_html(df)
    assert "<table" in html


def test_all_metrics_sentinel_merges_every_measure_type(fake_client):
    builder = TableBuilder(client=fake_client)
    df = builder.build(TableSpec(season="2023-24", measure_type=ALL_METRICS))
    # Base + Advanced + Misc + Scoring + Usage + Defense all merged in
    for col in ["PTS", "REB", "TS_PCT", "PTS_PAINT", "PCT_FGA", "DEF_RATING"]:
        assert col in df.columns
    assert len(df) == 2
