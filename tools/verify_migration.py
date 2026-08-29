#!/usr/bin/env python3
"""Verify post inventory, source Markdown, images, public HackMD hydration, and output."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup


MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(\s*(?:<)?(?P<url>[^\s>)]+)", re.MULTILINE)
HACKMD_IFRAME = re.compile(r"<iframe[^>]+(?:https?:)?//(?:www\.)?hackmd\.io", re.IGNORECASE)
HACKMD_FENCE = re.compile(r"(?m)^`{3,}[^`\r\n]*=")


def normalize_url(value: str) -> str:
    value = html.unescape(value).strip()
    if value.startswith("//"):
        value = f"https:{value}"
    parsed = urlsplit(value)
    if parsed.scheme in {"http", "https"}:
        return urlunsplit(("https", parsed.netloc.lower(), parsed.path, parsed.query, ""))
    return value


def source_body(value: str) -> str:
    if not value.startswith("---\n"):
        return value
    marker = value.find("\n---\n", 4)
    return value[marker + 5 :] if marker != -1 else value


def source_is_draft(value: str) -> bool:
    """Treat admin-managed drafts as intentionally absent from static output."""
    if not value.startswith("---\n"):
        return False
    marker = value.find("\n---\n", 4)
    if marker == -1:
        return False
    for line in value[4:marker].splitlines():
        if not line.startswith("draft:"):
            continue
        raw = line.split(":", 1)[1].strip().casefold().strip('"')
        return raw in {"true", "1", "yes", "on", "draft"}
    return False


def original_images(raw_html: str) -> list[str]:
    soup = BeautifulSoup(raw_html, "html.parser")
    values = []
    for image in soup.find_all("img"):
        source = image.get("src") or image.get("data-src") or image.get("data-original-src")
        if source:
            values.append(normalize_url(str(source)))
    return values


def markdown_images(markdown: str) -> list[str]:
    return [normalize_url(match.group("url")) for match in MARKDOWN_IMAGE.finditer(markdown)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    posts = json.loads((root / "data" / "posts.json").read_text(encoding="utf-8"))["posts"]
    categories = json.loads((root / "data" / "categories.json").read_text(encoding="utf-8"))
    assignments = categories.get("assignments", {})
    failures: dict[str, list[str]] = {
        "missing_source_files": [],
        "missing_output_files": [],
        "missing_original_images": [],
        "image_order_mismatch": [],
        "unclassified_posts": [],
        "hackmd_iframes_remaining": [],
        "hackmd_fences_remaining": [],
    }
    original_count = 0
    markdown_count = 0

    published_original_posts = 0
    published_output_posts = 0
    for post in posts:
        route = post["route"]
        source_path = root / "content" / "posts" / post["content_file"]
        output_path = root / "docs" / route
        if not source_path.exists():
            failures["missing_source_files"].append(route)
            continue
        source = source_path.read_text(encoding="utf-8")
        draft = source_is_draft(source)
        if not draft:
            published_original_posts += 1
        if not draft:
            if output_path.exists():
                published_output_posts += 1
            else:
                failures["missing_output_files"].append(route)
        markdown = source_body(source)
        expected = original_images(post["content"])
        actual = markdown_images(markdown)
        original_count += len(expected)
        markdown_count += len(actual)
        actual_set = set(actual)
        missing = [url for url in expected if url not in actual_set]
        if missing:
            failures["missing_original_images"].append(route)
        actual_original_order = [url for url in actual if url in set(expected)]
        expected_deduped = list(expected)
        if not missing and actual_original_order[: len(expected_deduped)] != expected_deduped:
            failures["image_order_mismatch"].append(route)
        if not assignments.get(route):
            failures["unclassified_posts"].append(route)
        if HACKMD_IFRAME.search(markdown):
            failures["hackmd_iframes_remaining"].append(route)
        if HACKMD_FENCE.search(markdown):
            failures["hackmd_fences_remaining"].append(route)

    report = {
        "post_count": len(posts),
        "markdown_source_count": len(list((root / "content" / "posts").glob("*.md"))),
        "output_post_count": published_output_posts,
        "published_original_post_count": published_original_posts,
        "original_img_tag_count": original_count,
        "markdown_image_count_including_hackmd": markdown_count,
        "failures": failures,
        "passed": not any(failures.values()),
    }
    (root / "data" / "verification-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in report if key != "failures"}, ensure_ascii=False))
    for name, values in failures.items():
        print(f"{name}={len(values)}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
