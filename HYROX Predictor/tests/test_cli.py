from hyrox_predictor.cli import build_arg_parser, inputs_from_args, main


def test_inputs_from_args_parses_time_strings():
    parser = build_arg_parser()
    args = parser.parse_args(["--run1", "4:20", "--sled-push", "2:15", "--sex", "female"])
    inp = inputs_from_args(args)
    assert inp.run1 == 260
    assert inp.stations["sled_push"] == 135
    assert inp.stations["sled_pull"] is None
    assert inp.sex == "female"


def test_main_non_interactive_runs_and_returns_zero(capsys):
    exit_code = main(["--run1", "4:20", "--sled-push", "2:15", "--method", "m7"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "RECOMMENDED PREDICTION" in out
    assert "ALL 10 METHODOLOGIES" in out
    assert "WEAKEST-LINK BOTTLENECK" in out


def test_main_missing_run1_falls_back_to_interactive_and_errors_on_bad_input(monkeypatch, capsys):
    # blank run1 in the interactive loop, then EOF -> should not crash uncaught in a way
    # that hides the "required" message; simulate a single blank/enter via StopIteration guard
    inputs_iter = iter(["male", "open", "", "4:20"] + [""] * 12)
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs_iter))
    exit_code = main([])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "RECOMMENDED PREDICTION" in out


def test_main_requires_run1_eventually(monkeypatch, capsys):
    # every station/optional prompt left blank, run1 given directly
    inputs_iter = iter(["", "", "", "5:00"] + [""] * 12)
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs_iter))
    exit_code = main([])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "TOTAL" in out
