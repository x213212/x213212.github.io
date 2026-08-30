#!/usr/bin/env python3
"""Generate small, deterministic WebP thumbnails for post-list cards.

Article images are served from ``assets/media-optimized`` at a readable
maximum edge of 1920 pixels.  A post list needs a different derivative: one
small, lazy-loadable image per post.  This tool reads the *written* optimized
media report, selects the same first usable image that the site builder uses
for each post, and writes a <=480px WebP derivative to
``site/assets/media-thumbnails``.

The original download cache is read-only here.  The output name is the stable
source-media ID already used by the optimizer, so thumbnails are deterministic
and cannot collide with locally uploaded Snowflake-named files.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
import markdown as markdown_library

try:
    from PIL import Image, ImageOps, UnidentifiedImageError
except ImportError as error:  # pragma: no cover - surfaced as an actionable message
    raise SystemExit("Pillow is required. Run: python3 -m pip install -r requirements.txt") from error

from build_site import load_editable_posts
from import_blogger import normalize_asset_url


REPORT_VERSION = 1
DEFAULT_MAX_DIMENSION = 480
DEFAULT_QUALITY = 82


def safe_site_path(root: Path, value: str, prefix: tuple[str, ...]) -> Path | None:
    """Resolve a report path only when it remains inside the expected asset tree."""
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.parts[: len(prefix)] != prefix:
        return None
    path = root / "site" / candidate
    try:
        path.resolve().relative_to((root / "site").resolve())
    except ValueError:
        return None
    return path


def optimization_sources(root: Path) -> dict[str, dict[str, Any]]:
    """Return source URL -> verified optimized asset record.

    A thumbnail must never point at a partial or dry-run optimizer output.  A
    report item is usable only when its source URL and on-disk optimized asset
    are both present.
    """
    report_path = root / "data" / "media-optimization-report.json"
    if not report_path.exists():
        raise RuntimeError(
            "Missing data/media-optimization-report.json. Run: python3 tools/optimize_media.py --write"
        )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("mode") != "write":
        raise RuntimeError(
            "The media optimizer report is only a dry run. Run: python3 tools/optimize_media.py --write"
        )

    result: dict[str, dict[str, Any]] = {}
    for item in report.get("items", []):
        if item.get("status") not in {"optimized", "copied"}:
            continue
        source_url = str(item.get("url", "")).strip()
        source_path = safe_site_path(
            root,
            str(item.get("optimized_local_path", "")).strip(),
            ("assets", "media-optimized"),
        )
        source_id = str(item.get("source_id", "")).strip()
        if not source_url or not source_path or not source_path.is_file() or not source_id:
            continue
        result[source_url] = {**item, "_source_path": source_path}
    if not result:
        raise RuntimeError(
            "The optimized media report has no usable output assets. Run the optimizer again without --limit."
        )
    return result


def upload_sources(root: Path) -> dict[str, dict[str, Any]]:
    """Return source URL -> record for images added through the local editor.

    Uploads never pass through the media optimizer - they are already local -
    so without this they would have no thumbnail, and a post card would show a
    full-size article image scaled down to a 148 px box by the browser.
    """
    directory = root / "site" / "assets" / "uploads"
    if not directory.is_dir():
        return {}
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            continue
        url = f"/assets/uploads/{path.name}"
        result[url] = {
            "source_id": path.stem,
            "optimized_local_path": f"assets/uploads/{path.name}",
            "_source_path": path,
        }
    return result


def signed_hackmd_preview(source: str) -> bool:
    """Match the site builder's treatment of expired HackMD preview URLs."""
    parsed = urlsplit(source)
    host = (parsed.hostname or "").casefold()
    query = parsed.query.casefold()
    return host.startswith("hackmd-prod-images.") and (
        "expires=" in query or "x-amz-expires=" in query
    )


def rendered_images(markdown_source: str) -> list[tuple[str, str]]:
    """Return article images in the order they will render on the site."""
    # Imported posts use JSON-compatible front matter; local drafts work too
    # because all front matter ends at the same explicit marker.
    body = markdown_source
    if body.startswith("---\n"):
        marker = body.find("\n---\n", 4)
        if marker != -1:
            body = body[marker + len("\n---\n") :]
    rendered = markdown_library.markdown(
        body,
        extensions=["extra", "sane_lists", "toc"],
        output_format="html5",
    )
    soup = BeautifulSoup(rendered, "html.parser")
    result: list[tuple[str, str]] = []
    for image in soup.find_all("img", src=True):
        raw = str(image.get("src", "")).strip()
        # normalize_asset_url is the importer's rule - remote media only, because
        # that is what it downloads. A thumbnail can come from a local upload too.
        source = raw if raw.startswith("/assets/") else normalize_asset_url(raw)
        if source:
            result.append((source, str(image.get("alt") or "")))
    return result


def thumbnail_dimensions(image: Image.Image, maximum: int) -> tuple[int, int]:
    width, height = image.size
    longest = max(width, height)
    if longest <= maximum:
        return width, height
    scale = maximum / longest
    return max(1, round(width * scale)), max(1, round(height * scale))


def thumbnail_one(
    source_path: Path,
    destination: Path,
    maximum: int,
    quality: int,
    force: bool,
) -> tuple[str, int, int, int, str | None]:
    """Create or reuse a stable static WebP thumbnail without touching source."""
    if destination.is_file() and not force:
        try:
            with Image.open(destination) as existing:
                existing.load()
                width, height = existing.size
            return "reused", destination.stat().st_size, width, height, None
        except (UnidentifiedImageError, OSError, ValueError):
            # Regenerate a corrupt prior derivative atomically below.
            pass

    try:
        with Image.open(source_path) as opened:
            # For animated input use the first frame as a light, predictable
            # list-card cover; the full animation remains untouched in articles.
            try:
                opened.seek(0)
            except EOFError:
                pass
            image = ImageOps.exif_transpose(opened)
            if image is opened:
                image = image.copy()
            if image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info):
                if image.mode != "RGBA":
                    image = image.convert("RGBA")
            elif image.mode != "RGB":
                image = image.convert("RGB")
            width, height = thumbnail_dimensions(image, maximum)
            if image.size != (width, height):
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".webp", delete=False) as handle:
                temporary = Path(handle.name)
            try:
                image.save(temporary, format="WEBP", quality=quality, method=6)
                os.replace(temporary, destination)
                destination.chmod(0o644)
            finally:
                temporary.unlink(missing_ok=True)
        return "generated", destination.stat().st_size, width, height, None
    except Exception as error:
        return "error", 0, 0, 0, f"{type(error).__name__}: {error}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--max-dimension", type=int, default=DEFAULT_MAX_DIMENSION)
    parser.add_argument("--quality", type=int, default=DEFAULT_QUALITY)
    parser.add_argument("--force", action="store_true", help="regenerate already-valid thumbnail files")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("site/assets/media-thumbnails"),
        help="directory relative to the project root",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/media-thumbnail-report.json"),
        help="report path relative to the project root",
    )
    args = parser.parse_args()
    if args.max_dimension < 64:
        parser.error("--max-dimension must be at least 64")
    if not 1 <= args.quality <= 100:
        parser.error("--quality must be in the range 1-100")

    root = args.root.resolve()
    output_directory = (root / args.output_dir).resolve() if not args.output_dir.is_absolute() else args.output_dir.resolve()
    report_path = (root / args.report).resolve() if not args.report.is_absolute() else args.report.resolve()
    try:
        output_directory.relative_to((root / "site").resolve())
    except ValueError:
        parser.error("--output-dir must be inside site/ so the static builder can deploy it safely")

    # Optimizer output first; a local upload only fills a gap it leaves.
    sources = {**upload_sources(root), **optimization_sources(root)}
    posts = [post for post in load_editable_posts(root) if not post.get("draft")]
    items: list[dict[str, Any]] = []
    emitted: set[str] = set()
    for index, post in enumerate(posts, start=1):
        selected: dict[str, Any] | None = None
        skipped: list[str] = []
        for source_url, alt in rendered_images(post["content"]):
            if signed_hackmd_preview(source_url):
                skipped.append("expired signed HackMD preview")
                continue
            candidate = sources.get(source_url)
            if candidate is None:
                skipped.append("no local optimized asset")
                continue
            selected = {**candidate, "_source_url": source_url, "_alt": alt}
            break

        record: dict[str, Any] = {
            "route": str(post["route"]),
            "title": str(post["title"]),
        }
        if selected is None:
            record.update(
                {
                    "status": "missing",
                    "reason": "No usable local article image" + (f" ({'; '.join(dict.fromkeys(skipped))})" if skipped else ""),
                }
            )
            items.append(record)
            continue

        source_id = str(selected["source_id"])
        relative = Path("assets") / "media-thumbnails" / f"{source_id}.webp"
        destination = root / "site" / relative
        status, output_bytes, width, height, error = thumbnail_one(
            Path(selected["_source_path"]),
            destination,
            args.max_dimension,
            args.quality,
            args.force,
        )
        record.update(
            {
                "source_url": selected["_source_url"],
                "source_id": source_id,
                "source_optimized_local_path": str(selected["optimized_local_path"]),
                "thumbnail_local_path": relative.as_posix(),
                "thumbnail_alt": selected["_alt"] or str(post["title"]),
                "status": "ready" if status in {"generated", "reused"} else status,
                "generation": status,
            }
        )
        if status in {"generated", "reused"}:
            record.update(
                {
                    "thumbnail_bytes": output_bytes,
                    "thumbnail_width": width,
                    "thumbnail_height": height,
                }
            )
            emitted.add(relative.as_posix())
        else:
            record["reason"] = error or "thumbnail generation failed"
        items.append(record)
        if index == 1 or index % 50 == 0 or index == len(posts):
            print(f"processed {index}/{len(posts)} posts", flush=True)

    counts = Counter(str(item.get("status", "unknown")) for item in items)
    ready = [item for item in items if item.get("status") == "ready"]
    report = {
        "version": REPORT_VERSION,
        "mode": "write",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_report": "data/media-optimization-report.json",
        "output_directory": output_directory.relative_to(root).as_posix(),
        "settings": {
            "format": "webp",
            "quality": args.quality,
            "max_dimension": args.max_dimension,
            "selection": "first locally optimized article image; signed HackMD previews skipped",
        },
        "summary": {
            "published_posts": len(posts),
            "ready_post_thumbnails": len(ready),
            "missing_post_thumbnails": len(items) - len(ready),
            "unique_thumbnail_files": len(emitted),
            "thumbnail_bytes": sum(int(item.get("thumbnail_bytes", 0) or 0) for item in ready),
            "status_counts": dict(sorted(counts.items())),
        },
        "items": items,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=report_path.parent, suffix=".json", delete=False, mode="w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary_report = Path(handle.name)
    try:
        os.replace(temporary_report, report_path)
        report_path.chmod(0o644)
    finally:
        temporary_report.unlink(missing_ok=True)

    summary = report["summary"]
    print(
        json.dumps(
            {
                "published_posts": summary["published_posts"],
                "ready": summary["ready_post_thumbnails"],
                "missing": summary["missing_post_thumbnails"],
                "unique_files": summary["unique_thumbnail_files"],
                "bytes": summary["thumbnail_bytes"],
                "report": report_path.relative_to(root).as_posix(),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
