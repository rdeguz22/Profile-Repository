from scrubber.share.embed import iframe_embed, image_embed, markdown_embed


def test_iframe_embed_escapes_query_string():
    html = iframe_embed("https://example.com/p/abc?x=1&y=2")
    assert "<iframe" in html
    assert "&amp;" in html


def test_image_embed_with_link():
    html = image_embed("https://example.com/card.png", link_url="https://example.com/p/abc")
    assert html.startswith("<a href=")
    assert "<img" in html


def test_markdown_embed_with_image():
    md = markdown_embed("https://example.com/p/abc", image_url="https://example.com/card.png")
    assert md == "[![Basketball Reference Scrubber view](https://example.com/card.png)](https://example.com/p/abc)"


def test_markdown_embed_without_image():
    md = markdown_embed("https://example.com/p/abc")
    assert md == "[Basketball Reference Scrubber view](https://example.com/p/abc)"
