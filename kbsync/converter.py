"""Turn messy Help Center HTML into clean, RAG-friendly Markdown."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import MarkdownConverter

# Tags whose *content* we keep. Anything else (span, div, font, Wix classes, broken tags) is unwrapped.
_KEEP_TAGS = {
    "p", "br", "hr", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "a", "img", "strong", "b", "em", "i", "code", "pre",
    "table", "thead", "tbody", "tr", "td", "th", "blockquote", "s", "del", "sup", "sub",
}
# Tags removed together with their content: page chrome, scripts, ads.
_DROP_TAGS = {"script", "style", "noscript", "nav", "header", "footer", "form", "button", "input", "svg", "aside"}
_YOUTUBE_RE = re.compile(r"(?:youtube(?:-nocookie)?\.com/embed/|youtu\.be/)([\w-]{6,})")
_BACK_TO_TOP_RE = re.compile(r"^\s*(back|return)\s+to\s+(the\s+)?top\s*$", re.I)
_HEADINGS = ["h1", "h2", "h3", "h4", "h5", "h6"]


@dataclass(frozen=True)
class MarkdownDoc:
    """Rendered Markdown for one article plus the hash used for change detection."""

    slug: str
    filename: str
    content: str
    content_hash: str


class _Converter(MarkdownConverter):
    """markdownify with fenced code blocks and no over-escaping."""

    def convert_pre(self, el: Tag, text: str, parent_tags: set[str]) -> str:  # type: ignore[override]
        code = el.find("code")
        lang = ""
        classes = (code.get("class") if isinstance(code, Tag) else None) or []
        for cls in classes:
            if cls.startswith("language-") and cls != "language-auto":
                lang = cls.removeprefix("language-")
        body = el.get_text().strip("\n")
        return f"\n\n```{lang}\n{body}\n```\n\n"


def _make_converter() -> _Converter:
    return _Converter(
        heading_style="ATX",
        bullets="-",
        strong_em_symbol="*",
        escape_asterisks=False,
        escape_underscores=False,
        escape_misc=False,
        wrap=False,
        newline_style="spaces",
    )


def _normalize_href(href: str) -> str:
    """Zendesk sometimes emits '/articles/undefined#anchor' for in-page links; make them plain anchors."""
    if "/articles/undefined#" in href:
        return "#" + href.split("#", 1)[1]
    return href


def _is_anchor_only_link(tag: Tag) -> bool:
    return tag.name == "a" and str(tag.get("href", "")).startswith("#")


def _own_text(li: Tag) -> str:
    """Text of a list item excluding any nested lists."""
    return "".join(
        c.get_text() if isinstance(c, Tag) else str(c)
        for c in li.children
        if not (isinstance(c, Tag) and c.name in ("ul", "ol"))
    )


def _is_toc_list(ul: Tag) -> bool:
    """Detect an in-page table of contents.

    Rule: at least two items, every link inside is a '#anchor' link, each linked item starts with
    its link text (annotations after it are allowed), and at least 75% of the items carry a link
    (Zendesk TOCs occasionally contain a plain-text item such as 'FAQs').
    """
    items = ul.find_all("li", recursive=True)
    if len(items) < 2:
        return False
    linked = 0
    for li in items:
        links = [a for a in li.find_all("a") if a.find_parent(["ul", "ol"]) is li.find_parent(["ul", "ol"])]
        if not links:
            continue
        if not all(_is_anchor_only_link(a) for a in links):
            return False
        if not _own_text(li).strip().startswith(links[0].get_text().strip()):
            return False
        linked += 1
    return linked / len(items) >= 0.75


def _hoist_whitespace(tag: Tag) -> None:
    strings = list(tag.strings)
    if not strings:
        return
    first, last = strings[0], strings[-1]
    lead = len(first) - len(first.lstrip())
    if lead:
        tag.insert_before(NavigableString(first[:lead]))
        first.replace_with(NavigableString(first[lead:]))
    strings = list(tag.strings)
    if not strings:
        return
    last = strings[-1]
    trail = len(last) - len(last.rstrip())
    if trail:
        tag.insert_after(NavigableString(last[len(last) - trail :]))
        last.replace_with(NavigableString(last[: len(last) - trail]))


def _callout_rows(table: Tag) -> list[Tag] | None:
    """Zendesk 'IMPORTANT'/'NOTE' boxes are 1-column tables; return their rows if so."""
    rows = table.find_all("tr")
    if not rows or len(rows) > 4:
        return None
    for tr in rows:
        if len(tr.find_all(["td", "th"], recursive=False)) != 1:
            return None
    return rows


def _preprocess(soup: BeautifulSoup) -> None:
    for tag in soup.find_all(list(_DROP_TAGS)):
        tag.decompose()

    # Embedded players -> plain links so the information survives.
    for iframe in soup.find_all("iframe"):
        src = str(iframe.get("src", ""))
        if src.startswith("//"):
            src = "https:" + src
        m = _YOUTUBE_RE.search(src)
        link = f"https://www.youtube.com/watch?v={m.group(1)}" if m else src
        label = "Watch the video" if m else "Embedded content"
        p = soup.new_tag("p")
        a = soup.new_tag("a", href=link)
        a.string = f"{label}: {link}"
        p.append(a)
        iframe.replace_with(p)

    # 1-column tables are callout boxes -> blockquote.
    for table in soup.find_all("table"):
        rows = _callout_rows(table)
        if rows is None:
            continue
        quote = soup.new_tag("blockquote")
        for tr in rows:
            cell = tr.find(["td", "th"])
            if isinstance(cell, Tag):
                for child in list(cell.children):
                    quote.append(child.extract())
        holder = table.parent if isinstance(table.parent, Tag) and table.parent.name == "figure" else table
        holder.replace_with(quote)

    # Empty anchors (<a name="x"></a>) and href-less links carry nothing in Markdown.
    for a in soup.find_all("a"):
        has_content = bool(a.get_text(strip=True)) or a.find("img") is not None
        if not a.get("href"):
            a.unwrap() if has_content else a.decompose()
        elif not has_content:
            a.decompose()

    for a in soup.find_all("a", href=True):
        a["href"] = _normalize_href(str(a["href"]))

    # In-page table of contents and "back to top" links are navigation, not content.
    for ul in soup.find_all(["ul", "ol"]):
        if ul.parent is not None and _is_toc_list(ul):
            ul.decompose()
    for p in soup.find_all("p"):
        if _BACK_TO_TOP_RE.match(p.get_text()) and p.find("a"):
            p.decompose()

    # Bold inside headings renders as '## **x**' - drop the inner emphasis; drop empty headings.
    for h in soup.find_all(_HEADINGS):
        for em in h.find_all(["strong", "b", "em", "i"]):
            em.unwrap()
        if not h.get_text(strip=True):
            if h.find("img") is None:
                h.decompose()
            else:  # image-only heading: keep the image as a paragraph, not an empty heading
                h.name = "p"

    # Tables without a header row: promote the first row so Markdown gets a real header.
    for table in soup.find_all("table"):
        if table.find("th") is None:
            first = table.find("tr")
            if isinstance(first, Tag):
                for td in first.find_all("td", recursive=False):
                    td.name = "th"

    # '<strong> text </strong>' -> ' <strong>text</strong> ' (Markdown emphasis cannot span spaces).
    for em in soup.find_all(["strong", "b", "em", "i"]):
        _hoist_whitespace(em)
        if not em.get_text(strip=True) and em.find("img") is None:
            em.unwrap()

    # Everything else that is not on the allow-list is presentation noise: keep its text only.
    for tag in soup.find_all(True):
        if tag.name not in _KEEP_TAGS:
            tag.unwrap()


def _postprocess(md: str) -> str:
    md = md.replace("\xa0", " ").replace("​", "")
    md = md.replace("****", "")  # adjacent bold runs
    md = re.sub(r"^#{1,6}[ \t]*$\n?", "", md, flags=re.M)  # headings that lost all their text
    md = re.sub(r"[ \t]+$", "", md, flags=re.M)  # trailing whitespace
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def html_to_markdown(html: str) -> str:
    """Convert one article body to Markdown (headings, lists, tables, code, links, images kept)."""
    soup = BeautifulSoup(html, "html.parser")
    _preprocess(soup)
    return _postprocess(_make_converter().convert_soup(soup))


def _yaml_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_article(
    *,
    slug: str,
    article_id: int,
    title: str,
    url: str,
    section: str,
    category: str,
    updated_at: str,
    body_html: str,
) -> MarkdownDoc:
    """Render the full Markdown file: front matter, H1, an 'Article URL:' line, then the body.

    The 'Article URL:' line is what OptiBot's system prompt asks the model to cite, so every
    document carries it verbatim right under the title.
    """
    body = html_to_markdown(body_html)
    front = "\n".join(
        [
            "---",
            f"title: {_yaml_str(title)}",
            f"article_id: {article_id}",
            f"url: {url}",
            f"section: {_yaml_str(section)}",
            f"category: {_yaml_str(category)}",
            f"updated_at: {updated_at}",
            "---",
        ]
    )
    content = f"{front}\n\n# {title}\n\nArticle URL: {url}\n\n{body}"
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return MarkdownDoc(slug=slug, filename=f"{slug}.md", content=content, content_hash=digest)


def estimate_chunks(content: str, max_tokens: int, overlap: int) -> int:
    """Estimate how many chunks Gemini's white-space chunker will produce for this document.

    The File Search API does not report chunk counts, so we mirror its strategy: tokens are
    whitespace-separated words, windows of max_tokens sliding by (max_tokens - overlap).
    """
    words = len(content.split())
    if words <= max_tokens:
        return 1
    step = max(1, max_tokens - overlap)
    return 1 + -(-(words - max_tokens) // step)
