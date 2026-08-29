#!/usr/bin/env python3
"""Convert the preserved Blogger HTML bodies into editable Markdown files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from markdown_conversion import html_to_markdown


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_post(post: dict) -> str:
    return "\n".join(
        [
            "---",
            f"title: {yaml_string(post['title'])}",
            f"date: {yaml_string(post['published'])}",
            f"updated: {yaml_string(post['updated'])}",
            f"permalink: {yaml_string('/' + post['route'])}",
            f"original_url: {yaml_string(post['url'])}",
            f"blogger_id: {yaml_string(post['blogger_id'])}",
            f"tags: {json.dumps(post['tags'], ensure_ascii=False)}",
            "layout: post",
            "---",
            "",
                html_to_markdown(post["content"]).rstrip(),
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    data_path = root / "data" / "posts.json"
    payload = json.loads(data_path.read_text(encoding="utf-8"))
    converted = 0
    embeds = 0
    for post in payload["posts"]:
        target = root / "content" / "posts" / post["content_file"]
        body = html_to_markdown(post["content"])
        embeds += body.count("<iframe")
        target.write_text(render_post(post), encoding="utf-8")
        converted += 1
    print(json.dumps({"converted_posts": converted, "preserved_iframes": embeds}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
