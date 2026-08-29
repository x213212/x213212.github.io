#!/usr/bin/env python3
"""Repair public historic media URLs that need a stable public resolver.

The normal downloader deliberately uses the URL embedded in each post.  A few
old hosts either expired signed URLs (which cannot safely be recovered) or
reject otherwise-valid historic thumbnail addresses.  This tool only handles
well-understood public alternatives and *keeps the original URL as the
manifest key*.  The site builder can therefore replace that exact original
reference with a local copy without rewriting the post text.

Unrecoverable items stay marked ``failed`` and are never replaced with a
look-alike image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from download_media import USER_AGENT, extension_for


MAX_BYTES = 20_000_000
IMAGE_ACCEPT = "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"


def public_alternative(url: str) -> str | None:
    """Return a verified-public resolver for a known, historic URL form."""
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    path = unquote(parsed.path)

    # Wikimedia now rejects many arbitrary thumbnail pixel widths, while its
    # canonical FilePath endpoint chooses a supported thumbnail size.
    if host == "upload.wikimedia.org" and "/thumb/" in path:
        pieces = path.split("/thumb/", 1)[1].split("/")
        if len(pieces) >= 4:
            filename = pieces[2]
            wiki = "zh.wikipedia.org" if "/wikipedia/zh/" in path else "commons.wikimedia.org"
            return f"https://{wiki}/wiki/Special:FilePath/{quote(filename)}?width=1024"

    # imgur's old /download endpoint blocks non-browser migration clients but
    # the same public asset remains available from the canonical image host.
    if host == "imgur.com" and path.startswith("/download/"):
        asset_id = path.rsplit("/", 1)[-1]
        if asset_id:
            return f"https://i.imgur.com/{asset_id}.gif"

    # GitHub's historical camo URLs contain the original URL as hex.  The
    # proxy signature has expired, but the referenced public image may remain.
    if host == "camo.githubusercontent.com":
        encoded = path.rsplit("/", 1)[-1]
        try:
            target = bytes.fromhex(encoded).decode("utf-8")
        except ValueError:
            return None
        target_parts = urlsplit(target)
        if target_parts.scheme in {"http", "https"} and target_parts.hostname:
            # Jianshu serves the same public image over HTTPS; prefer it over
            # the historical HTTP form embedded by the old camo proxy.
            return urlunsplit(("https", target_parts.netloc, target_parts.path, target_parts.query, ""))

    # Zhihu's CDN host is interchangeable for an image object; pic1 avoids a
    # transient edge timeout returned by the old pic4 endpoint.
    if host == "pic4.zhimg.com":
        return urlunsplit(("https", "pic1.zhimg.com", parsed.path, parsed.query, ""))

    # The original Arup asset was removed from its live URL.  This is an exact
    # public Internet Archive capture of that URL (not a substitute image).
    if host == "www.arup.com" and path.endswith(
        "highways-header-m6_toll_birmingham_northern_relief_road_bnrr_david_griffiths_photography-2000x1125.jpg"
    ):
        original_without_expired_query = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
        return f"https://web.archive.org/web/20240130165236id_/{original_without_expired_query}"

    return None


def irrecoverable_note(url: str) -> str | None:
    """Document known cases where no public, exact fallback is available."""
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    if host == "hackmd-prod-images.s3.ap-northeast-1.amazonaws.com":
        return (
            "The historic HackMD S3 URL is signed and its Expires timestamp has passed; "
            "the unsigned object returns 403 and no public URL for this exact object was found."
        )
    if host.endswith("fbcdn.net"):
        return (
            "The historic Facebook CDN URL signature has expired; the public photo endpoint no longer exposes "
            "an image for the embedded photo identifier, so no exact public replacement is available."
        )
    return None


def request_headers(source_url: str) -> dict[str, str]:
    headers = {"User-Agent": USER_AGENT, "Accept": IMAGE_ACCEPT}
    host = (urlsplit(source_url).hostname or "").lower()
    if host.endswith("jianshu.io"):
        headers["Referer"] = "https://www.jianshu.com/"
    elif host.endswith("zhimg.com"):
        headers["Referer"] = "https://www.zhihu.com/"
    return headers


def mirror_from_public_alternative(item: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    original_url = str(item["url"])
    source_url = public_alternative(original_url)
    if not source_url:
        return item

    result = dict(item)
    try:
        with urlopen(Request(source_url, headers=request_headers(source_url)), timeout=90) as response:
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            length = response.headers.get("Content-Length")
            if length and int(length) > MAX_BYTES:
                raise RuntimeError(f"content-length {length} exceeds {MAX_BYTES} bytes")
            payload = response.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise RuntimeError(f"download exceeds {MAX_BYTES} bytes")
        if not content_type.startswith(("image/", "video/", "audio/")):
            raise RuntimeError(f"public resolver returned non-media content type: {content_type or 'unknown'}")

        extension = extension_for(original_url, content_type)
        digest = hashlib.sha256(original_url.encode("utf-8")).hexdigest()[:20]
        relative = f"assets/media/{digest}{extension}"
        destination = output_dir / f"{digest}{extension}"
        output_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=output_dir, delete=False) as handle:
            handle.write(payload)
            temporary = Path(handle.name)
        os.replace(temporary, destination)
        result.update(
            status="downloaded",
            local_path=relative,
            bytes=len(payload),
            content_type=content_type,
            resolved_from=source_url,
            repaired_at=datetime.now(timezone.utc).isoformat(),
        )
        result.pop("error", None)
    except Exception as error:  # Preserve the prior failure and remote source.
        result.update(error=f"{type(error).__name__}: {error}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_path = root / "data" / "media-manifest.json"
    output_dir = root / "site" / "assets" / "media"
    manifest: list[dict[str, Any]] = json.loads(manifest_path.read_text(encoding="utf-8"))

    changed = 0
    for index, item in enumerate(manifest):
        if item.get("status") != "failed":
            continue
        if not public_alternative(str(item.get("url", ""))):
            note = irrecoverable_note(str(item.get("url", "")))
            if note:
                item["recovery_note"] = note
                item["recovery_attempted_at"] = datetime.now(timezone.utc).isoformat()
            continue
        repaired = mirror_from_public_alternative(item, output_dir)
        manifest[index] = repaired
        changed += int(repaired.get("status") == "downloaded")
        print(f"{repaired.get('status'):10} {item['url']}")

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for item in manifest:
        status = str(item.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    print(json.dumps({"repaired": changed, "counts": counts}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
