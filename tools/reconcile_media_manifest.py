#!/usr/bin/env python3
"""Add rendered Markdown article media to the local-media manifest.

The initial Blogger import produced ``media-manifest.json`` before public
HackMD iframe sources were converted to Markdown.  This reconciler reads the
same Markdown rendering settings as the site builder, so it adds only media
that will actually render in an article (and does not mistake image-looking
text inside a code fence for a real image).
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
import markdown as markdown_library

from build_site import parse_front_matter
from import_blogger import is_blogger_media, normalize_asset_url


MEDIA_ATTRIBUTES = ("src", "data-src", "data-original-src")
MEDIA_ELEMENTS = ("img", "source", "video", "audio")


def rendered_media(markdown_source: str) -> set[str]:
    """Return absolute media URLs emitted by the site's Markdown renderer."""
    _, body = parse_front_matter(markdown_source)
    rendered = markdown_library.markdown(
        body,
        extensions=["extra", "sane_lists", "toc"],
        output_format="html5",
    )
    soup = BeautifulSoup(rendered, "html.parser")
    found: set[str] = set()
    for element in soup.find_all(MEDIA_ELEMENTS):
        for attribute in MEDIA_ATTRIBUTES:
            value = element.get(attribute)
            if value:
                normalized = normalize_asset_url(str(value))
                if normalized:
                    found.add(normalized)
        for item in str(element.get("srcset", "")).split(","):
            candidate = item.strip().split(None, 1)[0] if item.strip() else ""
            normalized = normalize_asset_url(candidate)
            if normalized:
                found.add(normalized)
    return found


def route_media(root: Path, only_route: str | None = None) -> dict[str, set[str]]:
    raw_posts = json.loads((root / "data" / "posts.json").read_text(encoding="utf-8"))["posts"]
    mapping: dict[str, set[str]] = defaultdict(set)
    for post in raw_posts:
        route = str(post["route"])
        if only_route and route != only_route:
            continue
        source = root / "content" / "posts" / str(post["content_file"])
        if not source.exists():
            raise RuntimeError(f"Missing Markdown source: {source}")
        for url in rendered_media(source.read_text(encoding="utf-8")):
            mapping[url].add(route)
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--route", help="Reconcile one canonical post route, e.g. 2026/04/post.html")
    parser.add_argument("--write", action="store_true", help="Persist additions instead of reporting them")
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_path = root / "data" / "media-manifest.json"
    manifest: list[dict[str, Any]] = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = {str(item["url"]): item for item in manifest}
    found = route_media(root, args.route)

    added = 0
    updated_routes = 0
    for url in sorted(found):
        routes = sorted(found[url])
        if url not in current:
            current[url] = {
                "url": url,
                "kind": "blogger" if is_blogger_media(url) else "external",
                "posts": routes,
                "local_path": None,
                "status": "pending",
                "discovered_from": "rendered_markdown",
            }
            added += 1
            continue
        item = current[url]
        merged_routes = sorted(set(str(route) for route in item.get("posts", [])) | set(routes))
        if merged_routes != item.get("posts", []):
            item["posts"] = merged_routes
            updated_routes += 1

    if args.write:
        # Retain original importer order and append only genuinely newly
        # discovered Markdown media in stable URL order.
        known = {str(item["url"]) for item in manifest}
        for item in manifest:
            item.update(current[str(item["url"])])
        manifest.extend(current[url] for url in sorted(found) if url not in known)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "route": args.route or "all",
                "rendered_media_urls": len(found),
                "new_manifest_entries": added,
                "updated_route_references": updated_routes,
                "written": args.write,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
