from server import _normalize


def test_normalize_curly_apostrophes():
    assert _normalize("Mom’s Soup") == _normalize("Mom's Soup")
    assert _normalize("‘quoted’") == _normalize("'quoted'")


def test_normalize_lowercases():
    assert _normalize("Chicken Soup") == "chicken soup"
