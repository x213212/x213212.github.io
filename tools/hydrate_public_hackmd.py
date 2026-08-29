#!/usr/bin/env python3
"""Replace public HackMD iframes in imported Blogger posts with their Markdown.

Only iframe URLs already present in public Blogspot article bodies are fetched.
No account, cookie, private export, or non-iframe HackMD link is considered.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


USER_AGENT = "Mozilla/5.0 (compatible; BlogMigration/1.0; +https://github.com/)"
IFRAME_PATTERN = re.compile(
    r"<iframe\b(?P<attrs>[^>]*)>\s*</iframe>", re.IGNORECASE | re.DOTALL
)
SRC_PATTERN = re.compile(r"\bsrc\s*=\s*(['\"])(?P<url>.*?)\1", re.IGNORECASE | re.DOTALL)
MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(\s*(?:<)?(?P<url>https?://[^\s>)]+)", re.IGNORECASE)
RAW_IMAGE_PATTERN = re.compile(r"\bsrc\s*=\s*(['\"])(?P<url>https?://.*?)\1", re.IGNORECASE)
NOTE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{6,128}$")


def parse_front_matter(source: str) -> tuple[str, str]:
    if not source.startswith("---\n"):
        return "", source
    marker = source.find("\n---\n", 4)
    if marker == -1:
        return "", source
    return source[: marker + 5], source[marker + 5 :]


def note_id_from_url(url: str) -> str | None:
    parsed = urlsplit(url)
    if parsed.hostname not in {"hackmd.io", "www.hackmd.io"}:
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return None
    candidate = parts[-1]
    # `/s/<id>` is an ordinary external link, not an iframe source selected by
    # this migration. An iframe can be profile-style or bare note-style only.
    if len(parts) >= 2 and parts[-2] == "s":
        return None
    return candidate if NOTE_ID_PATTERN.fullmatch(candidate) else None


def strip_hackmd_front_matter(markdown: str) -> str:
    if not markdown.startswith("---\n"):
        return markdown.strip()
    marker = markdown.find("\n---\n", 4)
    body = markdown[marker + 5 :] if marker != -1 else markdown
    # HackMD appends `=` to a fenced-code language (` ```python=`). It is not
    # CommonMark and renders as literal text in GitHub Pages, so remove only
    # that terminal syntax marker while leaving code and prose unchanged.
    body = re.sub(r"(?m)^(`{3,}[^`\r\n]*)=[ \t]*$", r"\1", body)
    return re.sub(r"(?m)^(`{3,})=([A-Za-z0-9_+-]+)[ \t]*$", r"\1\2", body).strip()


def fetch_note(note_id: str) -> dict[str, Any]:
    source_url = f"https://hackmd.io/{note_id}/download"
    request = Request(source_url, headers={"User-Agent": USER_AGENT, "Accept": "text/markdown,text/plain;q=0.9,*/*;q=0.1"})
    try:
        with urlopen(request, timeout=90) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            payload = response.read(8_000_001)
        if len(payload) > 8_000_000:
            raise ValueError("response exceeds 8 MB limit")
        if not (content_type.startswith("text/markdown") or content_type.startswith("text/plain")):
            raise ValueError(f"unexpected content type: {content_type}")
        markdown = strip_hackmd_front_matter(payload.decode("utf-8", "replace"))
        if not markdown:
            raise ValueError("empty Markdown response")
        return {
            "note_id": note_id,
            "status": "downloaded",
            "download_url": source_url,
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "markdown": markdown,
        }
    except Exception as error:
        return {"note_id": note_id, "status": "failed", "download_url": source_url, "error": f"{type(error).__name__}: {error}"}


def find_iframes(body: str) -> list[tuple[re.Match[str], str, str]]:
    found: list[tuple[re.Match[str], str, str]] = []
    for match in IFRAME_PATTERN.finditer(body):
        src_match = SRC_PATTERN.search(match.group("attrs"))
        if not src_match:
            continue
        source_url = src_match.group("url").strip()
        note_id = note_id_from_url(source_url)
        if note_id:
            found.append((match, source_url, note_id))
    return found


def replacement(source_url: str, note: dict[str, Any]) -> str:
    # The published Markdown carries no import bookkeeping; provenance lives in
    # data/hackmd-hydration-report.json.
    del source_url
    return f"\n\n{note['markdown'].strip()}\n\n"


def markdown_media(markdown: str) -> set[str]:
    return {match.group("url") for match in MARKDOWN_IMAGE_PATTERN.finditer(markdown)} | {
        match.group("url") for match in RAW_IMAGE_PATTERN.finditer(markdown)
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    root = args.root.resolve()
    posts = json.loads((root / "data" / "posts.json").read_text(encoding="utf-8"))["posts"]
    source_dir = root / "source" / "hackmd"
    source_dir.mkdir(parents=True, exist_ok=True)

    pending: dict[str, dict[str, Any]] = {}
    post_iframes: dict[str, list[tuple[re.Match[str], str, str]]] = {}
    source_by_route: dict[str, tuple[str, str]] = {}
    for post in posts:
        path = root / "content" / "posts" / post["content_file"]
        front_matter, body = parse_front_matter(path.read_text(encoding="utf-8"))
        found = find_iframes(body)
        if not found:
            continue
        source_by_route[post["route"]] = (front_matter, body)
        post_iframes[post["route"]] = found
        for _, source_url, note_id in found:
            pending.setdefault(note_id, {"source_urls": set(), "routes": set()})
            pending[note_id]["source_urls"].add(source_url)
            pending[note_id]["routes"].add(post["route"])

    results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(fetch_note, note_id): note_id for note_id in pending}
        for future in as_completed(futures):
            result = future.result()
            results[result["note_id"]] = result
            print(f"{result['status']:10} {result['note_id']}")

    hydrated_routes: list[str] = []
    additions: dict[str, set[str]] = {}
    for route, found in post_iframes.items():
        front_matter, original_body = source_by_route[route]
        output: list[str] = []
        cursor = 0
        changed = False
        for match, source_url, note_id in found:
            output.append(original_body[cursor : match.start()])
            note = results[note_id]
            if note["status"] == "downloaded":
                output.append(replacement(source_url, note))
                additions[note_id] = markdown_media(note["markdown"])
                changed = True
            else:
                output.append(match.group(0))
            cursor = match.end()
        output.append(original_body[cursor:])
        if changed:
            post = next(item for item in posts if item["route"] == route)
            path = root / "content" / "posts" / post["content_file"]
            path.write_text(front_matter + "".join(output), encoding="utf-8")
            hydrated_routes.append(route)

    for note_id, note in results.items():
        if note["status"] == "downloaded":
            (source_dir / f"{note_id}.md").write_text(note["markdown"] + "\n", encoding="utf-8")

    report_notes = []
    for note_id in sorted(pending):
        note = dict(results[note_id])
        note.pop("markdown", None)
        note["routes"] = sorted(pending[note_id]["routes"])
        note["source_urls"] = sorted(pending[note_id]["source_urls"])
        note["media_urls"] = sorted(additions.get(note_id, set()))
        report_notes.append(note)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Only public HackMD iframes referenced by published Blogger posts.",
        "iframe_count": sum(len(items) for items in post_iframes.values()),
        "unique_note_count": len(pending),
        "hydrated_post_count": len(hydrated_routes),
        "downloaded_note_count": sum(note["status"] == "downloaded" for note in results.values()),
        "failed_note_count": sum(note["status"] != "downloaded" for note in results.values()),
        "notes": report_notes,
    }
    (root / "data" / "hackmd-hydration-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "data" / "hackmd-media-additions.json").write_text(
        json.dumps({note_id: sorted(urls) for note_id, urls in additions.items()}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: report[key] for key in ("iframe_count", "unique_note_count", "downloaded_note_count", "failed_note_count")}, ensure_ascii=False))
    return 0 if report["failed_note_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
