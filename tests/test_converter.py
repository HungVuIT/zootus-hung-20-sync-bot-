"""Unit tests for the HTML -> Markdown converter."""

from __future__ import annotations

import pytest

from kbsync.converter import estimate_chunks, html_to_markdown, render_article


def test_headings_lists_and_links_are_preserved() -> None:
    html = '<h2 id="x"><span style="color:red">Setup</span></h2><ul><li>Go to <a href="/hc/en-us/articles/1-Foo">Foo</a></li></ul>'
    md = html_to_markdown(html)
    assert "## Setup" in md
    assert "- Go to [Foo](/hc/en-us/articles/1-Foo)" in md


def test_code_block_becomes_fenced_without_auto_language() -> None:
    html = '<pre class="wysiwyg-code-block"><code class="language-auto">curl -s https://x/y.sh | bash\n</code></pre>'
    md = html_to_markdown(html)
    assert md.startswith("```\ncurl -s https://x/y.sh | bash\n```")


def test_code_block_keeps_real_language() -> None:
    md = html_to_markdown('<pre><code class="language-json">{"a": 1}</code></pre>')
    assert md.startswith('```json\n{"a": 1}\n```')


def test_single_column_table_becomes_callout_blockquote() -> None:
    html = (
        '<figure class="wysiwyg-table"><table><tbody>'
        "<tr><td><p><strong>IMPORTANT</strong></p></td></tr>"
        "<tr><td>Treat this URL like a password.</td></tr>"
        "</tbody></table></figure>"
    )
    md = html_to_markdown(html)
    assert "> **IMPORTANT**" in md
    assert "> Treat this URL like a password." in md
    assert "|" not in md


def test_real_table_gets_header_row() -> None:
    html = "<table><tbody><tr><td>Country</td><td>Currency</td></tr><tr><td>US</td><td>USD</td></tr></tbody></table>"
    md = html_to_markdown(html)
    assert "| Country | Currency |" in md
    assert "| --- | --- |" in md
    assert "| US | USD |" in md
    assert "|  |  |" not in md


def test_youtube_iframe_becomes_watch_link() -> None:
    md = html_to_markdown('<p><iframe src="//www.youtube-nocookie.com/embed/GyWZd10ure0" width="560"></iframe></p>')
    assert "[Watch the video: https://www.youtube.com/watch?v=GyWZd10ure0](https://www.youtube.com/watch?v=GyWZd10ure0)" in md


def test_in_page_toc_and_nav_are_removed() -> None:
    html = (
        '<ul><li><span><a href="#Step1">Step 1</a></span></li>'
        '<li><a href="https://support.optisigns.com/hc/en-us/articles/undefined#Step2">Step 2</a></li></ul>'
        '<p>Real content <a href="#Step1">see step 1</a>.</p>'
        '<p><a href="#top">Back to top</a></p>'
        "<script>alert(1)</script><nav>menu</nav>"
    )
    md = html_to_markdown(html)
    assert "Step 1\n" not in md.split("Real content")[0]
    assert "Real content [see step 1](#Step1)." in md
    assert "Back to top" not in md
    assert "alert" not in md and "menu" not in md


def test_bold_whitespace_is_hoisted_and_empty_anchors_dropped() -> None:
    html = '<p><a name="anchor"></a><strong>Landscape</strong>,<strong> Portrait </strong>or<strong> Custom</strong></p><h2><br></h2>'
    md = html_to_markdown(html)
    assert md.strip() == "**Landscape**, **Portrait** or **Custom**"


def test_noise_wrappers_and_broken_tags_are_unwrapped() -> None:
    html = '<div class="_3_7DB"><p><font>Authorized as <your name="n"></your><em>me</em></font>&nbsp;now</p></div>'
    md = html_to_markdown(html)
    assert md.strip() == "Authorized as *me* now"


def test_render_article_has_front_matter_and_article_url_line() -> None:
    doc = render_article(
        slug="how-to-use-youtube",
        article_id=42,
        title='Use "YouTube"',
        url="https://support.example.com/hc/en-us/articles/42-Use-YouTube",
        section="Apps",
        category="Integrations",
        updated_at="2026-01-01T00:00:00Z",
        body_html="<p>Hello</p>",
    )
    assert doc.filename == "how-to-use-youtube.md"
    assert doc.content.startswith('---\ntitle: "Use \\"YouTube\\""\narticle_id: 42\n')
    assert "\n# Use \"YouTube\"\n\nArticle URL: https://support.example.com/hc/en-us/articles/42-Use-YouTube\n\nHello\n" in doc.content
    assert len(doc.content_hash) == 64


def test_content_hash_changes_when_body_changes() -> None:
    kwargs = dict(slug="s", article_id=1, title="T", url="u", section="", category="", updated_at="")
    a = render_article(body_html="<p>one</p>", **kwargs)  # type: ignore[arg-type]
    b = render_article(body_html="<p>two</p>", **kwargs)  # type: ignore[arg-type]
    assert a.content_hash != b.content_hash


@pytest.mark.parametrize(
    ("words", "max_tokens", "overlap", "expected"),
    [(10, 400, 60, 1), (400, 400, 60, 1), (401, 400, 60, 2), (1000, 400, 60, 3), (1081, 400, 60, 4)],
)
def test_estimate_chunks(words: int, max_tokens: int, overlap: int, expected: int) -> None:
    assert estimate_chunks("w " * words, max_tokens, overlap) == expected
