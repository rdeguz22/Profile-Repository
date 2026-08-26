from scrubber.viz.trends import TrendVisualizer


def test_plot_creates_png_file(tmp_path, fake_client):
    viz = TrendVisualizer(client=fake_client)
    out = viz.plot(["LeBron James", "Kevin Durant"], stat="PTS", out_path=tmp_path / "trend.png")
    assert out.exists()
    assert out.stat().st_size > 0


def test_build_dataframe_shape_for_base_stat(fake_client):
    viz = TrendVisualizer(client=fake_client)
    df = viz.build_dataframe(["LeBron James"], stat="PTS")
    assert list(df["PLAYER"].unique()) == ["LeBron James"]
    assert len(df) == 2  # two seasons in the fixture


def test_build_dataframe_sorts_chronologically(fake_client):
    viz = TrendVisualizer(client=fake_client)
    df = viz.build_dataframe(["LeBron James"], stat="PTS")
    assert list(df["SEASON_ID"]) == ["2022-23", "2023-24"]  # fixture is newest-first, output must not be


def test_build_dataframe_falls_back_to_advanced_measure_type(fake_client):
    """TS_PCT only exists in the Advanced career_trend fixture, not Base —
    this proves TrendVisualizer searches across measure types."""
    viz = TrendVisualizer(client=fake_client)
    df = viz.build_dataframe(["LeBron James"], stat="TS_PCT")
    assert len(df) == 2
    namespaces_and_params = [
        call for call in fake_client._recorder.calls if call[0] == "playerdashboardbyyearoveryear"
    ]
    measure_types_tried = [p["measure_type_detailed"] for _, p, _ in namespaces_and_params]
    assert measure_types_tried == ["Base", "Advanced"]  # stopped as soon as it found TS_PCT
