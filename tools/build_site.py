#!/usr/bin/env python3
"""Build the imported Blogger archive as a dependency-free GitHub Pages site."""

from __future__ import annotations

import argparse
import calendar
import html
import json
import posixpath
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from xml.sax.saxutils import escape as xml_escape

from bs4 import BeautifulSoup
import markdown as markdown_library

from markdown_hackmd import HackMDExtension


DEFAULT_CONFIG = {
    "title": "Coding の ORZ",
    "description": "Technical notes on systems, software engineering, and reverse engineering.",
    "site_url": "https://x213212.github.io",
    "github_url": "https://github.com/x213212",
    "source_blog_url": "https://x8795278.blogspot.com",
    "per_page": 18,
    "rss": {
        "legacy_feedburner_url": "http://feeds.feedburner.com/blogspot/aHycb",
    },
    "analytics": {
        "ga4_measurement_id": "",
    },
    "media": {
        "use_local_mirror": False,
        # ``original`` publishes the untouched download cache.  ``optimized``
        # publishes only the separately generated WebP-oriented mirror from
        # tools/optimize_media.py, falling back to public URLs for any item the
        # optimizer intentionally skipped.
        "variant": "original",
    },
    "giscus": {
        "repo": "x213212/x213212.github.io",
        "repo_id": "",
        "category": "Announcements",
        "category_id": "",
        "mapping": "pathname",
        "strict": "0",
        "reactions_enabled": "1",
        "emit_metadata": "0",
        "input_position": "bottom",
        "theme": "dark",
        "lang": "zh-TW",
    },
    "profile": {
        "name": "CODING の ORZ",
        "photo_path": "assets/profile.jpg",
        "email": "x8795278@gmail.com",
        "website": "https://x213212.github.io/",
        "blogger_profile_url": "https://www.blogger.com/profile/06205957841262607002",
        "joined": "June 2018",
        "profile_views": "306",
        "gender": "Male",
        "industry": "Internet",
        "introduction": "Technical exchanges can be sent to my",
    },
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def optimized_media_mapping(root: Path) -> dict[str, str]:
    """Read the separate optimizer report without modifying the raw manifest.

    The report is only accepted after a real ``--write`` run and every mapped
    target must exist under ``site/assets/media-optimized``.  That makes a
    partial optimization safe: assets not in the report remain remote instead
    of producing a broken local URL or accidentally publishing the 1 GB cache.
    """
    report_path = root / "data" / "media-optimization-report.json"
    if not report_path.exists():
        raise RuntimeError(
            "Optimized media was selected but data/media-optimization-report.json is missing. "
            "Run: python3 tools/optimize_media.py --write"
        )
    report = load_json(report_path)
    if report.get("mode") != "write":
        raise RuntimeError(
            "Optimized media was selected but the report is only a dry run. "
            "Run: python3 tools/optimize_media.py --write"
        )
    media: dict[str, str] = {}
    for item in report.get("items", []):
        if item.get("status") not in {"optimized", "copied"}:
            continue
        url = str(item.get("url", "")).strip()
        local_path = str(item.get("optimized_local_path", "")).strip()
        if not url or not local_path:
            continue
        candidate = Path(local_path)
        if candidate.is_absolute() or ".." in candidate.parts or candidate.parts[:2] != ("assets", "media-optimized"):
            continue
        if (root / "site" / candidate).is_file():
            media[url] = candidate.as_posix()
    if not media:
        raise RuntimeError(
            "Optimized media was selected but the report has no usable output files. "
            "Run the optimizer again without --limit."
        )
    return media


def optimized_media_dimensions(root: Path) -> dict[str, tuple[int, int]]:
    """Intrinsic size of every optimized asset, keyed by original URL.

    Giving each ``<img>`` a width and height lets the browser reserve the right
    box before the file arrives, which removes the layout shift that lazy-loaded
    article images would otherwise cause.
    """
    report_path = root / "data" / "media-optimization-report.json"
    if not report_path.exists():
        return {}
    dimensions: dict[str, tuple[int, int]] = {}
    for item in load_json(report_path).get("items", []):
        url = str(item.get("url", "")).strip()
        width = item.get("output_width") or item.get("source_width")
        height = item.get("output_height") or item.get("source_height")
        if url and isinstance(width, int) and isinstance(height, int) and width > 0 and height > 0:
            dimensions[url] = (width, height)
    return dimensions


def optimized_thumbnail_mapping(root: Path) -> dict[str, tuple[str, str]]:
    """Load small deterministic card thumbnails for the self-hosted mirror.

    The report is route keyed, so a post card never has to download its full
    in-article image just to show a preview. Only generated thumbnail paths
    are accepted, even if someone edits the report by hand.
    """
    report_path = root / "data" / "media-thumbnail-report.json"
    if not report_path.exists():
        return {}
    report = load_json(report_path)
    if report.get("mode") != "write":
        return {}
    thumbnails: dict[str, tuple[str, str]] = {}
    for item in report.get("items", []):
        if item.get("status") != "ready":
            continue
        route = str(item.get("route", "")).strip()
        local_path = str(item.get("thumbnail_local_path", "")).strip()
        alt = str(item.get("thumbnail_alt", "")).strip()
        candidate = Path(local_path)
        if (
            not route
            or not local_path
            or candidate.is_absolute()
            or ".." in candidate.parts
            or candidate.parts[:2] != ("assets", "media-thumbnails")
            or not (root / "site" / candidate).is_file()
        ):
            continue
        thumbnails[route] = (candidate.as_posix(), alt)
    return thumbnails


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_config(root: Path) -> dict[str, Any]:
    path = root / "data" / "site-config.json"
    config = dict(DEFAULT_CONFIG)
    if path.exists():
        saved = load_json(path)
        config.update(saved)
        for key, default in DEFAULT_CONFIG.items():
            if isinstance(default, dict):
                merged = dict(default)
                merged.update(saved.get(key, {}) if isinstance(saved.get(key), dict) else {})
                config[key] = merged
        if config != saved:
            save_json(path, config)
    else:
        save_json(path, config)
    config["site_url"] = str(config["site_url"]).rstrip("/")
    config["per_page"] = max(1, int(config["per_page"]))
    return config


def parse_front_matter(source: str) -> tuple[dict[str, Any], str]:
    """Parse the intentionally JSON-compatible front matter written by import_blogger."""
    if not source.startswith("---\n"):
        return {}, source
    marker = source.find("\n---\n", 4)
    if marker == -1:
        return {}, source
    metadata: dict[str, Any] = {}
    for line in source[4:marker].splitlines():
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        raw_value = raw_value.strip()
        try:
            metadata[key.strip()] = json.loads(raw_value)
        except json.JSONDecodeError:
            metadata[key.strip()] = raw_value
    return metadata, source[marker + 5 :].lstrip("\n")


def front_matter_bool(value: Any) -> bool:
    """Interpret the small boolean surface used by editable post sources."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().casefold() in {"1", "true", "yes", "on", "draft"}


def front_matter_tags(value: Any) -> list[str]:
    """Keep tags predictable for hand-authored posts as well as imported ones."""
    if isinstance(value, list):
        return list(dict.fromkeys(str(tag).strip() for tag in value if str(tag).strip()))
    if isinstance(value, str):
        return list(dict.fromkeys(tag.strip() for tag in value.split(",") if tag.strip()))
    return []


def load_tag_aliases(root: Path) -> dict[str, str]:
    """Read the small, reviewable label normalisation table."""
    path = root / "data" / "tag-normalization.json"
    if not path.exists():
        return {}
    payload = load_json(path)
    aliases = payload.get("aliases", {}) if isinstance(payload, dict) else {}
    if not isinstance(aliases, dict):
        return {}
    return {
        str(source).strip().casefold(): str(target).strip()
        for source, target in aliases.items()
        if str(source).strip() and str(target).strip()
    }


def normalize_tag(tag: Any, aliases: dict[str, str]) -> str:
    """Return a canonical label while guarding against accidental alias loops."""
    current = str(tag).strip()
    seen: set[str] = set()
    while current.casefold() in aliases and current.casefold() not in seen:
        seen.add(current.casefold())
        current = aliases[current.casefold()]
    return current


def normalize_tags(tags: list[str], aliases: dict[str, str]) -> list[str]:
    normalized: list[str] = []
    for tag in tags:
        canonical = normalize_tag(tag, aliases)
        if canonical and canonical not in normalized:
            normalized.append(canonical)
    return normalized


def load_editable_posts(root: Path) -> list[dict[str, Any]]:
    """Load imported Markdown and local hand-authored Markdown posts.

    When the raw Blogger export is present, imported posts keep their immutable
    metadata from it. Any file the export does not cover - a locally written
    post, or every post when the export is not shipped - is wholly defined by its
    JSON-compatible front matter, which is what the import wrote there anyway.
    """
    # ``content/posts/*.md`` is the source of truth: every imported post carries
    # its Blogger metadata in front matter. The raw export is optional, so a
    # published repository can ship the articles without the 6 MB import record.
    import_record = root / "data" / "posts.json"
    payload = load_json(import_record) if import_record.is_file() else {"posts": []}
    tag_aliases = load_tag_aliases(root)
    posts: list[dict[str, Any]] = []
    content_directory = root / "content" / "posts"
    known_files: set[str] = set()
    for original in payload["posts"]:
        post = dict(original)
        source_path = content_directory / post["content_file"]
        if not source_path.exists():
            raise RuntimeError(f"Missing editable post source: {source_path}")
        metadata, body = parse_front_matter(source_path.read_text(encoding="utf-8"))
        post["content"] = body
        post["draft"] = front_matter_bool(metadata.get("draft", False))
        for key in ("title", "date", "updated", "tags", "blogger_id", "original_url"):
            if key not in metadata:
                continue
            target = {"date": "published", "original_url": "url"}.get(key, key)
            post[target] = front_matter_tags(metadata[key]) if key == "tags" else metadata[key]
        if "permalink" in metadata:
            post["route"] = str(metadata["permalink"]).lstrip("/")
        post["tags"] = normalize_tags(front_matter_tags(post.get("tags", [])), tag_aliases)
        posts.append(post)
        known_files.add(source_path.name)

    # Locally created Markdown posts are deliberately not added to the raw
    # Blogger export.  They remain normal editable files and must contain the
    # same small front-matter contract the local editor writes.
    for source_path in sorted(content_directory.glob("*.md")):
        if source_path.name in known_files:
            continue
        metadata, body = parse_front_matter(source_path.read_text(encoding="utf-8"))
        required = [key for key in ("title", "date", "permalink") if not metadata.get(key)]
        if required:
            joined = ", ".join(required)
            raise RuntimeError(f"Local Markdown post {source_path.name} is missing required front matter: {joined}")
        route = str(metadata["permalink"]).lstrip("/")
        posts.append(
            {
                "title": str(metadata["title"]),
                "published": str(metadata["date"]),
                "updated": str(metadata.get("updated") or metadata["date"]),
                "url": str(metadata.get("original_url", "")),
                "route": route,
                "tags": normalize_tags(front_matter_tags(metadata.get("tags", [])), tag_aliases),
                "content": body,
                "content_file": source_path.name,
                "draft": front_matter_bool(metadata.get("draft", False)),
                "local_post": True,
            }
        )
    # Treat case-only differences as the same label across every imported and
    # future local post. Explicit aliases above decide the preferred spelling;
    # otherwise the first existing canonical spelling is kept consistently.
    canonical_by_case: dict[str, str] = {}
    for post in posts:
        for tag in post.get("tags", []):
            canonical_by_case.setdefault(str(tag).casefold(), str(tag))
    for post in posts:
        post["tags"] = list(
            dict.fromkeys(canonical_by_case[str(tag).casefold()] for tag in post.get("tags", []) if str(tag).casefold() in canonical_by_case)
        )
    return posts


def attach_categories(
    root: Path, posts: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Attach display-only English topics without modifying Markdown or raw tags.

    The curated tag taxonomy is authoritative when present: every one of the
    original Blogger labels maps to a maintained English topic.  The older
    route classifier remains a safe fallback for a future partial import.
    """
    taxonomy_path = root / "data" / "tag-taxonomy.json"
    if taxonomy_path.exists():
        taxonomy = load_json(taxonomy_path)
        topics = {str(topic["id"]): topic for topic in taxonomy.get("topics", [])}
        aliases = load_tag_aliases(root)
        tag_to_topic = {
            normalize_tag(tag, aliases): str(topic_id)
            for tag, topic_id in taxonomy.get("tag_to_topic", {}).items()
        }
        ordered_ids = [str(topic_id) for topic_id in taxonomy.get("topic_order", []) if str(topic_id) in topics]
        if topics and tag_to_topic and ordered_ids:
            cloud_order = [
                str(topics[topic_id]["label"])
                for topic_id in ordered_ids
                if topics[topic_id].get("show_in_word_cloud", True)
            ]
            overrides_path = root / "data" / "topic-route-overrides.json"
            overrides_source = load_json(overrides_path) if overrides_path.exists() else {}
            route_overrides = overrides_source.get("overrides", overrides_source)
            if not isinstance(route_overrides, dict):
                route_overrides = {}
            for post in posts:
                ids = list(
                    dict.fromkeys(
                        tag_to_topic[tag]
                        for tag in post.get("tags", [])
                        if tag in tag_to_topic and tag_to_topic[tag] in topics
                    )
                )
                extra_ids = route_overrides.get(post["route"], [])
                if isinstance(extra_ids, list):
                    ids = list(dict.fromkeys([*ids, *(str(topic_id) for topic_id in extra_ids if str(topic_id) in topics)]))
                visible_ids = [topic_id for topic_id in ids if topics[topic_id].get("show_in_word_cloud", True)]
                post["categories"] = [str(topics[topic_id]["label"]) for topic_id in visible_ids] or ["General Technical Notes"]
            category_order = [*cloud_order, "General Technical Notes"]
            return posts, category_order, cloud_order

    path = root / "data" / "categories.json"
    if not path.exists():
        for post in posts:
            post["categories"] = ["General Technical Notes"]
        return posts, ["General Technical Notes"], ["General Technical Notes"]
    data = load_json(path)
    assignments = data.get("assignments", {})
    for post in posts:
        post["categories"] = assignments.get(post["route"], ["General Technical Notes"])
    known = {category for post in posts for category in post["categories"]}
    order = [category for category in data.get("category_order", []) if category in known]
    order.extend(sorted(known - set(order), key=str.casefold))
    return posts, order, order


def output_relative_link(current: str, target: str) -> str:
    current_dir = posixpath.dirname(current) or "."
    return posixpath.relpath(target, start=current_dir)


def absolute_url(config: dict[str, Any], output_path: str) -> str:
    pretty_path = output_path
    if pretty_path == "index.html":
        pretty_path = ""
    elif pretty_path.endswith("/index.html"):
        pretty_path = pretty_path[: -len("index.html")]
    return f"{config['site_url']}/{pretty_path}".replace("//", "/").replace("https:/", "https://")


def iso_date(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)


def display_date(value: str) -> str:
    return iso_date(value).strftime("%Y-%m-%d")


def tag_slug(tag: str) -> str:
    ascii_part = re.sub(r"[^a-z0-9]+", "-", tag.casefold()).strip("-")[:36]
    checksum = __import__("hashlib").sha256(tag.encode("utf-8")).hexdigest()[:8]
    return f"{ascii_part or 'tag'}-{checksum}"


def post_text(post: dict[str, Any], limit: int = 190) -> str:
    text = BeautifulSoup(post.get("rendered_content", post["content"]), "html.parser").get_text(" ", strip=True)
    return text if len(text) <= limit else f"{text[:limit].rstrip()}…"


def is_internal_blogger_link(value: str, blog_host: str) -> tuple[str, str] | None:
    parsed = urlsplit(value)
    host = (parsed.hostname or "").lower()
    path = parsed.path.strip("/")
    if not host and path.startswith(tuple(str(year) for year in range(2000, 2100))):
        return path, parsed.fragment
    if host == blog_host or host.endswith(".blogspot.com"):
        return path, parsed.fragment
    return None


def replace_srcset(value: str, replace) -> str:
    parts: list[str] = []
    for source in value.split(","):
        bits = source.strip().split(None, 1)
        if not bits:
            continue
        rewritten = replace(bits[0])
        parts.append(" ".join([rewritten] + bits[1:]))
    return ", ".join(parts)


def rewrite_article_html(
    post: dict[str, Any],
    current_output: str,
    routes: set[str],
    media: dict[str, str],
    blog_host: str,
    dimensions: dict[str, tuple[int, int]] | None = None,
) -> str:
    """Rewrite local media and old Blogspot links while retaining article HTML."""
    soup = BeautifulSoup(post.get("rendered_content", post["content"]), "html.parser")

    # Old Blogger posts include active script/style snippets.  Preserve their
    # source as code, but never allow historic embeds to change the new site.
    for active in soup.find_all(["script", "style"]):
        source = str(active)
        pre = soup.new_tag("pre", attrs={"class": "legacy-code"})
        code = soup.new_tag("code")
        code.string = source
        pre.append(code)
        active.replace_with(pre)

    def replace(value: str) -> str:
        if value in media:
            return output_relative_link(current_output, media[value])
        internal = is_internal_blogger_link(value, blog_host)
        if internal:
            target_path, fragment = internal
            if target_path in routes:
                result = output_relative_link(current_output, target_path)
                return f"{result}#{fragment}" if fragment else result
        return value

    original_sources: dict[int, str] = {}
    for element in soup.find_all("img", src=True):
        original_sources[id(element)] = str(element["src"]).strip()

    for element in soup.find_all(True):
        for attribute in ("src", "href", "poster", "data-src", "data-original-src"):
            if element.get(attribute):
                element[attribute] = replace(str(element[attribute]))
        if element.get("srcset"):
            element["srcset"] = replace_srcset(str(element["srcset"]), replace)
        if element.name == "img":
            element["loading"] = element.get("loading", "lazy")
            element["decoding"] = element.get("decoding", "async")
            size = (dimensions or {}).get(original_sources.get(id(element), ""))
            if size and not element.get("width") and not element.get("height"):
                element["width"], element["height"] = str(size[0]), str(size[1])
        if element.get("style"):
            element["style"] = re.sub(
                r"url\((['\"]?)([^)'\"]+)\1\)",
                lambda match: f"url({match.group(1)}{replace(match.group(2))}{match.group(1)})",
                str(element["style"]),
            )
    return str(soup)


def nav(config: dict[str, Any], current: str) -> str:
    links = [
        ("Posts", "index.html"),
        ("Topics", "categories/index.html"),
        ("Archive", "archive/index.html"),
        ("Search", "search/index.html"),
        ("RSS", "feed.xml"),
        ("About", "about/index.html"),
    ]
    items = "".join(
        f'<a href="{html.escape(output_relative_link(current, target), quote=True)}">{label}</a>' for label, target in links
    )
    home_url = output_relative_link(current, "index.html")
    icon_url = output_relative_link(current, "assets/original-blogger-icon.png")
    return f'''<header class="site-header">
  <div class="site-header__inner">
    <a class="brand" href="{html.escape(home_url, quote=True)}" aria-label="{html.escape(str(config['title']), quote=True)} homepage">
      <img class="brand__icon" src="{html.escape(icon_url, quote=True)}" width="16" height="16" alt="">
      <span>Coding <span lang="ja">の</span> ORZ</span>
    </a>
    <nav class="site-nav" id="site-navigation" aria-label="Primary navigation">{items}</nav>
    <button class="theme-toggle" type="button" data-theme-toggle aria-label="Switch to light mode" title="Switch to light mode"><span aria-hidden="true" data-theme-icon>☼</span><span data-theme-label>Light</span></button>
    <button class="menu-toggle" type="button" data-sidebar-toggle aria-controls="site-sidebar" aria-expanded="false" aria-label="Open sidebar" title="Open sidebar"><span aria-hidden="true">☰</span></button>
    <a class="github-link" href="{html.escape(str(config['github_url']), quote=True)}" target="_blank" rel="noopener" aria-label="GitHub profile" title="GitHub">
      <svg class="github-link__mark" viewBox="0 0 16 16" width="18" height="18" aria-hidden="true" focusable="false"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg>
      <span class="github-link__text">GitHub ↗</span>
    </a>
  </div>
</header>'''


def analytics_embed(config: dict[str, Any]) -> str:
    measurement_id = str(config.get("analytics", {}).get("ga4_measurement_id", "")).strip()
    if not re.fullmatch(r"G-[A-Z0-9]+", measurement_id):
        return ""
    safe_id = html.escape(measurement_id, quote=True)
    return f'''  <!-- Google Analytics 4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={safe_id}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{safe_id}');</script>'''


def goatcounter_embed(config: dict[str, Any]) -> str:
    """Load the GoatCounter tracker when a site code is configured.

    GA4 cannot show its own numbers on a static page - its Data API needs a
    credential that would have to be published. GoatCounter exposes a public
    counter endpoint instead, so the visitor count can be rendered client-side.
    """
    code = str(config.get("analytics", {}).get("goatcounter_code", "")).strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", code):
        return ""
    safe = html.escape(code, quote=True)
    return (
        f'  <script data-goatcounter="https://{safe}.goatcounter.com/count"'
        '\n          async src="//gc.zgo.at/count.js"></script>'
    )


def visitor_counter(config: dict[str, Any]) -> str:
    """The footer counter: a live count plus the archive's Blogger total.

    The two numbers come from different systems measuring different periods, so
    they are shown side by side rather than added together. The legacy figure is
    rendered here rather than fetched, so it survives without JavaScript.
    """
    analytics = config.get("analytics", {})
    code = str(analytics.get("goatcounter_code", "")).strip()
    legacy = analytics.get("legacy_pageviews")
    legacy_source = str(analytics.get("legacy_source", "")).strip()

    parts: list[str] = []
    live = bool(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", code))
    if live:
        parts.append('<span data-visitor-total hidden></span>')
    if isinstance(legacy, int) and legacy > 0:
        label = f"{legacy:,} views on {legacy_source}" if legacy_source else f"{legacy:,} views"
        parts.append(f'<span class="visitor-count__legacy">{html.escape(label)}</span>')
    if not parts:
        return ""

    attribute = f' data-visitor-count="{html.escape(code, quote=True)}"' if live else ""
    return f'<div class="visitor-count"{attribute}>{"".join(parts)}</div>'


FENCE_WITH_LANG = re.compile(r"(?m)^[ ]{0,3}(?P<fence>`{3,}|~{3,})[ \t]*(?P<lang>[\w#.+-]+)[ \t]*$")


def fenced_languages(markdown_source: str) -> list[str]:
    """Languages of the fenced blocks, in document order, ignoring block bodies."""
    languages: list[str] = []
    fence: str | None = None
    for line in markdown_source.split("\n"):
        marker = re.match(r"^[ ]{0,3}(`{3,}|~{3,})", line)
        if not marker:
            continue
        if fence is None:
            fence = marker.group(1)
            declared = FENCE_WITH_LANG.match(line)
            if declared and declared.group("fence") == fence:
                languages.append(declared.group("lang"))
        elif marker.group(1) == fence:
            fence = None
    return languages


def render_markdown(source: str) -> str:
    """The single Markdown pipeline: extras, HackMD syntax, highlighting, chrome."""
    rendered = markdown_library.markdown(
        source,
        extensions=["extra", "sane_lists", "toc", "codehilite", HackMDExtension()],
        extension_configs={
            # Only highlight blocks that declared a language; guessing mislabels
            # the many shell and log dumps in the archive.
            "codehilite": {"guess_lang": False, "css_class": "highlight"}
        },
        output_format="html5",
    )
    return decorate_code_blocks(rendered, source)


def decorate_code_blocks(rendered: str, markdown_source: str) -> str:
    """Give every code block a caption with its language and a copy button.

    Building the chrome here rather than in the browser keeps the language label
    available without JavaScript and avoids a layout shift on load.
    """
    soup = BeautifulSoup(rendered, "html.parser")
    highlighted = soup.select("div.highlight")
    languages = fenced_languages(markdown_source)
    if len(languages) != len(highlighted):
        languages = []
    for index, block in enumerate(highlighted):
        language = languages[index] if languages else ""
        figure = soup.new_tag("figure", attrs={"class": "code-block"})
        caption = soup.new_tag("figcaption", attrs={"class": "code-block__bar"})
        label = soup.new_tag("span", attrs={"class": "code-block__lang"})
        label.string = language or "code"
        button = soup.new_tag(
            "button",
            attrs={"class": "code-block__copy", "type": "button", "data-copy": "true"},
        )
        button.string = "Copy"
        caption.append(label)
        caption.append(button)
        block.wrap(figure)
        figure.insert(0, caption)
    return str(soup)


def page_shell(
    config: dict[str, Any],
    current: str,
    title: str,
    description: str,
    body: str,
    noindex: bool = False,
) -> str:
    css_url = output_relative_link(current, "assets/site.css")
    js_url = output_relative_link(current, "assets/site.js")
    favicon_url = output_relative_link(current, "assets/original-blogger-icon.png")
    canonical = absolute_url(config, current)
    return f'''<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(description, quote=True)}">
  <meta name="color-scheme" content="dark light">
{'  <meta name="robots" content="noindex, nofollow">' + chr(10) if noindex else ''}
  <link rel="canonical" href="{html.escape(canonical, quote=True)}">
  <link rel="icon" type="image/png" href="{html.escape(favicon_url, quote=True)}">
  <script>try{{document.documentElement.dataset.theme=localStorage.getItem('coding-orz-theme')||'dark'}}catch(_e){{document.documentElement.dataset.theme='dark'}}</script>
  <link rel="stylesheet" href="{html.escape(css_url, quote=True)}">
{analytics_embed(config)}
{goatcounter_embed(config)}
  <title>{(html.escape(title) + " · ") if title else ""}{html.escape(str(config['title']))}</title>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  {nav(config, current)}
  <main id="main" class="site-main">{body}</main>
  <button class="sidebar-scrim" type="button" data-sidebar-scrim aria-label="Close sidebar" tabindex="-1"></button>
  <footer class="site-footer">
    <div>© {datetime.now().year} {html.escape(str(config['title']))} · <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.zh-Hant" target="_blank" rel="license noopener">CC BY-SA 4.0</a></div>
    <div>Legacy theme image by <a href="https://www.istockphoto.com/portfolio/AndrzejStajer" target="_blank" rel="noopener">AndrzejStajer</a> · Static archive</div>
  </footer>
  <script src="{html.escape(js_url, quote=True)}" defer></script>
</body>
</html>
'''


def tag_links(post: dict[str, Any], current: str, tag_paths: dict[str, str]) -> str:
    if not post["tags"]:
        return ""
    tags = "".join(
        f'<a class="tag" href="{html.escape(output_relative_link(current, tag_paths[tag]), quote=True)}">#{html.escape(tag)}</a>'
        for tag in post["tags"]
    )
    return f'<div class="post-tags" aria-label="Original Blogger labels">{tags}</div>'


def legacy_tag_details(post: dict[str, Any], current: str, tag_paths: dict[str, str]) -> str:
    if not post["tags"]:
        return ""
    return f'''<details class="legacy-tags">
  <summary>Original Blogger labels · {len(post["tags"])}</summary>
  {tag_links(post, current, tag_paths)}
</details>'''


def category_links(post: dict[str, Any], current: str, category_paths: dict[str, str]) -> str:
    categories = [category for category in post.get("categories", []) if category in category_paths]
    if not categories:
        return ""
    links = "".join(
        f'<a class="category" href="{html.escape(output_relative_link(current, category_paths[category]), quote=True)}">{html.escape(category)}</a>'
        for category in categories
    )
    return f'<div class="post-categories" aria-label="Categories">{links}</div>'


def category_counts(posts: list[dict[str, Any]]) -> Counter[str]:
    return Counter(category for post in posts for category in post.get("categories", []))


def topic_cloud(
    posts: list[dict[str, Any]],
    current: str,
    category_paths: dict[str, str],
    category_order: list[str],
) -> str:
    """Render the curated categories as a compact, weighted discovery cloud."""
    counts = category_counts(posts)
    categories = [category for category in category_order if counts.get(category)]
    if not categories:
        return ""
    lowest = min(counts[category] for category in categories)
    highest = max(counts[category] for category in categories)
    spread = max(1, highest - lowest)
    items = []
    for category in categories:
        weight = 0.18 + 0.82 * (counts[category] - lowest) / spread
        size = 0.78 + 0.40 * weight
        href = output_relative_link(current, category_paths[category])
        items.append(
            f'<a class="topic-cloud__topic" title="{html.escape(category, quote=True)}" style="--topic-weight: {weight:.3f}; font-size: {size:.3f}rem" '
            f'href="{html.escape(href, quote=True)}">{html.escape(category)} '
            f'<span>{counts[category]}</span></a>'
        )
    return '<div class="topic-cloud" aria-label="Topics">' + "".join(items) + "</div>"


def label_cloud(posts: list[dict[str, Any]], current: str) -> str:
    """Keep the Blogger-style raw label cloud visible in the sidebar."""
    counts = Counter(tag for post in posts for tag in post["tags"])
    if not counts:
        return ""
    lowest = min(counts.values())
    highest = max(counts.values())
    spread = max(1, highest - lowest)
    items: list[str] = []
    for tag in sorted(counts, key=str.casefold):
        weight = .72 + .34 * (counts[tag] - lowest) / spread
        href = output_relative_link(current, f"tags/{tag_slug(tag)}.html")
        items.append(
            f'<a title="{html.escape(tag, quote=True)}" style="font-size: {weight:.3f}rem" '
            f'href="{html.escape(href, quote=True)}">{html.escape(tag)} <span class="label-cloud__count">{counts[tag]}</span></a>'
        )
    return '<div class="label-cloud" aria-label="Original Blogger labels">' + " ".join(items) + "</div>"


def year_cloud(posts: list[dict[str, Any]], current: str) -> str:
    """Link each publication year to the title-based archive section."""
    counts = Counter(display_date(post["published"])[:4] for post in posts)
    if not counts:
        return ""
    archive = output_relative_link(current, "archive/index.html")
    items = "".join(
        f'<a class="year-cloud__year" href="{html.escape(archive + "#year-" + year, quote=True)}">'
        f'{html.escape(year)} <span>{counts[year]}</span></a>'
        for year in sorted(counts, reverse=True)
    )
    return '<div class="year-cloud" aria-label="Posts by year">' + items + "</div>"


def year_archive_tree(posts: list[dict[str, Any]], current: str) -> str:
    """Render a compact classic archive: year → month → dated post title."""
    grouped: dict[str, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for post in posts:
        published = iso_date(post["published"])
        grouped[str(published.year)][published.month].append(post)
    sections: list[str] = []
    for year_position, year in enumerate(sorted(grouped, reverse=True)):
        months: list[str] = []
        for month_position, month in enumerate(sorted(grouped[year], reverse=True)):
            entries = "".join(
                f'<li><time datetime="{html.escape(post["published"], quote=True)}">{display_date(post["published"])[5:]}</time>'
                f'<a href="{html.escape(output_relative_link(current, post["route"]), quote=True)}">{html.escape(post["title"])}</a></li>'
                for post in grouped[year][month]
            )
            month_open = " open" if year_position == 0 and month_position == 0 else ""
            months.append(
                f'<details class="archive-tree__month"{month_open}><summary><span>{calendar.month_name[month]}</span>'
                f'<small>{len(grouped[year][month])}</small></summary><ul>{entries}</ul></details>'
            )
        count = sum(len(items) for items in grouped[year].values())
        year_open = " open" if year_position == 0 else ""
        sections.append(
            f'<details class="archive-tree__year"{year_open}><summary><span>{html.escape(year)}</span>'
            f'<small>{count}</small></summary>{"".join(months)}</details>'
        )
    return '<div class="archive-tree" id="archive-tree" aria-label="Posts by year">' + "".join(sections) + "</div>"


def site_sidebar(
    config: dict[str, Any],
    posts: list[dict[str, Any]],
    current: str,
    category_paths: dict[str, str],
    cloud_category_order: list[str],
) -> str:
    search_url = output_relative_link(current, "search/index.html")
    license_badge_url = output_relative_link(current, "assets/cc-by-sa-4.0.png")
    profile = config.get("profile", {})
    profile_name = html.escape(str(profile.get("name", config["title"])))
    profile_photo = output_relative_link(current, str(profile.get("photo_path", "assets/profile.jpg")))
    about_url = output_relative_link(current, "about/index.html")
    return f'''<aside class="site-sidebar" id="site-sidebar" aria-label="Browse posts">
  <details class="discovery-section home-search" data-panel="search" open>
    <summary aria-label="Search"><span class="eyebrow">SEARCH</span><span class="discovery-section__chevron" aria-hidden="true">⌄</span></summary>
    <form action="{html.escape(search_url, quote=True)}" method="get" role="search">
      <label class="sr-only" for="home-query">Search terms</label>
      <input id="home-query" name="q" type="search" autocomplete="off" placeholder="Search posts: Docker, LLVM, Python">
      <button type="submit">Search</button>
    </form>
  </details>
  <details class="discovery-section" data-panel="years" open>
    <summary aria-label="Archive"><span class="eyebrow">ARCHIVE</span><span class="discovery-section__chevron" aria-hidden="true">⌄</span></summary>
    <div class="archive-toolbar"><span>{len(posts)} posts</span><button type="button" data-archive-toggle aria-controls="archive-tree">Expand all</button></div>
    {year_archive_tree(posts, current)}
  </details>
  <section class="sidebar-about" aria-labelledby="sidebar-about-heading">
    <div class="sidebar-static-section__heading"><span class="eyebrow" id="sidebar-about-heading">ABOUT</span></div>
    <a class="sidebar-about__identity" href="{html.escape(about_url, quote=True)}">
      <img src="{html.escape(profile_photo, quote=True)}" width="220" height="147" alt="">
      <span>{profile_name}</span>
    </a>
    <a class="sidebar-about__link" href="{html.escape(about_url, quote=True)}">View my complete profile ↗</a>
    {visitor_counter(config)}
    <div class="sidebar-license sidebar-license--about">
      <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.zh-Hant" target="_blank" rel="license noopener"><img src="{html.escape(license_badge_url, quote=True)}" width="88" height="31" alt="Creative Commons Attribution-ShareAlike 4.0 International"></a>
    </div>
  </section>
  <section class="sidebar-static-section" aria-labelledby="labels-heading">
    <div class="sidebar-static-section__heading"><span class="eyebrow" id="labels-heading">LABELS</span></div>
    {label_cloud(posts, current)}
  </section>
</aside>'''


def content_with_sidebar(content: str, sidebar: str) -> str:
    """Keep the classic left-content/right-sidebar layout on every HTML page."""
    return f'''<div class="site-layout">
  <section class="site-layout__content">{content}</section>
  {sidebar}
</div>'''


def giscus_embed(config: dict[str, Any]) -> str:
    """Render Giscus once its repository and category IDs are configured."""
    settings = config.get("giscus", {})
    repo_id = str(settings.get("repo_id", "")).strip()
    category_id = str(settings.get("category_id", "")).strip()
    if not repo_id or not category_id:
        # A half-configured comment box is site furniture the reader cannot use;
        # render nothing until Giscus actually has its identifiers.
        return ""
    attributes = {
        "data-repo": settings.get("repo", ""),
        "data-repo-id": repo_id,
        "data-category": settings.get("category", "Announcements"),
        "data-category-id": category_id,
        "data-mapping": settings.get("mapping", "pathname"),
        "data-strict": settings.get("strict", "0"),
        "data-reactions-enabled": settings.get("reactions_enabled", "1"),
        "data-emit-metadata": settings.get("emit_metadata", "0"),
        "data-input-position": settings.get("input_position", "bottom"),
        "data-theme": settings.get("theme", "dark"),
        "data-lang": settings.get("lang", "zh-TW"),
        "crossorigin": "anonymous",
    }
    rendered = "\n      ".join(
        f'{name}="{html.escape(str(value), quote=True)}"' for name, value in attributes.items()
    )
    return f'''<section class="comments">
  <h2>Comments</h2>
  <script src="https://giscus.app/client.js"
      {rendered}
      async></script>
</section>'''


def post_thumbnail(
    post: dict[str, Any],
    current: str,
    media: dict[str, str],
    thumbnails: dict[str, tuple[str, str]],
) -> str:
    """Use the first actual in-article image as a compact list thumbnail."""
    if post["route"] in thumbnails:
        thumbnail_path, thumbnail_alt = thumbnails[post["route"]]
        source = output_relative_link(current, thumbnail_path)
        alt = thumbnail_alt or post["title"]
        return f'''<a class="post-card__thumbnail" href="{html.escape(output_relative_link(current, post["route"]), quote=True)}" aria-label="{html.escape(post["title"], quote=True)}">
  <img src="{html.escape(source, quote=True)}" alt="{html.escape(alt, quote=True)}" loading="lazy" decoding="async">
</a>'''
    soup = BeautifulSoup(post.get("rendered_content", ""), "html.parser")
    for image in soup.find_all("img", src=True):
        source = str(image.get("src", "")).strip()
        if not source:
            continue
        parsed = urlsplit(source)
        host = (parsed.hostname or "").casefold()
        # HackMD S3 preview URLs are signed and expire; use a later valid image
        # from the same post rather than displaying a broken card thumbnail.
        query = parsed.query.casefold()
        if host.startswith("hackmd-prod-images.") and ("expires=" in query or "x-amz-expires=" in query):
            continue
        if source in media:
            source = output_relative_link(current, media[source])
        alt = str(image.get("alt") or post["title"])
        return f'''<a class="post-card__thumbnail" href="{html.escape(output_relative_link(current, post["route"]), quote=True)}" aria-label="{html.escape(post["title"], quote=True)}">
  <img src="{html.escape(source, quote=True)}" alt="{html.escape(alt, quote=True)}" loading="lazy" decoding="async">
</a>'''
    return ""


def thumbnail_route(
    post: dict[str, Any],
    media: dict[str, str],
    thumbnails: dict[str, tuple[str, str]],
) -> str:
    """The card thumbnail as a site-relative path, or "" when there is none."""
    if post["route"] in thumbnails:
        return thumbnails[post["route"]][0]
    soup = BeautifulSoup(post.get("rendered_content", ""), "html.parser")
    for image in soup.find_all("img", src=True):
        source = str(image.get("src", "")).strip()
        if source in media:
            return media[source]
    return ""


def post_card(
    post: dict[str, Any],
    current: str,
    tag_paths: dict[str, str],
    category_paths: dict[str, str],
    media: dict[str, str],
    thumbnails: dict[str, tuple[str, str]],
) -> str:
    href = output_relative_link(current, post["route"])
    thumbnail = post_thumbnail(post, current, media, thumbnails)
    return f'''<article class="post-card" data-reveal>
  <div class="post-card__body">
    <div class="post-card__meta"><time datetime="{html.escape(post['published'], quote=True)}">{display_date(post['published'])}</time></div>
    <h2><a href="{html.escape(href, quote=True)}">{html.escape(post['title'])}</a></h2>
    <p>{html.escape(post_text(post))}</p>
    {category_links(post, current, category_paths)}
  </div>
  {thumbnail}
</article>'''


def pagination(posts: list[dict[str, Any]], current: str, page: int, per_page: int) -> str:
    page_count = (len(posts) + per_page - 1) // per_page
    if page_count < 2:
        return ""

    def page_path(number: int) -> str:
        return "index.html" if number == 1 else f"page/{number}/index.html"

    parts = ['<nav class="pagination" aria-label="Post pagination">']
    if page > 1:
        parts.append(f'<a href="{html.escape(output_relative_link(current, page_path(page - 1)), quote=True)}">← Newer</a>')
    parts.append(f"<span>{page} / {page_count}</span>")
    if page < page_count:
        parts.append(f'<a href="{html.escape(output_relative_link(current, page_path(page + 1)), quote=True)}">Older →</a>')
    parts.append("</nav>")
    return "".join(parts)


def write_page(output_root: Path, relative: str, contents: str) -> None:
    target = output_root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    temporary.write_text(contents, encoding="utf-8")
    temporary.replace(target)


def build_posts(
    output_root: Path,
    config: dict[str, Any],
    posts: list[dict[str, Any]],
    routes: set[str],
    media: dict[str, str],
    tag_paths: dict[str, str],
    category_paths: dict[str, str],
    cloud_category_order: list[str],
    dimensions: dict[str, tuple[int, int]] | None = None,
) -> None:
    blog_host = urlsplit(str(config["source_blog_url"])).hostname or ""
    for index, post in enumerate(posts):
        previous_post = posts[index - 1] if index else None
        next_post = posts[index + 1] if index + 1 < len(posts) else None
        content = rewrite_article_html(post, post["route"], routes, media, blog_host, dimensions)
        adjacent: list[str] = []
        if previous_post:
            adjacent.append(
                f'<a href="{html.escape(output_relative_link(post["route"], previous_post["route"]), quote=True)}">← {html.escape(previous_post["title"])}</a>'
            )
        if next_post:
            adjacent.append(
                f'<a href="{html.escape(output_relative_link(post["route"], next_post["route"]), quote=True)}">{html.escape(next_post["title"])} →</a>'
            )
        body = f'''<article class="post-page">
  <header class="post-page__header">
    {'<p class="draft-flag">草稿預覽 · 這篇尚未發布</p>' if post.get('draft') else ''}
    <div class="eyebrow">ARCHIVE / {display_date(post['published'])}</div>
    <h1>{html.escape(post['title'])}</h1>
    <div class="post-page__details"><time datetime="{html.escape(post['published'], quote=True)}">Published {display_date(post['published'])}</time>{category_links(post, post['route'], category_paths)}</div>
  </header>
  <div class="post-content">{content}</div>
  {legacy_tag_details(post, post['route'], tag_paths)}
  <nav class="post-adjacent" aria-label="Adjacent posts">{''.join(adjacent)}</nav>
  {giscus_embed(config)}
</article>'''
        sidebar = site_sidebar(config, posts, post["route"], category_paths, cloud_category_order)
        rendered = content_with_sidebar(body, sidebar)
        write_page(
            output_root,
            post["route"],
            page_shell(config, post["route"], post["title"], post_text(post), rendered, noindex=bool(post.get("draft"))),
        )


def home_filter(posts: list[dict[str, Any]], category_order: list[str], page: int) -> str:
    """A progressive-enhancement filter bar for the post list.

    The list above it is server-rendered and works with JavaScript disabled; this
    form only becomes active once the browser has the search index, which is why
    it is hidden by default and revealed by the script.
    """
    if page != 1:
        return ""
    years = sorted({str(post["published"])[:4] for post in posts}, reverse=True)
    topics = "".join(
        f'<option value="{html.escape(name, quote=True)}">{html.escape(name)}</option>'
        for name in category_order
    )
    year_options = "".join(f'<option value="{year}">{year}</option>' for year in years)
    return f'''<form class="post-filter" data-post-filter hidden>
  <label class="post-filter__field post-filter__field--grow">
    <span class="sr-only">Filter posts</span>
    <input type="search" name="q" placeholder="Filter {len(posts)} posts: Docker, LLVM, RISC-V…" autocomplete="off" data-filter-query>
  </label>
  <label class="post-filter__field">
    <span class="sr-only">Topic</span>
    <select name="topic" data-filter-topic><option value="">All topics</option>{topics}</select>
  </label>
  <label class="post-filter__field">
    <span class="sr-only">Year</span>
    <select name="year" data-filter-year><option value="">All years</option>{year_options}</select>
  </label>
  <button type="button" class="post-filter__reset" data-filter-reset hidden>Clear</button>
  <p class="post-filter__status" role="status" aria-live="polite" data-filter-status></p>
</form>'''


def build_index(
    output_root: Path,
    config: dict[str, Any],
    posts: list[dict[str, Any]],
    tag_paths: dict[str, str],
    category_paths: dict[str, str],
    category_order: list[str],
    cloud_category_order: list[str],
    media: dict[str, str],
    thumbnails: dict[str, tuple[str, str]],
) -> None:
    per_page = config["per_page"]
    page_count = max(1, (len(posts) + per_page - 1) // per_page)
    for page in range(1, page_count + 1):
        current = "index.html" if page == 1 else f"page/{page}/index.html"
        selected = posts[(page - 1) * per_page : page * per_page]
        cards = "\n".join(post_card(post, current, tag_paths, category_paths, media, thumbnails) for post in selected)
        intro = ""
        article_heading = (
            '<section class="home-article-heading"><p class="eyebrow">ALL POSTS</p><h2>Posts</h2></section>'
            if page == 1
            else f'<section class="home-article-heading"><p class="eyebrow">ALL POSTS</p><h2>Posts · Page {page}</h2></section>'
        )
        article_list = (
            f"{article_heading}{home_filter(posts, category_order, page)}"
            f'<section class="post-list" data-post-list>{cards}</section>'
            f'<div data-pagination>{pagination(posts, current, page, per_page)}</div>'
        )
        sidebar = site_sidebar(config, posts, current, category_paths, cloud_category_order)
        body = f'{intro}{content_with_sidebar(article_list, sidebar)}'
        title = "" if page == 1 else f"Posts · Page {page}"
        write_page(output_root, current, page_shell(config, current, title, str(config["description"]), body))


def build_tags(
    output_root: Path,
    config: dict[str, Any],
    posts: list[dict[str, Any]],
    tag_paths: dict[str, str],
    category_paths: dict[str, str],
    cloud_category_order: list[str],
    media: dict[str, str],
    thumbnails: dict[str, tuple[str, str]],
) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for post in posts:
        for tag in post["tags"]:
            grouped[tag].append(post)
    current = "tags/index.html"
    items = "".join(
        f'<a class="tag-cloud__tag" href="{html.escape(output_relative_link(current, tag_paths[tag]), quote=True)}">{html.escape(tag)} <span>{len(grouped[tag])}</span></a>'
        for tag in sorted(grouped, key=lambda item: (-len(grouped[item]), item.casefold()))
    )
    content = f'<section class="page-heading"><p class="eyebrow">TAXONOMY</p><h1>Labels</h1><p>{len(grouped)} normalised Blogger labels, consolidated only where spelling, casing, or meaning are unambiguous.</p></section><div class="tag-cloud">{items}</div>'
    body = content_with_sidebar(content, site_sidebar(config, posts, current, category_paths, cloud_category_order))
    write_page(output_root, current, page_shell(config, current, "Labels", "Browse normalised Blogger labels.", body))

    for tag, selected in grouped.items():
        current = tag_paths[tag]
        cards = "\n".join(post_card(post, current, tag_paths, category_paths, media, thumbnails) for post in selected)
        content = f'<section class="page-heading"><p class="eyebrow">LABEL / {html.escape(tag)}</p><h1>#{html.escape(tag)}</h1><p>{len(selected)} posts</p></section><section class="post-list">{cards}</section>'
        body = content_with_sidebar(content, site_sidebar(config, posts, current, category_paths, cloud_category_order))
        write_page(output_root, current, page_shell(config, current, f"Label: {tag}", f"Posts labelled {tag}.", body))


def build_categories(
    output_root: Path,
    config: dict[str, Any],
    posts: list[dict[str, Any]],
    tag_paths: dict[str, str],
    category_paths: dict[str, str],
    category_order: list[str],
    cloud_category_order: list[str],
    media: dict[str, str],
    thumbnails: dict[str, tuple[str, str]],
) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for post in posts:
        for category in post.get("categories", []):
            grouped[category].append(post)
    current = "categories/index.html"
    items = "".join(
        f'<a class="category-card" href="{html.escape(output_relative_link(current, category_paths[category]), quote=True)}"><span>{html.escape(category)}</span><strong>{len(grouped[category])}</strong></a>'
        for category in category_order
        if category in grouped
    )
    legacy_tags_url = output_relative_link(current, "tags/index.html")
    content = '''<section class="page-heading"><p class="eyebrow">CURATED TAXONOMY</p><h1>Topics</h1><p>Original Blogger labels have been non-destructively consolidated into English technical topics. Posts and original labels remain intact.</p>''' + f'<p><a class="text-link" href="{html.escape(legacy_tags_url, quote=True)}">View original labels →</a></p></section><div class="category-grid">{items}</div>'
    body = content_with_sidebar(content, site_sidebar(config, posts, current, category_paths, cloud_category_order))
    write_page(output_root, current, page_shell(config, current, "Topics", "Curated English topics for technical articles.", body))
    for category in category_order:
        selected = grouped.get(category, [])
        if not selected:
            continue
        current = category_paths[category]
        cards = "\n".join(post_card(post, current, tag_paths, category_paths, media, thumbnails) for post in selected)
        content = f'<section class="page-heading"><p class="eyebrow">CATEGORY</p><h1>{html.escape(category)}</h1><p>{len(selected)} posts</p></section><section class="post-list">{cards}</section>'
        body = content_with_sidebar(content, site_sidebar(config, posts, current, category_paths, cloud_category_order))
        write_page(output_root, current, page_shell(config, current, category, f"{category} posts.", body))


def build_archive(
    output_root: Path,
    config: dict[str, Any],
    posts: list[dict[str, Any]],
    category_paths: dict[str, str],
    cloud_category_order: list[str],
) -> None:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for post in posts:
        groups[display_date(post["published"])[:4]].append(post)
    current = "archive/index.html"
    sections: list[str] = []
    for year in sorted(groups, reverse=True):
        links = "".join(
            f'<li><time datetime="{html.escape(post["published"], quote=True)}">{display_date(post["published"])[5:]}</time><a href="{html.escape(output_relative_link(current, post["route"]), quote=True)}">{html.escape(post["title"])}</a></li>'
            for post in groups[year]
        )
        sections.append(f'<section class="archive-year" id="year-{year}"><h2>{year}<span>{len(groups[year])}</span></h2><ul>{links}</ul></section>')
    content = '<section class="page-heading"><p class="eyebrow">TIMELINE</p><h1>Archive</h1><p>Posts by original publication date, newest year first.</p></section>' + "".join(sections)
    body = content_with_sidebar(content, site_sidebar(config, posts, current, category_paths, cloud_category_order))
    write_page(output_root, current, page_shell(config, current, "Archive", "Browse all posts by year.", body))


def build_search(
    output_root: Path,
    config: dict[str, Any],
    posts: list[dict[str, Any]],
    category_paths: dict[str, str],
    cloud_category_order: list[str],
) -> None:
    current = "search/index.html"
    content = '''<section class="page-heading"><p class="eyebrow">SEARCH</p><h1>Search posts</h1><p>Search titles, labels, and article text.</p></section>
<div class="search-box" data-search>
  <label for="query">Search terms</label>
  <input id="query" type="search" autocomplete="off" placeholder="Docker, LLVM, Python">
  <p class="search-status" aria-live="polite"></p>
  <div class="search-results"></div>
</div>'''
    body = content_with_sidebar(content, site_sidebar(config, posts, current, category_paths, cloud_category_order))
    write_page(output_root, current, page_shell(config, current, "Search", "Search the complete technical archive.", body))


def build_about(
    output_root: Path,
    config: dict[str, Any],
    posts: list[dict[str, Any]],
    category_paths: dict[str, str],
    cloud_category_order: list[str],
) -> None:
    current = "about/index.html"
    profile = config.get("profile", {})
    name = html.escape(str(profile.get("name", config["title"])))
    photo = output_relative_link(current, str(profile.get("photo_path", "assets/profile.jpg")))
    email = html.escape(str(profile.get("email", "")), quote=True)
    website = html.escape(str(profile.get("website", "")), quote=True)
    blogger_profile = html.escape(str(profile.get("blogger_profile_url", "")), quote=True)
    intro = html.escape(str(profile.get("introduction", "")))
    metadata = [
        ("On Blogger since", str(profile.get("joined", ""))),
        ("Profile views", str(profile.get("profile_views", ""))),
        ("Gender", str(profile.get("gender", ""))),
        ("Industry", str(profile.get("industry", ""))),
    ]
    facts = "".join(
        f"<dt>{html.escape(label)}</dt><dd>{html.escape(value)}</dd>"
        for label, value in metadata
        if value
    )
    contacts = "".join(
        part
        for part in [
            f'<a href="mailto:{email}">{email}</a>' if email else "",
            f'<a href="{website}" target="_blank" rel="noopener">x213212.github.io ↗</a>' if website else "",
            f'<a href="{blogger_profile}" target="_blank" rel="noopener">Original Blogger profile ↗</a>' if blogger_profile else "",
        ]
        if part
    )
    content = f'''<section class="page-heading"><p class="eyebrow">PROFILE</p><h1>About</h1></section>
<article class="about-profile">
  <img class="about-profile__photo" src="{html.escape(photo, quote=True)}" width="220" height="147" alt="{name} profile photo">
  <div class="about-profile__body">
    <h2>{name}</h2>
    <p>{intro}</p>
    <dl>{facts}</dl>
    <section class="about-profile__contact"><h3>Contact</h3>{contacts}</section>
  </div>
</article>'''
    body = content_with_sidebar(content, site_sidebar(config, posts, current, category_paths, cloud_category_order))
    write_page(output_root, current, page_shell(config, current, "About", f"About {profile.get('name', config['title'])}.", body))


def build_feed_and_sitemap(output_root: Path, config: dict[str, Any], posts: list[dict[str, Any]]) -> None:
    # A preview build renders drafts, but they must never be advertised.
    posts = [post for post in posts if not post.get("draft")]
    sitemap_entries = "\n".join(
        f"  <url><loc>{xml_escape(absolute_url(config, post['route']))}</loc><lastmod>{xml_escape(post['updated'])}</lastmod></url>"
        for post in posts
    )
    sitemap_entries += f"\n  <url><loc>{xml_escape(absolute_url(config, 'index.html'))}</loc></url>"
    write_page(
        output_root,
        "sitemap.xml",
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap_entries}\n</urlset>\n',
    )
    entries = "\n".join(
        f'''  <item>
    <title>{xml_escape(post['title'])}</title>
    <link>{xml_escape(absolute_url(config, post['route']))}</link>
    <guid isPermaLink="true">{xml_escape(absolute_url(config, post['route']))}</guid>
    <pubDate>{iso_date(post['published']).strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>
    <description>{xml_escape(post_text(post, 380))}</description>
  </item>'''
        for post in posts[:30]
    )
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>{xml_escape(str(config['title']))}</title>
  <link>{xml_escape(absolute_url(config, 'index.html'))}</link>
  <description>{xml_escape(str(config['description']))}</description>
  <language>zh-Hant</language>
{entries}
</channel></rss>
'''
    write_page(output_root, "feed.xml", rss)
    write_page(output_root, "robots.txt", "User-agent: *\nAllow: /\nSitemap: " + absolute_url(config, "sitemap.xml") + "\n")


def build_404(
    output_root: Path,
    config: dict[str, Any],
    posts: list[dict[str, Any]],
    category_paths: dict[str, str],
    cloud_category_order: list[str],
) -> None:
    current = "404.html"
    content = '''<section class="not-found"><p class="eyebrow">404</p><h1>Page not found</h1><p>The post may have moved. Continue with search or the archive.</p><p><a class="button" href="index.html">Back to home</a></p></section>'''
    body = content_with_sidebar(content, site_sidebar(config, posts, current, category_paths, cloud_category_order))
    write_page(output_root, current, page_shell(config, current, "Page not found", "The requested page was not found.", body))


def build_maintenance(output_root: Path, config: dict[str, Any]) -> None:
    """Publish a maintenance notice in place of the archive.

    Both index.html and 404.html carry it, so a deep link to an article shows the
    notice too rather than a bare not-found page.
    """
    settings = config.get("maintenance", {})
    heading = str(settings.get("heading", "Under maintenance"))
    message = str(settings.get("message", "The archive is being rebuilt and will be back shortly."))
    body = f'''<section class="not-found maintenance">
  <p class="eyebrow">STATUS</p>
  <h1>{html.escape(heading)}</h1>
  <p>{html.escape(message)}</p>
  <p class="maintenance__meta">{html.escape(str(config["title"]))} · <a href="{html.escape(str(config["github_url"]), quote=True)}">GitHub</a></p>
</section>'''
    page = page_shell(config, "index.html", heading, message, body, noindex=True)
    write_page(output_root, "index.html", page)
    write_page(output_root, "404.html", page_shell(config, "404.html", heading, message, body, noindex=True))
    write_page(output_root, ".nojekyll", "")


def render_single_post(root: Path, config: dict[str, Any], filename: str, asset_base: str) -> int:
    """Render one Markdown file as a standalone page for the local admin preview.

    This is the same renderer the site uses, so a draft is proofread exactly as it
    will look once published - without writing to ``docs/`` or publishing anything.
    """
    if Path(filename).name != filename or not filename.endswith(".md"):
        print("invalid post filename", file=sys.stderr)
        return 2
    source_path = root / "content" / "posts" / filename
    if not source_path.is_file():
        print(f"post not found: {filename}", file=sys.stderr)
        return 2

    metadata: dict[str, Any] = {}
    text = source_path.read_text(encoding="utf-8")
    body = text
    if text.startswith("---\n"):
        marker = text.find("\n---\n", 4)
        if marker != -1:
            for line in text[4:marker].splitlines():
                if ":" not in line:
                    continue
                key, raw = line.split(":", 1)
                try:
                    metadata[key.strip()] = json.loads(raw.strip())
                except json.JSONDecodeError:
                    metadata[key.strip()] = raw.strip()
            body = text[marker + 5 :].lstrip("\n")

    title = str(metadata.get("title") or filename)
    published = str(metadata.get("date") or "")
    is_draft = front_matter_bool(metadata.get("draft", False))
    base = asset_base.rstrip("/")
    tags = "".join(
        f'<span class="tag">#{html.escape(str(tag))}</span>'
        for tag in (metadata.get("tags") or [])
    )
    article = f'''<article class="post-page">
  <header class="post-page__header">
    {'<p class="draft-flag">草稿預覽 · 尚未發布</p>' if is_draft else '<p class="draft-flag">預覽 · 未重新建置</p>'}
    <div class="eyebrow">PREVIEW / {html.escape(published[:10])}</div>
    <h1>{html.escape(title)}</h1>
    <div class="post-page__details"><time>{html.escape(published[:10])}</time></div>
  </header>
  <div class="post-content">{render_markdown(body)}</div>
  <div class="post-tags">{tags}</div>
</article>'''
    print(preview_document(title, article, base))
    return 0


def preview_document(title: str, article: str, asset_base: str) -> str:
    """Wrap a rendered article in a standalone page that loads the site styles."""
    base = asset_base.rstrip("/")
    return f'''<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <link rel="stylesheet" href="{html.escape(base, quote=True)}/site.css">
  <title>{html.escape(title)} · 預覽</title>
</head>
<body>
  <main id="main" class="site-main">{article}</main>
  <script src="{html.escape(base, quote=True)}/site.js" defer></script>
</body>
</html>'''


def render_body_preview(asset_base: str) -> int:
    """Render Markdown arriving on stdin, for the editor's live preview pane.

    Nothing is read from or written to disk: this is the same renderer the site
    uses, applied to text the author has not saved yet.
    """
    article = (
        '''<article class="post-page">
  <div class="post-content">'''
        + render_markdown(sys.stdin.read())
        + "</div>\n</article>"
    )
    print(preview_document("Live", article, asset_base))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--clean", action="store_true", help="Remove stale generated files before building (not needed for local preview).")
    parser.add_argument(
        "--include-drafts",
        action="store_true",
        help="Render drafts too, for local preview. Drafts are marked, kept out of "
             "the feed and sitemap, and served noindex, so this output is never "
             "safe to publish. CI never passes this flag.",
    )
    parser.add_argument(
        "--render-post",
        metavar="FILENAME",
        help="Render one content/posts/*.md file to stdout as a standalone preview "
             "page and exit. Nothing is written to docs/ and nothing is published.",
    )
    parser.add_argument(
        "--render-body",
        action="store_true",
        help="Render Markdown read from stdin to stdout as a standalone preview "
             "page and exit. Used by the local admin's live editor preview.",
    )
    parser.add_argument(
        "--asset-base",
        default="/preview-assets",
        help="URL prefix the --render-post preview uses for site.css and site.js.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    config = read_config(root)
    if args.render_body:
        return render_body_preview(args.asset_base)
    if args.render_post:
        return render_single_post(root, config, args.render_post, args.asset_base)
    all_posts = load_editable_posts(root)
    draft_count = sum(bool(post.get("draft")) for post in all_posts)
    posts = all_posts if args.include_drafts else [post for post in all_posts if not post.get("draft")]
    posts, category_order, cloud_category_order = attach_categories(root, posts)
    for post in posts:
        post["rendered_content"] = render_markdown(post["content"])
    posts.sort(key=lambda post: (post["published"], post.get("url", "")), reverse=True)
    routes = {post["route"] for post in posts}
    if len(routes) != len(posts):
        raise RuntimeError("Duplicate canonical post routes found")

    manifest = load_json(root / "data" / "media-manifest.json")
    media_config = config.get("media", {})
    use_local_mirror = bool(media_config.get("use_local_mirror", False))
    media_variant = str(media_config.get("variant", "original")).strip().casefold()
    if media_variant not in {"original", "optimized"}:
        raise RuntimeError("media.variant must be either 'original' or 'optimized'")
    if not use_local_mirror:
        media = {}
        thumbnails: dict[str, tuple[str, str]] = {}
    elif media_variant == "optimized":
        media = optimized_media_mapping(root)
        thumbnails = optimized_thumbnail_mapping(root)
    else:
        media = {
            item["url"]: item["local_path"]
            for item in manifest
            if item.get("status") == "downloaded" and item.get("local_path")
        }
        thumbnails = {}
    tags = sorted({tag for post in posts for tag in post["tags"]}, key=str.casefold)
    tag_paths = {tag: f"tags/{tag_slug(tag)}.html" for tag in tags}
    category_paths = {category: f"categories/{tag_slug(category)}.html" for category in category_order}

    output_root = root / "docs"
    if args.clean:
        shutil.rmtree(output_root, ignore_errors=True)
    output_root.mkdir(parents=True, exist_ok=True)
    assets_source = root / "site" / "assets"
    if assets_source.exists():
        if not use_local_mirror:
            ignored = shutil.ignore_patterns("media", "media-optimized")
        elif media_variant == "optimized":
            # Never pull the original 1 GB cache into docs/ in optimized mode.
            ignored = shutil.ignore_patterns("media")
        else:
            ignored = shutil.ignore_patterns("media-optimized")
        shutil.copytree(assets_source, output_root / "assets", dirs_exist_ok=True, ignore=ignored)

    # Files that have to sit at the site root to work at all: search-console
    # verification, ads.txt, a CNAME. Anything in site/root/ is copied verbatim.
    root_passthrough = root / "site" / "root"
    if root_passthrough.is_dir():
        shutil.copytree(root_passthrough, output_root, dirs_exist_ok=True)
    write_page(output_root, ".nojekyll", "")

    if config.get("maintenance", {}).get("enabled"):
        # Emit only the notice: leaving the old articles in place would let deep
        # links serve stale content while the site is meant to be down.
        build_maintenance(output_root, config)
        print(json.dumps({"built_at": datetime.now(timezone.utc).isoformat(), "maintenance": True, "output": output_root.name}))
        return 0

    dimensions = optimized_media_dimensions(root) if use_local_mirror and media_variant == "optimized" else {}
    build_posts(output_root, config, posts, routes, media, tag_paths, category_paths, cloud_category_order, dimensions)
    build_index(output_root, config, posts, tag_paths, category_paths, category_order, cloud_category_order, media, thumbnails)
    build_tags(output_root, config, posts, tag_paths, category_paths, cloud_category_order, media, thumbnails)
    build_categories(output_root, config, posts, tag_paths, category_paths, category_order, cloud_category_order, media, thumbnails)
    build_archive(output_root, config, posts, category_paths, cloud_category_order)
    build_search(output_root, config, posts, category_paths, cloud_category_order)
    build_about(output_root, config, posts, category_paths, cloud_category_order)
    build_404(output_root, config, posts, category_paths, cloud_category_order)
    build_feed_and_sitemap(output_root, config, posts)

    # One index serves both the search page and the home-page filter, so it
    # carries everything a post card needs to be rebuilt in the browser.
    search_index = [
        {
            "title": post["title"],
            "date": display_date(post["published"]),
            "iso": post["published"],
            "tags": post["tags"],
            "categories": post.get("categories", []),
            "text": post_text(post, 600),
            "route": post["route"],
            "thumb": thumbnail_route(post, media, thumbnails),
        }
        for post in posts
    ]
    save_json(output_root / "assets" / "search-index.json", search_index)
    build_report = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "posts": len(posts),
        "published_posts": sum(not post.get("draft") for post in posts),
        "draft_posts": draft_count,
        "includes_drafts": bool(args.include_drafts),
        "tags": len(tags),
        "categories": len(category_order),
        "localized_media": len(media),
        "localized_thumbnails": len(thumbnails),
        "using_local_media_mirror": use_local_mirror,
        "media_variant": media_variant if use_local_mirror else "remote",
        "output": "docs",
    }
    save_json(root / "data" / "build-report.json", build_report)
    print(json.dumps(build_report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
