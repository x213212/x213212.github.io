"""Loss-aware HTML → Markdown conversion used by the Blogger migration."""

from __future__ import annotations

import re

from markdownify import MarkdownConverter


def code_language(element) -> str | None:
    classes = " ".join(element.get("class", []))
    for pattern in (r"(?:language|lang)-([\w+-]+)", r"brush:\s*([\w+-]+)"):
        match = re.search(pattern, classes, flags=re.IGNORECASE)
        if match:
            return match.group(1).lower()
    return None


def fenced(source: str, language: str = "") -> str:
    # A longer fence avoids accidentally closing around code that includes ```.
    longest = max((len(run) for run in re.findall(r"`+", source)), default=0)
    marker = "`" * max(3, longest + 1)
    return f"\n{marker}{language}\n{source.strip()}\n{marker}\n"


class LossAwareConverter(MarkdownConverter):
    """Keep embeds and executable snippets as readable, non-executable source."""

    def convert_pre(self, element, text, convert_as_inline):
        if not text:
            return ""
        return fenced(text, code_language(element) or self.options["code_language"])

    def convert_img(self, element, text, convert_as_inline):
        # Always emit image Markdown, including images wrapped by a link.  The
        # upstream converter treats some inline images as alt text, which would
        # silently lose image placement in older Blogger posts.
        source = (
            element.attrs.get("src")
            or element.attrs.get("data-src")
            or element.attrs.get("data-original-src")
            or ""
        ).strip()
        if not source:
            return ""
        alt = str(element.attrs.get("alt", "")).replace("[", "\\[").replace("]", "\\]")
        title = str(element.attrs.get("title", "")).replace('"', r'\"')
        title_part = f' "{title}"' if title else ""
        return f"\n\n![{alt}]({source}{title_part})\n\n"

    def convert_iframe(self, element, text, convert_as_inline):
        return f"\n\n{element}\n\n"

    def convert_video(self, element, text, convert_as_inline):
        return f"\n\n{element}\n\n"

    def convert_audio(self, element, text, convert_as_inline):
        return f"\n\n{element}\n\n"

    def convert_object(self, element, text, convert_as_inline):
        return f"\n\n{element}\n\n"

    def convert_embed(self, element, text, convert_as_inline):
        return f"\n\n{element}\n\n"

    def convert_script(self, element, text, convert_as_inline):
        return fenced(str(element), "html")

    def convert_style(self, element, text, convert_as_inline):
        return fenced(str(element), "html")


def html_to_markdown(source: str) -> str:
    converter = LossAwareConverter(
        heading_style="ATX",
        bullets="-",
        strong_em_symbol="*",
        code_language_callback=code_language,
        escape_asterisks=False,
        escape_underscores=False,
    )
    markdown = converter.convert(source)
    markdown = re.sub(r"\n{4,}", "\n\n\n", markdown).strip()
    return f"{markdown}\n" if markdown else ""
