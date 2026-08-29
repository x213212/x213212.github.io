#!/usr/bin/env python3
"""Mirror image/media files referenced by the Blogger import into site/assets.

Every failed item stays referenced remotely by the site builder and is recorded
in data/media-manifest.json.  This makes the migration reviewable instead of
turning a transient network failure into a broken article image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen


USER_AGENT = "Mozilla/5.0 (compatible; BlogMigration/1.0; +https://github.com/)"
CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/avif": ".avif",
    "image/svg+xml": ".svg",
    "image/x-icon": ".ico",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "audio/mpeg": ".mp3",
    "audio/ogg": ".ogg",
    "audio/wav": ".wav",
}
SAFE_EXTENSIONS = set(CONTENT_TYPE_EXTENSIONS.values()) | {".jpeg", ".bmp", ".tiff", ".mp3", ".wav"}


def extension_for(url: str, content_type: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in SAFE_EXTENSIONS:
        return suffix
    content_type = content_type.split(";", 1)[0].strip().lower()
    return CONTENT_TYPE_EXTENSIONS.get(content_type) or mimetypes.guess_extension(content_type) or ".bin"


def mirror_one(item: dict[str, Any], output_dir: Path, max_bytes: int) -> dict[str, Any]:
    url = item["url"]
    result = dict(item)
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "image/avif,image/webp,image/*,*/*;q=0.8"})
    try:
        with urlopen(request, timeout=90) as response:
            content_type = response.headers.get("Content-Type", "")
            length = response.headers.get("Content-Length")
            if length and int(length) > max_bytes:
                result.update(status="too_large", error=f"content-length {length} exceeds {max_bytes} bytes")
                return result
            payload = response.read(max_bytes + 1)
        if len(payload) > max_bytes:
            result.update(status="too_large", error=f"download exceeds {max_bytes} bytes")
            return result

        extension = extension_for(url, content_type)
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
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
            content_type=content_type.split(";", 1)[0].strip().lower(),
        )
        result.pop("error", None)
    except Exception as error:  # Keep the remote URL in the generated site.
        result.update(status="failed", error=f"{type(error).__name__}: {error}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--max-bytes", type=int, default=20_000_000)
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument(
        "--url",
        action="append",
        default=[],
        help="Mirror only this exact manifest URL (repeatable).",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    manifest_path = root / "data" / "media-manifest.json"
    output_dir = root / "site" / "assets" / "media"
    items = json.loads(manifest_path.read_text(encoding="utf-8"))
    targets = [
        item
        for item in items
        if item.get("status") == "pending" or (args.retry_failed and item.get("status") == "failed")
    ]
    if args.url:
        selected = set(args.url)
        targets = [item for item in targets if item["url"] in selected]
        missing = selected - {item["url"] for item in targets} - {
            item["url"] for item in items if item.get("status") == "downloaded"
        }
        if missing:
            parser.error(f"No pending/failed manifest entry for: {', '.join(sorted(missing))}")

    results: dict[str, dict[str, Any]] = {item["url"]: item for item in items}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(mirror_one, item, output_dir, args.max_bytes): item["url"] for item in targets}
        for future in as_completed(futures):
            item = future.result()
            results[item["url"]] = item
            print(f"{item['status']:10} {item['url']}")

    ordered = [results[item["url"]] for item in items]
    manifest_path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for item in ordered:
        counts[item.get("status", "unknown")] = counts.get(item.get("status", "unknown"), 0) + 1
    print(json.dumps(counts, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
