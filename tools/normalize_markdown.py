#!/usr/bin/env python3
"""Normalize imported Markdown so every post renders as real Markdown.

The Blogger and HackMD imports left a small set of mechanical defects behind:
HackMD-only fence spellings, code fences that were truncated before their
closing marker, lists and tables that lost the blank line Python-Markdown needs
in front of them, nested bullets indented by two spaces instead of four, image
URLs broken across lines, and leftover import bookkeeping comments.

HackMD's own syntax (``:::info`` containers, ``~~strikethrough~~``, task lists)
is deliberately left alone: it is rendered by ``tools/markdown_hackmd.py`` so the
Markdown source stays portable.

Every rule below is fence-aware (nothing inside a code block is ever touched)
and front-matter-aware, and each one reports how many files it changed so a run
can be audited.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FENCE_EXTENSION = re.compile(r"(?m)^(`{3,}[^`\r\n]*)=[ \t]*$")
FENCE_PREFIX_EXTENSION = re.compile(r"(?m)^(`{3,})=([A-Za-z0-9_+-]+)[ \t]*$")

FENCE_LINE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})")
INDENTED_FENCE = re.compile(r"^[ \t]{4,}(`{3,}|~{3,})[ \t]*$")
# HackMD writes ```python! / ```=  and the Blogger import produced info strings
# with spaces in them; Python-Markdown accepts none of those and silently leaves
# the whole block as literal text, which cascades into every fence after it.
FENCE_OPEN = re.compile(r"^(?P<indent>[ \t]{0,3})(?P<fence>`{3,}|~{3,})(?P<info>[^\r\n]*)$")
VALID_INFO = re.compile(r"^\.?[\w#.+-]*$")
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d{1,3}[.)])\s+\S")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
HEADING = re.compile(r"^#{1,6} \S")

# ``** text**`` / ``**text **`` never renders as emphasis; the import produced a
# handful of these when Blogger had a stray space inside a <b> tag.
LOOSE_EMPHASIS = re.compile(r"(?<![*\w])(\*\*|__)[ \t\xa0]+([^*_\n]+?)[ \t\xa0]*\1(?![*\w])")
LOOSE_EMPHASIS_TAIL = re.compile(r"(?<![*\w])(\*\*|__)([^*_\n]+?)[ \t\xa0]+\1(?![*\w])")

# The import occasionally wrapped a Markdown link inside another link.
NESTED_LINK = re.compile(r"\[(\[[^\]\n]*\]\([^)\s]+\))\]\([^)\s]+\)")

# An image or link whose URL was split across lines by the HTML conversion.
BROKEN_MEDIA = re.compile(r"(!?\[[^\]\n]*\])\(\s*<?([^)]*?)>?\s*\)", re.DOTALL)

# Blogger wrapped some images and whole bullet lists in an <h1>, which the
# conversion turned into a heading that is not a heading.
PSEUDO_HEADING = re.compile(r"^#{1,6}[ \t]+(?P<rest>(?:!\[[^\]]*\]\([^)\s]+\)|[-*] ).*)$")

# Blogger collapsed some <br>-separated bullet lists onto a single line.
INLINE_BULLETS = re.compile(r"^[-*] .+?(?: [-*] .+?){2,}$")

# Blogger emitted non-breaking spaces inside ordinary prose, which silently
# break emphasis and list parsing.
NBSP = "\u00a0"
# One trailing space means nothing in Markdown; two or more are a hard break.
SINGLE_TRAILING_SPACE = re.compile(r"(?m)(?<![ \t])[ \t]$")

# Misspellings confirmed by reading each occurrence in context. Only words that
# are never a real identifier in this archive are listed, and replacements run
# outside code so a typo inside a snippet is left exactly as it was written.
MISSPELLINGS = {
    "fucntion": "function", "funciton": "function", "fuctnion": "function",
    "funciotn": "function", "funaction": "function",
    "comiler": "compiler", "complier": "compiler",
    "semarntic": "Semantic", "optimziztion": "Optimization",
    "soruce": "source", "sorce": "source",
    "windwos": "windows", "windos": "windows",
    "regitster": "register", "regiser": "register",
    "clinet": "client", "preocess": "process", "requset": "request",
    "virtial": "virtual", "herder": "header", "serlet": "servlet",
    "seesion": "session", "sesion": "session", "slcing": "slicing",
    "docer": "docker", "reids": "Redis", "nutika": "Nuitka",
    "traing": "training", "trainging": "training", "addree": "address",
}
MISSPELLING_RE = re.compile(
    r"(?<![\w/._-])(" + "|".join(sorted(MISSPELLINGS, key=len, reverse=True)) + r")(?![\w/._-])",
    re.IGNORECASE,
)
INLINE_CODE = re.compile(r"`[^`\n]*`")
# A space in front of full-width punctuation, and a half-width comma wedged
# between two Chinese characters, are both typing slips rather than style.
SPACE_BEFORE_CJK_PUNCT = re.compile(r"[ \t]+(?=[，。！？；：、）」』])")
HALFWIDTH_COMMA_IN_CJK = re.compile(r"(?<=[\u4e00-\u9fff]),(?=[\u4e00-\u9fff])")
# A line that begins with closing punctuation is the tail of the sentence above,
# split by an editor wrap; rendered, it shows up as a gap before the comma.
ORPHAN_PUNCT_LINE = re.compile(r"^[，。！？；：、）」』]")

# Import bookkeeping comments: useful while migrating, noise in a published post.
IMPORT_MARKER = re.compile(
    r"(?m)^[ \t]*<!--[ \t]*(?:Converted from Blogger HTML[^>]*?"
    r"|Public HackMD source imported from[^>]*?"
    r"|End public HackMD source)[ \t]*-->[ \t]*\n?"
)

# A standalone image line never appears inside real code, so finding one inside a
# fenced block is proof the fences were mispaired by the import.
STANDALONE_IMAGE = re.compile(r"^!\[[^\]]*\]\([^)\s]+\)\s*$")


def split_front_matter(source: str) -> tuple[str, str]:
    if not source.startswith("---\n"):
        return "", source
    end = source.find("\n---\n", 3)
    if end == -1:
        return "", source
    return source[: end + 5], source[end + 5 :]


def fence_marker(line: str) -> str | None:
    """The fence marker on this line, using Python-Markdown's own rules.

    Python-Markdown closes a fence with a back-reference, so ``````` inside a
    ```````` block is content, not a closer, and a marker indented by four or
    more spaces is not a fence at all.
    """
    match = FENCE_LINE.match(line)
    return match.group(1) if match else None


def fence_mask(lines: list[str]) -> list[bool]:
    """True for every line that lives inside a fenced code block."""
    mask: list[bool] = []
    fence: str | None = None
    for line in lines:
        marker = fence_marker(line)
        if fence is None and marker:
            fence = marker
            mask.append(True)
            continue
        if fence is not None and marker == fence:
            fence = None
            mask.append(True)
            continue
        mask.append(fence is not None)
    return mask


def apply_outside_code(line: str, transform) -> str:
    """Run a text transform on a line while leaving `inline code` untouched."""
    parts: list[str] = []
    index = 0
    for match in INLINE_CODE.finditer(line):
        parts.append(transform(line[index : match.start()]))
        parts.append(match.group(0))
        index = match.end()
    parts.append(transform(line[index:]))
    return "".join(parts)


def fix_misspellings(body: str) -> str:
    """Correct the curated misspelling list in prose only."""

    def repair(text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            word = match.group(1)
            correction = MISSPELLINGS[word.lower()]
            # "Fucntion" keeps its capital; an all-caps heading keeps its shape.
            if word.isupper():
                return correction.upper()
            if word[0].isupper() and not correction[0].isupper():
                return correction.capitalize()
            return correction

        return MISSPELLING_RE.sub(replace, text)

    lines = body.split("\n")
    mask = fence_mask(lines)
    for index, line in enumerate(lines):
        if not mask[index]:
            lines[index] = apply_outside_code(line, repair)
    return "\n".join(lines)


def fix_cjk_punctuation(body: str) -> str:
    """Remove the stray space before full-width punctuation and fix `,` in prose."""

    def repair(text: str) -> str:
        return HALFWIDTH_COMMA_IN_CJK.sub("，", SPACE_BEFORE_CJK_PUNCT.sub("", text))

    lines = body.split("\n")
    mask = fence_mask(lines)
    for index, line in enumerate(lines):
        if not mask[index]:
            lines[index] = apply_outside_code(line, repair)
    return "\n".join(lines)


def rejoin_orphan_punctuation(body: str) -> str:
    """Pull a line that starts with closing punctuation back onto its sentence."""
    lines = body.split("\n")
    mask = fence_mask(lines)
    out: list[str] = []
    for index, line in enumerate(lines):
        previous = out[-1] if out else ""
        joinable = (
            out
            and not mask[index]
            and ORPHAN_PUNCT_LINE.match(line)
            and previous.strip()
            and not previous.endswith("  ")          # keep hard line breaks
            and not FENCE_LINE.match(previous)
            and not LIST_ITEM.match(previous)
            and not TABLE_ROW.match(previous)
            and not HEADING.match(previous)
            and not previous.lstrip().startswith((">", "<", "|"))
        )
        if joinable:
            out[-1] = previous.rstrip() + line
            continue
        out.append(line)
    return "\n".join(out)


def normalize_whitespace(body: str) -> str:
    """Replace Blogger's non-breaking spaces and drop meaningless trailing space."""
    lines = body.split("\n")
    mask = fence_mask(lines)
    for index, line in enumerate(lines):
        if mask[index]:
            continue
        lines[index] = SINGLE_TRAILING_SPACE.sub("", line.replace(NBSP, " "))
    return "\n".join(lines)


def strip_import_markers(body: str) -> str:
    """Drop the migration bookkeeping comments from the published Markdown."""
    cleaned = IMPORT_MARKER.sub("", body)
    # Only close the gap the removed comment left, so the rule stays idempotent.
    return re.sub(r"\n{3,}", "\n\n", cleaned) if cleaned != body else body


def unwrap_pseudo_headings(body: str) -> str:
    """Drop the ``#`` from headings that only wrap an image or a whole list."""
    lines = body.split("\n")
    mask = fence_mask(lines)
    for index, line in enumerate(lines):
        if mask[index]:
            continue
        match = PSEUDO_HEADING.match(line)
        if match:
            lines[index] = match.group("rest")
    return "\n".join(lines)


def split_inline_bullets(body: str) -> str:
    """Break a list that the import flattened onto one line back into items."""
    lines = body.split("\n")
    mask = fence_mask(lines)
    out: list[str] = []
    for index, line in enumerate(lines):
        if mask[index] or not INLINE_BULLETS.match(line.strip()):
            out.append(line)
            continue
        items = re.split(r" (?=[-*] )", line.strip())
        if len(items) < 3:
            out.append(line)
            continue
        out.extend(items)
    return "\n".join(out)


def repair_table_delimiter(body: str) -> str:
    """Restore the ``| --- |`` row the import replaced with whitespace."""
    lines = body.split("\n")
    mask = fence_mask(lines)
    for index in range(1, len(lines) - 1):
        if mask[index] or lines[index].strip():
            continue
        header, following = lines[index - 1], lines[index + 1]
        if not (TABLE_ROW.match(header) and TABLE_ROW.match(following)):
            continue
        columns = header.strip().strip("|").count("|") + 1
        lines[index] = "|" + "|".join([" --- "] * columns) + "|"
    return "\n".join(lines)


def fence_pipe_diagrams(body: str) -> str:
    """A lone ``|a|-->|b|`` line is ASCII art, not a table; render it as code."""
    lines = body.split("\n")
    mask = fence_mask(lines)
    for index, line in enumerate(lines):
        stripped = line.strip()
        if mask[index] or not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        if "--&gt;" not in stripped and "-->" not in stripped and "→" not in stripped:
            continue
        neighbours = [
            lines[offset]
            for offset in (index - 1, index + 1)
            if 0 <= offset < len(lines)
        ]
        if any(TABLE_ROW.match(neighbour) for neighbour in neighbours):
            continue
        lines[index] = f"`{stripped}`"
    return "\n".join(lines)


def adopt_indented_closer(body: str) -> str:
    """An over-indented lone marker is a closer whose opener the import dropped.

    Python-Markdown ignores a fence indented by four spaces or more, so the block
    above it renders as prose and the marker itself renders as literal text. Pull
    the marker back to column zero and open a fence in front of the run it closes.
    """
    lines = body.split("\n")
    out: list[str] = []
    fence: str | None = None
    for line in lines:
        marker = fence_marker(line)
        if marker:
            fence = None if marker == fence else (fence or marker)
            out.append(line)
            continue
        if fence is None and INDENTED_FENCE.match(line):
            start = len(out)
            while start > 0 and out[start - 1].strip() and not fence_marker(out[start - 1]):
                start -= 1
            if start < len(out):
                out.insert(start, "```")
                out.append("```")
                continue
        out.append(line)
    return "\n".join(out)


def split_fence_on_prose(body: str) -> str:
    """Close a fence that swallowed prose because its partner marker was lost."""
    lines = body.split("\n")
    out: list[str] = []
    fence: str | None = None
    opened_at = 0
    for line in lines:
        marker = fence_marker(line)
        if marker:
            if fence is None:
                fence = marker
                opened_at = len(out)
            elif marker == fence:
                fence = None
            out.append(line)
            continue
        if fence is not None and STANDALONE_IMAGE.match(line) and len(out) > opened_at + 1:
            out.append(fence)
            out.append("")
            fence = None
        out.append(line)
    return "\n".join(out)


def close_unclosed_fence(body: str) -> str:
    lines = body.split("\n")
    fence: str | None = None
    for line in lines:
        marker = fence_marker(line)
        if marker is None:
            continue
        if fence is None:
            fence = marker
        elif marker == fence:
            fence = None
    if fence is None:
        return body
    trailing = ""
    while lines and not lines[-1].strip():
        trailing = "\n" + trailing
        lines.pop()
    opener = max(
        index for index, line in enumerate(lines) if fence_marker(line) == fence
    )
    remainder = [
        line for line in lines[opener + 1 :]
        if line.strip() and not line.strip().startswith("<!--")
    ]
    if not remainder:
        # Nothing left to fence: the marker is a leftover, not a truncation.
        del lines[opener]
        return "\n".join(lines) + (trailing or "\n")
    # A truncated import ends mid-block: close it so the code renders as code,
    # keeping the import's trailing HTML comments outside the block.
    tail: list[str] = []
    while lines and (not lines[-1].strip() or lines[-1].strip().startswith("<!--")):
        tail.insert(0, lines.pop())
    return "\n".join([*lines, fence, *tail]) + (trailing or "\n")


def normalize_fence_markers(body: str) -> str:
    """Make every fence marker one Python-Markdown actually recognises."""
    lines = body.split("\n")
    fence: str | None = None
    for index, line in enumerate(lines):
        match = FENCE_OPEN.match(line)
        if not match:
            continue
        marker = match.group("fence")
        if fence is not None:
            if marker == fence:
                fence = None
                lines[index] = marker
            continue
        info = match.group("info").strip().rstrip("!=")
        if not VALID_INFO.match(info):
            # "add new fucntion" -> "add"; drop it entirely when the first word
            # is not a usable language token.
            first = info.split()[0] if info.split() else ""
            info = first if VALID_INFO.match(first) and first else ""
        fence = marker
        lines[index] = marker + info
    return "\n".join(lines)


def collapse_nested_links(body: str) -> str:
    lines = body.split("\n")
    mask = fence_mask(lines)
    for index, line in enumerate(lines):
        if not mask[index]:
            lines[index] = NESTED_LINK.sub(r"\1", line)
    return "\n".join(lines)


def blank_line_before_blocks(body: str) -> str:
    lines = body.split("\n")
    mask = fence_mask(lines)
    out: list[str] = []
    for index, line in enumerate(lines):
        if index and not mask[index] and not mask[index - 1]:
            previous = lines[index - 1]
            # Headings already parse without a leading blank line; lists and
            # tables do not, and that is what left literal "- item" / "| a |"
            # rows in the rendered posts.
            list_start = LIST_ITEM.match(line)
            # An indented item preceded by a blank line turns into an indented
            # code block, so only unindented list starts are safe to separate.
            if list_start and len(list_start.group(1).expandtabs(4)) >= 4:
                list_start = None
            starts_block = list_start or TABLE_ROW.match(line)
            previous_is_prose = (
                previous.strip()
                and not LIST_ITEM.match(previous)
                and not TABLE_ROW.match(previous)
                and not HEADING.match(previous)
                and not previous.lstrip().startswith((">", "<", "|"))
                and not previous.endswith("  ")
            )
            if starts_block and previous_is_prose:
                out.append("")
        out.append(line)
    return "\n".join(out)


def normalize_nested_indent(body: str) -> str:
    """Re-indent list nesting by depth instead of by the import's raw spacing.

    The HackMD and Blogger sources nest with two, five or sixteen spaces. Python-
    Markdown measures nesting in four-space steps and turns anything deeper into
    an indented code block, so depth has to be recomputed from the structure.
    """
    lines = body.split("\n")
    mask = fence_mask(lines)
    out = list(lines)
    levels: list[int] = []
    current = 0
    for index, line in enumerate(lines):
        if mask[index]:
            levels, current = [], 0
            continue
        if not line.strip():
            continue
        match = LIST_ITEM.match(line)
        if match:
            indent = len(match.group(1).expandtabs(4))
            while levels and indent < levels[-1]:
                levels.pop()
            if not levels or indent > levels[-1]:
                levels.append(indent)
            depth = len(levels) - 1
            current = depth * 4
            out[index] = " " * current + line.lstrip()
            continue
        indent = len(line) - len(line.lstrip())
        if not levels:
            continue
        if indent == 0:
            levels, current = [], 0
            continue
        # A continuation line must stay inside its item without reaching the
        # four-space step that would make it an indented code block.
        out[index] = " " * (current + 2) + line.lstrip()
    return "\n".join(out)


def fix_loose_emphasis(body: str) -> str:
    lines = body.split("\n")
    mask = fence_mask(lines)
    for index, line in enumerate(lines):
        if mask[index]:
            continue
        fixed = LOOSE_EMPHASIS.sub(r"\1\2\1", line)
        fixed = LOOSE_EMPHASIS_TAIL.sub(r"\1\2\1", fixed)
        lines[index] = fixed
    return "\n".join(lines)


def rejoin_broken_media(body: str) -> str:
    """Rebuild image/link targets that the HTML conversion split across lines."""

    def repair(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        if "\n" not in target and "<" not in match.group(0):
            return match.group(0)
        collapsed = re.sub(r"\s+", "", target).replace("<", "").replace(">", "")
        if not collapsed or " " in collapsed:
            return match.group(0)
        return f"{label}({collapsed})"

    lines = body.split("\n")
    mask = fence_mask(lines)
    # Only rewrite regions that are entirely outside code fences.
    chunks: list[str] = []
    buffer: list[str] = []
    buffer_masked = mask[0] if mask else False
    for index, line in enumerate(lines):
        masked = mask[index] if index < len(mask) else False
        if masked != buffer_masked:
            text = "\n".join(buffer)
            chunks.append(text if buffer_masked else BROKEN_MEDIA.sub(repair, text))
            buffer, buffer_masked = [], masked
        buffer.append(line)
    text = "\n".join(buffer)
    chunks.append(text if buffer_masked else BROKEN_MEDIA.sub(repair, text))
    return "\n".join(chunks)


RULES = (
    ("import-markers", strip_import_markers),
    ("whitespace", normalize_whitespace),
    ("misspellings", fix_misspellings),
    ("orphan-punctuation", rejoin_orphan_punctuation),
    ("cjk-punctuation", fix_cjk_punctuation),
    ("hackmd-fence", lambda body: FENCE_PREFIX_EXTENSION.sub(r"\1\2", FENCE_EXTENSION.sub(r"\1", body))),
    ("fence-marker", normalize_fence_markers),
    ("indented-closer", adopt_indented_closer),
    ("fence-prose", split_fence_on_prose),
    ("pseudo-heading", unwrap_pseudo_headings),
    ("inline-bullets", split_inline_bullets),
    ("table-delimiter", repair_table_delimiter),
    ("pipe-diagram", fence_pipe_diagrams),
    ("unclosed-fence", close_unclosed_fence),
    ("nested-link", collapse_nested_links),
    ("broken-media", rejoin_broken_media),
    ("loose-emphasis", fix_loose_emphasis),
    ("nested-indent", normalize_nested_indent),
    ("blank-line", blank_line_before_blocks),
)


def normalize_title(front: str) -> str:
    """Trim and de-duplicate whitespace in the front-matter title."""

    def repair(match: re.Match[str]) -> str:
        title = match.group("title")
        cleaned = re.sub(r"[ \t]{2,}", " ", title.replace(NBSP, " ")).strip(" \t\u3000")
        return f'title: "{cleaned}"' if cleaned else match.group(0)

    return re.sub(r'(?m)^title: "(?P<title>.*)"$', repair, front)


def normalize(path: Path, counters: dict[str, int]) -> bool:
    source = path.read_text(encoding="utf-8")
    front, body = split_front_matter(source)
    original_front, original = front, body
    front = normalize_title(front)
    if front != original_front:
        counters["title"] = counters.get("title", 0) + 1
    for name, rule in RULES:
        updated = rule(body)
        if updated != body:
            counters[name] = counters.get(name, 0) + 1
            body = updated
    if body == original and front == original_front:
        return False
    path.write_text(front + body, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing them.")
    args = parser.parse_args()
    root = args.root.resolve()
    files = [
        *sorted((root / "content" / "posts").glob("*.md")),
        *sorted((root / "source" / "hackmd").glob("*.md")),
    ]
    counters: dict[str, int] = {}
    changed = 0
    for path in files:
        if args.dry_run:
            source = path.read_text(encoding="utf-8")
            front, body = split_front_matter(source)
            probe = body
            if normalize_title(front) != front:
                counters["title"] = counters.get("title", 0) + 1
            for name, rule in RULES:
                updated = rule(probe)
                if updated != probe:
                    counters[name] = counters.get(name, 0) + 1
                    probe = updated
            changed += probe != body
        else:
            changed += normalize(path, counters)
    for name in ("title", *(name for name, _ in RULES)):
        print(f"{name}={counters.get(name, 0)}")
    print(f"normalized_files={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
