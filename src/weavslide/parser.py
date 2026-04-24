"""Shared parsing utilities for .slide.html files.

A .slide.html file consists of three top-level custom elements:
<slide>, <thoughts>, and <spoken>. All three are required.

<slide>    — PPT slide content (any HTML, kept as raw string)
<thoughts> — fragmented notes / ideas (any HTML, kept as raw string)
<spoken>   — TTS narration script; must contain ONLY <p> elements as direct
             children, extracted into a list of inner-HTML strings
"""

from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class ParseError:
    """A validation error found during parsing.

    Attributes:
        line: Approximate source line number (0 if not applicable).
        message: Human-readable error description.
    """

    line: int
    message: str


@dataclass
class SlideFile:
    """Represents a parsed .slide.html file.

    slide_html and thoughts_html carry the inner HTML of each section
    (without the wrapper tags). spoken_paragraphs is a list of inner-HTML
    strings, one per <p> inside <spoken>.
    """

    path: Path
    slide_html: str = ""
    thoughts_html: str = ""
    spoken_paragraphs: list[str] = field(default_factory=list)
    errors: list[ParseError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True when no errors were found."""
        return len(self.errors) == 0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_slide_file(path: Path) -> SlideFile:
    """Parse a single .slide.html file.

    Returns a SlideFile containing slide/thoughts as raw HTML strings,
    spoken as a list of paragraph inner-HTML strings, and any validation
    errors.  result.is_valid is True only when no errors were found.

    Errors include:
    - File read / encoding problems
    - Missing required top-level elements (<slide>, <thoughts>, <spoken>)
    - Duplicate top-level elements
    - Unknown top-level elements
    - <spoken> containing non-<p> children or bare text
    """
    errors: list[ParseError] = []

    # -- read file --
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(ParseError(0, f"读取文件失败: {exc}"))
        return SlideFile(path=path, errors=errors)

    # -- parse HTML with BeautifulSoup --
    soup = BeautifulSoup(content, "html.parser")

    # Collect top-level tags (direct children of the document root)
    toplevel_tags = [child for child in soup.children if isinstance(child, Tag)]

    required = {"slide", "thoughts", "spoken"}
    found: set[str] = set()

    for tag in toplevel_tags:
        name = tag.name
        line = tag.sourceline or 0
        if name in required:
            if name in found:
                errors.append(ParseError(line, f"重复的顶层元素: <{name}>"))
            else:
                found.add(name)
        else:
            errors.append(
                ParseError(
                    line,
                    f"不允许的顶层元素: <{name}>，只允许 <slide> <thoughts> <spoken>",
                )
            )

    # -- check required sections --
    for tag in ("slide", "thoughts", "spoken"):
        if tag not in found:
            errors.append(ParseError(0, f"缺少必要的顶层元素: <{tag}>"))

    # -- extract slide / thoughts inner HTML --
    slide_tag = soup.find("slide")
    thoughts_tag = soup.find("thoughts")

    slide_html = "".join(str(c) for c in slide_tag.contents) if slide_tag else ""
    thoughts_html = (
        "".join(str(c) for c in thoughts_tag.contents) if thoughts_tag else ""
    )

    # -- extract and validate <spoken> --
    spoken_paragraphs: list[str] = []
    spoken_tag = soup.find("spoken")
    if spoken_tag:
        for child in spoken_tag.children:
            if isinstance(child, Tag):
                if child.name != "p":
                    errors.append(
                        ParseError(
                            child.sourceline or 0,
                            f"<spoken> 内只能包含 <p> 元素，发现: <{child.name}>",
                        )
                    )
            elif isinstance(child, NavigableString):
                if child.strip():
                    snippet = child.strip()[:50]
                    errors.append(
                        ParseError(
                            0,
                            f'<spoken> 内只能包含 <p> 元素，发现文本: "{snippet}"',
                        )
                    )

        for p in spoken_tag.find_all("p", recursive=False):
            spoken_paragraphs.append("".join(str(c) for c in p.contents))

    return SlideFile(
        path=path,
        slide_html=slide_html,
        thoughts_html=thoughts_html,
        spoken_paragraphs=spoken_paragraphs,
        errors=errors,
    )
