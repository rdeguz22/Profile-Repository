from scrubber.data import catalog


def test_find_player_exact():
    p = catalog.find_player("LeBron James")
    assert p is not None
    assert p.full_name == "LeBron James"
    assert p.id == 2544


def test_find_player_fuzzy_typo():
    p = catalog.find_player("Lebron Jams")
    assert p is not None
    assert p.full_name == "LeBron James"


def test_find_player_none_for_garbage():
    assert catalog.find_player("Zzzzznotarealplayer") is None


def test_find_players_substring():
    matches = catalog.find_players("Curry", limit=5)
    assert any(p.full_name == "Stephen Curry" for p in matches)


def test_find_team_by_nickname():
    t = catalog.find_team("Lakers")
    assert t is not None
    assert t.abbreviation == "LAL"


def test_find_team_by_abbreviation():
    t = catalog.find_team("BOS")
    assert t is not None
    assert t.full_name == "Boston Celtics"
