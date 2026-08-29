#!/usr/bin/env python3
"""Import every published post from a public Blogger site.

The Blogger JSON feed is paginated inconsistently for this blog, so the
importer follows the number of entries actually returned by each page rather
than assuming a fixed page size.  It also validates the result against the
public sitemap before writing editable Markdown source files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from bs4 import BeautifulSoup
from markdown_conversion import html_to_markdown


DEFAULT_BLOG = "https://x8795278.blogspot.com"
USER_AGENT = "Mozilla/5.0 (compatible; BlogMigration/1.0; +https://github.com/)"
MEDIA_HOST_SUFFIXES = (
    ".blogger.googleusercontent.com",
    ".bp.blogspot.com",
    ".googleusercontent.com",
)


def fetch_bytes(url: str, timeout: int = 60) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_json(url: str) -> dict[str, Any]:
    return json.loads(fetch_bytes(url).decode("utf-8"))


def canonical_url(entry: dict[str, Any]) -> str | None:
    for link in entry.get("link", []):
        if link.get("rel") == "alternate" and link.get("href"):
            return link["href"].split("?", 1)[0]
    return None


def text_value(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("$t", ""))
    return str(value or "")


def get_sitemap_urls(blog_url: str) -> list[str]:
    root = ElementTree.fromstring(fetch_bytes(f"{blog_url}/sitemap.xml"))
    urls: list[str] = []
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] == "loc" and element.text:
            urls.append(element.text.strip().split("?", 1)[0])
    return list(dict.fromkeys(urls))


def collect_feed_entries(blog_url: str) -> tuple[dict[str, dict[str, Any]], list[dict[str, int]]]:
    """Fetch all feed pages, advancing by actual returned entry counts."""
    entries_by_url: dict[str, dict[str, Any]] = {}
    pages: list[dict[str, int]] = []
    start = 1
    total: int | None = None
    seen_starts: set[int] = set()

    while start not in seen_starts:
        seen_starts.add(start)
        endpoint = f"{blog_url}/feeds/posts/default?alt=json&max-results=150&start-index={start}"
        payload = fetch_json(endpoint)
        feed = payload.get("feed", {})
        raw_entries = feed.get("entry", []) or []
        if isinstance(raw_entries, dict):
            raw_entries = [raw_entries]
        page_entries = [entry for entry in raw_entries if isinstance(entry, dict)]
        if total is None:
            total = int(text_value(feed.get("openSearch$totalResults")) or "0")

        for entry in page_entries:
            url = canonical_url(entry)
            if url:
                entries_by_url[url] = entry

        pages.append({"start_index": start, "entry_count": len(page_entries)})
        if not page_entries:
            break
        start += len(page_entries)
        if total is not None and start > total:
            break

    return entries_by_url, pages


def fallback_entry(url: str) -> dict[str, Any]:
    """Build a minimal entry only if Blogger's feed omits a sitemap URL."""
    soup = BeautifulSoup(fetch_bytes(url).decode("utf-8", "replace"), "html.parser")
    body = soup.select_one(".post-body")
    title = soup.select_one(".post-title") or soup.find("h1") or soup.find("title")
    labels = [item.get_text(" ", strip=True) for item in soup.select(".post-labels a")]
    date = ""
    published = soup.select_one("abbr.published")
    if published:
        date = published.get("title", "")
    return {
        "id": {"$t": f"fallback:{url}"},
        "published": {"$t": date or "1970-01-01T00:00:00+00:00"},
        "updated": {"$t": date or "1970-01-01T00:00:00+00:00"},
        "title": {"$t": title.get_text(" ", strip=True) if title else url},
        "content": {"$t": str(body) if body else ""},
        "category": [{"term": label} for label in labels],
        "link": [{"rel": "alternate", "href": url}],
    }


def normalize_asset_url(value: str) -> str | None:
    value = unescape(value).strip()
    if not value or value.startswith(("data:", "#", "javascript:")):
        return None
    if value.startswith("//"):
        value = f"https:{value}"
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        return None
    return value


def is_blogger_media(url: str) -> bool:
    hostname = (urlparse(url).hostname or "").lower()
    return hostname == "blogger.googleusercontent.com" or hostname.endswith(MEDIA_HOST_SUFFIXES)


def find_media_urls(html: str) -> Iterable[str]:
    soup = BeautifulSoup(html, "html.parser")
    for element in soup.find_all(["img", "source", "video", "audio"]):
        for attribute in ("src", "data-src", "data-original-src"):
            if element.get(attribute):
                url = normalize_asset_url(str(element[attribute]))
                if url:
                    yield url
        if element.get("srcset"):
            for source in str(element["srcset"]).split(","):
                url = normalize_asset_url(source.strip().split(" ", 1)[0])
                if url:
                    yield url

    for element in soup.find_all(style=True):
        for value in re.findall(r"url\((?:['\"])?([^'\")]+)", str(element["style"])):
            url = normalize_asset_url(value)
            if url:
                yield url


def route_from_url(url: str) -> str:
    route = urlparse(url).path.strip("/")
    if not route or not route.endswith(".html"):
        raise ValueError(f"Unexpected Blogger post URL: {url}")
    return route


def content_filename(url: str, blogger_id: str) -> str:
    route = route_from_url(url)
    path = Path(route)
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "-", path.stem).strip("-.") or "post"
    path_bits = path.parts[:2]
    prefix = "-".join(path_bits) if len(path_bits) == 2 else "post"
    checksum = hashlib.sha256(blogger_id.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}-{safe_stem}-{checksum}.md"


def yaml_string(value: str) -> str:
    # JSON strings are legal YAML scalars and safely preserve Chinese/quotes.
    return json.dumps(value, ensure_ascii=False)


def render_markdown(post: dict[str, Any]) -> str:
    front_matter = [
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
    return "\n".join(front_matter)


def transform_entry(entry: dict[str, Any]) -> dict[str, Any]:
    url = canonical_url(entry)
    if not url:
        raise ValueError("Entry lacks a canonical URL")
    blogger_id = text_value(entry.get("id"))
    tags = [text_value(category.get("term")) for category in entry.get("category", []) if text_value(category.get("term"))]
    author = ""
    authors = entry.get("author", [])
    if authors:
        author = text_value(authors[0].get("name"))
    return {
        "blogger_id": blogger_id,
        "url": url,
        "route": route_from_url(url),
        "title": text_value(entry.get("title")) or Path(route_from_url(url)).stem,
        "published": text_value(entry.get("published")),
        "updated": text_value(entry.get("updated")) or text_value(entry.get("published")),
        "author": author,
        "tags": list(dict.fromkeys(tags)),
        "content": text_value(entry.get("content")) or text_value(entry.get("summary")),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blog-url", default=DEFAULT_BLOG)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--refresh", action="store_true", help="replace prior imported content")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    blog_url = args.blog_url.rstrip("/")
    posts_dir = root / "content" / "posts"
    data_dir = root / "data"
    source_dir = root / "source" / "blogger"

    if args.refresh:
        shutil.rmtree(posts_dir, ignore_errors=True)
    posts_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    source_dir.mkdir(parents=True, exist_ok=True)

    sitemap_urls = get_sitemap_urls(blog_url)
    feed_entries, feed_pages = collect_feed_entries(blog_url)
    missing = [url for url in sitemap_urls if url not in feed_entries]
    for url in missing:
        print(f"Feed omitted {url}; retrieving article page directly.", file=sys.stderr)
        feed_entries[url] = fallback_entry(url)

    unexpected = sorted(set(feed_entries) - set(sitemap_urls))
    posts = [transform_entry(feed_entries[url]) for url in sitemap_urls if url in feed_entries]
    posts.sort(key=lambda post: (post["published"], post["url"]), reverse=True)

    if len(posts) != len(sitemap_urls):
        raise RuntimeError(f"Import incomplete: sitemap has {len(sitemap_urls)} URLs but only {len(posts)} posts were collected")

    media: dict[str, dict[str, Any]] = {}
    for post in posts:
        post["content_file"] = content_filename(post["url"], post["blogger_id"])
        (posts_dir / post["content_file"]).write_text(render_markdown(post), encoding="utf-8")
        for asset_url in find_media_urls(post["content"]):
            record = media.setdefault(
                asset_url,
                {
                    "url": asset_url,
                    "kind": "blogger" if is_blogger_media(asset_url) else "external",
                    "posts": [],
                    "local_path": None,
                    # The downloader attempts every image/media URL.  Failed or
                    # oversized assets deliberately keep their original URL so a
                    # published page never loses content silently.
                    "status": "pending",
                },
            )
            record["posts"].append(post["route"])

    tag_counts = Counter(tag for post in posts for tag in post["tags"])
    posts_payload = {
        "schema_version": 1,
        "blog_url": blog_url,
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "posts": posts,
    }
    report = {
        "blog_url": blog_url,
        "sitemap_post_count": len(sitemap_urls),
        "imported_post_count": len(posts),
        "feed_pages": feed_pages,
        "feed_omitted_sitemap_urls": missing,
        "unexpected_feed_urls": unexpected,
        "empty_content_posts": [post["route"] for post in posts if not post["content"].strip()],
        "tag_count": len(tag_counts),
        "tag_counts": dict(sorted(tag_counts.items(), key=lambda pair: (-pair[1], pair[0].casefold()))),
        "media": {
            "unique_urls": len(media),
            "blogger_hosted": sum(item["kind"] == "blogger" for item in media.values()),
            "external": sum(item["kind"] == "external" for item in media.values()),
        },
    }

    (source_dir / "sitemap.xml").write_bytes(fetch_bytes(f"{blog_url}/sitemap.xml"))
    (data_dir / "posts.json").write_text(json.dumps(posts_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (data_dir / "media-manifest.json").write_text(json.dumps(list(media.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (data_dir / "migration-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"posts": len(posts), "tags": len(tag_counts), "media": report["media"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
