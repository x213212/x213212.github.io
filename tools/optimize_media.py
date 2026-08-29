#!/usr/bin/env python3
"""Create a deployable optimized media mirror without touching original media.

``site/assets/media/`` is the lossless download cache made by
``download_media.py``.  This tool only reads that cache and writes a separate
``site/assets/media-optimized/`` directory plus a report.  It intentionally
does *not* change ``data/media-manifest.json``: the manifest remains the
auditable record of what was downloaded from the public site.

The default operation is a sampled dry run.  It estimates the result before
any image is written.  Use ``--write`` only after reviewing the report.
"""

from __future__ import annotations

import argparse
import json
import math
import mimetypes
import os
import shutil
import tempfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from PIL import Image, ImageOps, UnidentifiedImageError
except ImportError as error:  # pragma: no cover - surfaced as a helpful CLI error
    raise SystemExit("Pillow is required. Run: python3 -m pip install -r requirements.txt") from error


REPORT_VERSION = 1
DEFAULT_MAX_DIMENSION = 1920
DEFAULT_QUALITY = 88
DEFAULT_SAMPLE_SIZE = 48
RASTER_FORMATS = {"JPEG", "PNG", "WEBP", "GIF", "BMP", "TIFF"}
FORMAT_EXTENSIONS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
    "GIF": ".gif",
    "BMP": ".bmp",
    "TIFF": ".tiff",
}
FORMAT_MIME_TYPES = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
    "GIF": "image/gif",
    "BMP": "image/bmp",
    "TIFF": "image/tiff",
}


@dataclass(frozen=True)
class Asset:
    """One immutable source asset described by the existing media manifest."""

    url: str
    source_path: Path
    source_local_path: str
    source_bytes: int


@dataclass(frozen=True)
class Inspection:
    asset: Asset
    image_format: str | None
    width: int | None
    height: int | None
    frames: int | None
    action: str
    reason: str

    @property
    def needs_resize(self) -> bool:
        return bool(self.width and self.height and max(self.width, self.height) > 0)


def bytes_text(value: int | float) -> str:
    """Render bytes compactly for CLI output without losing machine data in JSON."""
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if amount < 1024 or unit == "GiB":
            return f"{amount:.1f} {unit}" if unit != "B" else f"{amount:.0f} {unit}"
        amount /= 1024
    return f"{amount:.1f} GiB"


def percent(saved: int | float, total: int | float) -> float:
    return round(100 * float(saved) / float(total), 2) if total else 0.0


def safe_relative_path(value: str) -> Path:
    """Make a manifest-provided path safe to resolve below ``site/``."""
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe local media path in manifest: {value!r}")
    return path


def load_downloaded_assets(root: Path) -> tuple[list[Asset], list[dict[str, Any]]]:
    """Read downloaded manifest entries without writing or reordering them."""
    manifest_path = root / "data" / "media-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assets: list[Asset] = []
    missing: list[dict[str, Any]] = []
    for item in manifest:
        if item.get("status") != "downloaded" or not item.get("local_path"):
            continue
        source_local_path = str(item["local_path"])
        try:
            source_path = root / "site" / safe_relative_path(source_local_path)
        except ValueError as error:
            missing.append(
                {
                    "url": str(item.get("url", "")),
                    "source_local_path": source_local_path,
                    "status": "missing",
                    "reason": str(error),
                }
            )
            continue
        if not source_path.is_file():
            missing.append(
                {
                    "url": str(item.get("url", "")),
                    "source_local_path": source_local_path,
                    "status": "missing",
                    "reason": "downloaded file is absent from the original media cache",
                }
            )
            continue
        assets.append(
            Asset(
                url=str(item["url"]),
                source_path=source_path,
                source_local_path=source_local_path,
                source_bytes=source_path.stat().st_size,
            )
        )
    return assets, missing


def inspect_asset(asset: Asset, max_dimension: int) -> Inspection:
    """Determine whether an asset can be safely optimized or must be preserved."""
    try:
        with Image.open(asset.source_path) as image:
            image_format = (image.format or "").upper() or None
            width, height = image.size
            frames = int(getattr(image, "n_frames", 1))
    except (UnidentifiedImageError, OSError, ValueError) as error:
        return Inspection(asset, None, None, None, None, "skipped", f"not a readable raster image: {type(error).__name__}")

    if image_format not in RASTER_FORMATS:
        return Inspection(asset, image_format, width, height, frames, "skipped", "unsupported or non-raster image format")
    if image_format == "GIF" and frames > 1:
        # Animated WebP keeps every frame, so the animation survives while the
        # file stops costing megabytes; a byte-for-byte copy is the fallback.
        return Inspection(asset, image_format, width, height, frames, "animated", "animated GIF re-encoded as animated WebP")
    if max(width, height) <= 0:
        return Inspection(asset, image_format, width, height, frames, "skipped", "invalid image dimensions")
    return Inspection(asset, image_format, width, height, frames, "eligible", "static raster image")


def bucket(inspection: Inspection, max_dimension: int) -> str:
    """Use coarse, transparent groups so dry-run sampling is representative."""
    format_name = inspection.image_format or "unknown"
    resized = bool(
        inspection.width
        and inspection.height
        and max(inspection.width, inspection.height) > max_dimension
    )
    return f"{format_name}:{'resized' if resized else 'native'}"


def representative_samples(
    eligible: Iterable[Inspection], sample_size: int, max_dimension: int
) -> list[Inspection]:
    """Select a stable, byte-weighted sample from every format/dimension group."""
    groups: dict[str, list[Inspection]] = defaultdict(list)
    for item in eligible:
        groups[bucket(item, max_dimension)].append(item)
    total_count = sum(len(items) for items in groups.values())
    total_bytes = sum(item.asset.source_bytes for items in groups.values() for item in items)
    if not total_count or not total_bytes or sample_size <= 0:
        return []

    target = min(sample_size, total_count)
    selected: list[Inspection] = []
    remainders: list[tuple[float, str]] = []
    allocations: dict[str, int] = {}
    if target < len(groups):
        # An unusually tiny sample cannot cover every group; choose the
        # largest byte groups deterministically instead of exceeding the request.
        for key in sorted(
            groups,
            key=lambda value: (-sum(item.asset.source_bytes for item in groups[value]), value),
        )[:target]:
            allocations[key] = 1
        groups = {key: groups[key] for key in allocations}
    else:
        for key, items in groups.items():
            group_bytes = sum(item.asset.source_bytes for item in items)
            exact = target * group_bytes / total_bytes
            # Include each group whenever the requested sample can accommodate it.
            amount = min(len(items), max(1, math.floor(exact)))
            allocations[key] = amount
            remainders.append((exact - math.floor(exact), key))

    while sum(allocations.values()) > target:
        candidates = sorted(
            (key for key, amount in allocations.items() if amount > 1),
            key=lambda key: (len(groups[key]), key),
        )
        if not candidates:
            break
        allocations[candidates[0]] -= 1
    for _, key in sorted(remainders, reverse=True):
        if sum(allocations.values()) >= target:
            break
        if allocations[key] < len(groups[key]):
            allocations[key] += 1

    for key, items in groups.items():
        # Pick source-byte quantiles: a tiny icon does not get the same vote
        # as a 5 MiB camera image when predicting deployment bandwidth.
        ordered = sorted(items, key=lambda value: (value.asset.source_bytes, value.asset.source_path.name))
        amount = allocations[key]
        if amount >= len(ordered):
            selected.extend(ordered)
            continue
        total_group_bytes = sum(item.asset.source_bytes for item in ordered)
        indexes: list[int] = []
        cumulative = 0
        cursor = 0
        for sample_index in range(amount):
            target_bytes = (sample_index + 0.5) * total_group_bytes / amount
            while cursor < len(ordered) - 1 and cumulative + ordered[cursor].asset.source_bytes < target_bytes:
                cumulative += ordered[cursor].asset.source_bytes
                cursor += 1
            candidate = cursor
            # Make each measured asset unique; a very large source can span
            # several byte quantiles, but measuring it only once is enough.
            if candidate in indexes:
                for offset in range(1, len(ordered)):
                    before = candidate - offset
                    after = candidate + offset
                    if before >= 0 and before not in indexes:
                        candidate = before
                        break
                    if after < len(ordered) and after not in indexes:
                        candidate = after
                        break
            indexes.append(candidate)
        selected.extend(ordered[index] for index in sorted(indexes))
    return selected


def output_dimensions(width: int, height: int, max_dimension: int) -> tuple[int, int]:
    longest = max(width, height)
    if longest <= max_dimension:
        return width, height
    scale = max_dimension / longest
    return max(1, round(width * scale)), max(1, round(height * scale))


def image_has_alpha(image: Image.Image) -> bool:
    if image.mode in {"RGBA", "LA"}:
        return True
    return image.mode == "P" and "transparency" in image.info


def source_extension(inspection: Inspection) -> str:
    """Choose an extension from decoded bytes, not a potentially wrong URL header."""
    return FORMAT_EXTENSIONS.get(inspection.image_format or "", inspection.asset.source_path.suffix.lower() or ".bin")


def source_mime_type(inspection: Inspection) -> str:
    return FORMAT_MIME_TYPES.get(
        inspection.image_format or "",
        mimetypes.guess_type(inspection.asset.source_path.name)[0] or "application/octet-stream",
    )


def encode_webp(source: Path, destination: Path, max_dimension: int, quality: int) -> tuple[int, int]:
    """Render one static image with orientation, alpha, and dimensions preserved."""
    with Image.open(source) as opened:
        opened.load()
        image = ImageOps.exif_transpose(opened)
        # Ensure the output remains valid after the source file closes, and
        # normalize modes Pillow's WebP encoder does not consistently accept.
        if image is opened:
            image = image.copy()
        if image_has_alpha(image):
            if image.mode != "RGBA":
                image = image.convert("RGBA")
        elif image.mode != "RGB":
            image = image.convert("RGB")
        width, height = output_dimensions(*image.size, max_dimension)
        if image.size != (width, height):
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        image.save(destination, format="WEBP", quality=quality, method=6)
    return width, height


def encode_animated_webp(source: Path, destination: Path, max_dimension: int, quality: int) -> tuple[int, int]:
    """Re-encode every frame of an animation into a single animated WebP."""
    from PIL import ImageSequence

    with Image.open(source) as opened:
        frames: list[Image.Image] = []
        durations: list[int] = []
        width = height = 0
        for frame in ImageSequence.Iterator(opened):
            converted = frame.convert("RGBA")
            if not width:
                width, height = output_dimensions(*converted.size, max_dimension)
            if converted.size != (width, height):
                converted = converted.resize((width, height), Image.Resampling.LANCZOS)
            frames.append(converted)
            durations.append(int(frame.info.get("duration", 100)))
        if not frames:
            raise ValueError("animation contained no frames")
        frames[0].save(
            destination,
            format="WEBP",
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=int(opened.info.get("loop", 0)),
            quality=quality,
            method=4,
            minimize_size=True,
        )
    return width, height


def write_animated(
    inspection: Inspection,
    output_directory: Path,
    root: Path,
    max_dimension: int,
    quality: int,
) -> dict[str, Any]:
    """Write an animated WebP, falling back to the untouched GIF if it is larger."""
    temporary = temporary_path(output_directory, ".webp")
    try:
        output_width, output_height = encode_animated_webp(
            inspection.asset.source_path, temporary, max_dimension, quality
        )
        webp_bytes = temporary.stat().st_size
        if webp_bytes < inspection.asset.source_bytes:
            destination = output_directory / f"{inspection.asset.source_path.stem}.webp"
            os.replace(temporary, destination)
            destination.chmod(0o644)
            temporary = None
            return output_record(
                inspection,
                destination,
                root,
                "optimized",
                webp_bytes,
                "image/webp",
                output_width,
                output_height,
            )
    except Exception:  # A stubborn animation is preserved rather than dropped.
        pass
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return copy_preserved(inspection, output_directory, root)


def temporary_path(directory: Path, suffix: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(dir=directory, suffix=suffix, delete=False)
    handle.close()
    return Path(handle.name)


def preview_eligible(inspection: Inspection, temporary_directory: Path, max_dimension: int, quality: int) -> dict[str, Any]:
    """Actually encode a sample to obtain a measured, not guessed, ratio."""
    temporary = temporary_path(temporary_directory, ".webp")
    try:
        output_width, output_height = encode_webp(inspection.asset.source_path, temporary, max_dimension, quality)
        webp_bytes = temporary.stat().st_size
    except Exception as error:  # Keep a readable original if a decoder rejects one edge case.
        return {
            "status": "copied",
            "output_bytes": inspection.asset.source_bytes,
            "output_extension": source_extension(inspection),
            "output_mime_type": source_mime_type(inspection),
            "width": inspection.width,
            "height": inspection.height,
            "reason": f"WebP encoding failed; source format retained ({type(error).__name__})",
        }
    finally:
        temporary.unlink(missing_ok=True)
    if webp_bytes < inspection.asset.source_bytes:
        return {
            "status": "optimized",
            "output_bytes": webp_bytes,
            "output_extension": ".webp",
            "output_mime_type": "image/webp",
            "width": output_width,
            "height": output_height,
        }
    return {
        "status": "copied",
        "output_bytes": inspection.asset.source_bytes,
        "output_extension": source_extension(inspection),
        "output_mime_type": source_mime_type(inspection),
        "width": inspection.width,
        "height": inspection.height,
        "reason": "WebP was not smaller; source format retained",
    }


def write_eligible(
    inspection: Inspection,
    output_directory: Path,
    root: Path,
    max_dimension: int,
    quality: int,
) -> dict[str, Any]:
    """Atomically write one optimized image, falling back to a source copy."""
    temporary = temporary_path(output_directory, ".webp")
    fallback_reason = "WebP was not smaller; source format retained"
    try:
        output_width, output_height = encode_webp(inspection.asset.source_path, temporary, max_dimension, quality)
        webp_bytes = temporary.stat().st_size
        if webp_bytes < inspection.asset.source_bytes:
            destination = output_directory / f"{inspection.asset.source_path.stem}.webp"
            os.replace(temporary, destination)
            destination.chmod(0o644)
            temporary = None  # ownership transferred by os.replace
            return output_record(
                inspection,
                destination,
                root,
                "optimized",
                webp_bytes,
                "image/webp",
                output_width,
                output_height,
            )
    except Exception as error:  # A single malformed image must not stop the archive build.
        fallback_reason = f"WebP encoding failed; source format retained ({type(error).__name__})"
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

    destination = output_directory / f"{inspection.asset.source_path.stem}{source_extension(inspection)}"
    temporary_copy = temporary_path(output_directory, source_extension(inspection))
    try:
        shutil.copyfile(inspection.asset.source_path, temporary_copy)
        os.replace(temporary_copy, destination)
        destination.chmod(0o644)
    finally:
        temporary_copy.unlink(missing_ok=True)
    return output_record(
        inspection,
        destination,
        root,
        "copied",
        inspection.asset.source_bytes,
        source_mime_type(inspection),
        inspection.width,
        inspection.height,
        fallback_reason,
    )


def copy_preserved(inspection: Inspection, output_directory: Path, root: Path) -> dict[str, Any]:
    """Copy animation byte-for-byte so optimized mode never removes movement."""
    destination = output_directory / f"{inspection.asset.source_path.stem}{source_extension(inspection)}"
    temporary = temporary_path(output_directory, source_extension(inspection))
    try:
        shutil.copyfile(inspection.asset.source_path, temporary)
        os.replace(temporary, destination)
        destination.chmod(0o644)
    finally:
        temporary.unlink(missing_ok=True)
    return output_record(
        inspection,
        destination,
        root,
        "copied",
        inspection.asset.source_bytes,
        source_mime_type(inspection),
        inspection.width,
        inspection.height,
        inspection.reason,
    )


def output_record(
    inspection: Inspection,
    destination: Path,
    root: Path,
    status: str,
    output_bytes: int,
    output_mime_type: str,
    width: int | None,
    height: int | None,
    reason: str | None = None,
) -> dict[str, Any]:
    record = record_base(inspection)
    record.update(
        {
            "status": status,
            "optimized_local_path": destination.relative_to(root / "site").as_posix(),
            "output_bytes": output_bytes,
            "output_mime_type": output_mime_type,
            "output_width": width,
            "output_height": height,
        }
    )
    if reason:
        record["reason"] = reason
    return record


def record_base(inspection: Inspection) -> dict[str, Any]:
    return {
        "url": inspection.asset.url,
        # Stable opaque ID inherited from the existing cache filename.  The
        # optimizer deliberately preserves this stem so historic media stays
        # addressable even when future uploads use a different (Snowflake)
        # naming scheme.
        "source_id": inspection.asset.source_path.stem,
        "source_local_path": inspection.asset.source_local_path,
        "source_bytes": inspection.asset.source_bytes,
        "source_format": inspection.image_format,
        "source_width": inspection.width,
        "source_height": inspection.height,
        "frames": inspection.frames,
    }


def skipped_record(inspection: Inspection) -> dict[str, Any]:
    record = record_base(inspection)
    record.update({"status": "skipped", "reason": inspection.reason})
    return record


def write_record(
    inspection: Inspection,
    output_directory: Path,
    root: Path,
    max_dimension: int,
    quality: int,
) -> dict[str, Any]:
    """Process one asset without allowing a single bad file to stop the batch."""
    try:
        if inspection.action == "eligible":
            return write_eligible(inspection, output_directory, root, max_dimension, quality)
        if inspection.action == "animated":
            return write_animated(inspection, output_directory, root, max_dimension, quality)
        if inspection.action == "copied":
            return copy_preserved(inspection, output_directory, root)
        return skipped_record(inspection)
    except Exception as error:
        record = record_base(inspection)
        record.update({"status": "error", "reason": f"optimizer write failed: {type(error).__name__}: {error}"})
        return record


def estimated_record(
    inspection: Inspection,
    output_bytes: int,
    max_dimension: int,
    status: str = "estimated",
) -> dict[str, Any]:
    record = record_base(inspection)
    width = inspection.width
    height = inspection.height
    if width and height:
        width, height = output_dimensions(width, height, max_dimension)
    record.update(
        {
            "status": status,
            "estimated_output_bytes": output_bytes,
            "estimated_output_mime_type": "image/webp",
            "estimated_output_width": width,
            "estimated_output_height": height,
        }
    )
    return record


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = temporary_path(path.parent, ".json")
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)
        path.chmod(0o644)
    finally:
        temporary.unlink(missing_ok=True)


def report_summary(items: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    status_counts = Counter(str(item.get("status", "unknown")) for item in items)
    # Skipped files remain remote; a limited pilot has not emitted the rest.
    # Excluding both from the baseline avoids pretending a five-file pilot
    # compressed the entire cache.
    emitted_candidates = [
        item
        for item in items
        if item.get("status") not in {"skipped", "missing", "not_processed", "error"}
    ]
    downloaded_sources = [item for item in items if item.get("source_bytes") is not None]
    downloaded_bytes = sum(int(item.get("source_bytes", 0) or 0) for item in downloaded_sources)
    source_bytes = sum(int(item.get("source_bytes", 0) or 0) for item in emitted_candidates)
    if mode == "write":
        output_bytes = sum(int(item.get("output_bytes", 0) or 0) for item in items)
        output_label = "output_bytes"
    else:
        output_bytes = sum(int(item.get("estimated_output_bytes", 0) or 0) for item in items)
        output_label = "estimated_output_bytes"
    saved = max(0, source_bytes - output_bytes)
    return {
        "downloaded_source_assets": len(downloaded_sources),
        "downloaded_source_bytes": downloaded_bytes,
        "source_assets": len(emitted_candidates),
        "source_bytes": source_bytes,
        output_label: output_bytes,
        "savings_bytes": saved,
        "savings_percent": percent(saved, source_bytes),
        "status_counts": dict(sorted(status_counts.items())),
    }


def print_summary(report: dict[str, Any]) -> None:
    summary = report["summary"]
    is_write = report["mode"] == "write"
    output_key = "output_bytes" if is_write else "estimated_output_bytes"
    heading = "Optimized media mirror" if is_write else "Media optimization dry run"
    print(heading)
    print(
        f"  source cache: {bytes_text(summary['downloaded_source_bytes'])} "
        f"across {summary['downloaded_source_assets']} downloaded assets"
    )
    if summary["source_assets"] != summary["downloaded_source_assets"]:
        print(
            f"  deployable:   {bytes_text(summary['source_bytes'])} "
            f"across {summary['source_assets']} raster/animation assets"
        )
    label = "output" if is_write else "projected output"
    print(f"  {label}: {bytes_text(summary[output_key])}")
    print(f"  savings: {bytes_text(summary['savings_bytes'])} ({summary['savings_percent']}%)")
    print(f"  states:  {json.dumps(summary['status_counts'], ensure_ascii=False, sort_keys=True)}")
    print(f"  report:  {report['report_path']}")
    if not is_write:
        print("  no files were written; rerun with --write after reviewing the report")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("site/assets/media-optimized"),
        help="directory relative to project root for deployable assets",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/media-optimization-report.json"),
        help="JSON report path relative to project root",
    )
    parser.add_argument("--max-dimension", type=int, default=DEFAULT_MAX_DIMENSION)
    parser.add_argument("--quality", type=int, default=DEFAULT_QUALITY, help="WebP quality, 1-100")
    parser.add_argument(
        "--workers",
        type=int,
        default=min(4, os.cpu_count() or 1),
        help="concurrent image encoders for --write (default: 4)",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help="representative assets measured in dry-run mode",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write the separate optimized media mirror")
    mode.add_argument("--dry-run", action="store_true", help="measure a sample only (the default)")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="process only this many downloaded assets (safe pilot; 0 means all)",
    )
    args = parser.parse_args()
    if args.max_dimension < 64:
        parser.error("--max-dimension must be at least 64")
    if not 1 <= args.quality <= 100:
        parser.error("--quality must be in the range 1-100")
    if args.sample < 1:
        parser.error("--sample must be at least 1")
    if args.limit < 0:
        parser.error("--limit cannot be negative")
    if args.workers < 1:
        parser.error("--workers must be at least 1")

    root = args.root.resolve()
    output_directory = (root / args.output_dir).resolve() if not args.output_dir.is_absolute() else args.output_dir.resolve()
    report_path = (root / args.report).resolve() if not args.report.is_absolute() else args.report.resolve()
    site_root = (root / "site").resolve()
    try:
        output_directory.relative_to(site_root)
    except ValueError:
        parser.error("--output-dir must be inside site/ so the static builder can deploy it safely")

    assets, missing = load_downloaded_assets(root)
    inspections = [inspect_asset(asset, args.max_dimension) for asset in assets]
    eligible = [item for item in inspections if item.action == "eligible"]
    preserved = [item for item in inspections if item.action in {"copied", "animated"}]
    skipped = [item for item in inspections if item.action == "skipped"]
    mode = "write" if args.write else "dry-run"

    items: list[dict[str, Any]] = []
    if args.write:
        selected = inspections if not args.limit else inspections[: args.limit]
        selected_names = {item.asset.source_path.name for item in selected}
        output_directory.mkdir(parents=True, exist_ok=True)
        written: dict[str, dict[str, Any]] = {}
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(write_record, inspection, output_directory, root, args.max_dimension, args.quality): inspection
                for inspection in selected
            }
            for index, future in enumerate(as_completed(futures), start=1):
                inspection = futures[future]
                written[inspection.asset.source_path.name] = future.result()
                if index == 1 or index % 25 == 0 or index == len(selected):
                    print(f"processed {index}/{len(selected)} assets", flush=True)
        items.extend(written[inspection.asset.source_path.name] for inspection in selected)
        for inspection in inspections:
            if inspection.asset.source_path.name in selected_names:
                continue
            record = record_base(inspection)
            record.update({"status": "not_processed", "reason": "excluded by --limit"})
            items.append(record)
    else:
        samples = representative_samples(eligible, args.sample, args.max_dimension)
        sampled: dict[str, dict[str, Any]] = {}
        with tempfile.TemporaryDirectory(prefix="coding-orz-media-preview-") as temporary_name:
            temporary_directory = Path(temporary_name)
            for index, inspection in enumerate(samples, start=1):
                sampled[inspection.asset.source_path.name] = preview_eligible(
                    inspection, temporary_directory, args.max_dimension, args.quality
                )
                if index == 1 or index % 10 == 0 or index == len(samples):
                    print(f"sampled {index}/{len(samples)} raster images", flush=True)

        ratios: dict[str, float] = {}
        bucket_sources: dict[str, int] = defaultdict(int)
        bucket_outputs: dict[str, int] = defaultdict(int)
        for inspection in samples:
            key = bucket(inspection, args.max_dimension)
            bucket_sources[key] += inspection.asset.source_bytes
            bucket_outputs[key] += int(sampled[inspection.asset.source_path.name]["output_bytes"])
        for key, source_bytes in bucket_sources.items():
            ratios[key] = min(1.0, bucket_outputs[key] / source_bytes) if source_bytes else 1.0

        for inspection in inspections:
            if inspection.action == "eligible":
                key = bucket(inspection, args.max_dimension)
                estimated = round(inspection.asset.source_bytes * ratios.get(key, 1.0))
                record = estimated_record(inspection, estimated, args.max_dimension)
                if inspection.asset.source_path.name in sampled:
                    measured = sampled[inspection.asset.source_path.name]
                    record.update(
                        {
                            "status": "sampled",
                            "estimated_output_bytes": measured["output_bytes"],
                            "estimated_output_mime_type": measured["output_mime_type"],
                            "estimated_output_width": measured["width"],
                            "estimated_output_height": measured["height"],
                        }
                    )
                    if measured.get("reason"):
                        record["reason"] = measured["reason"]
                items.append(record)
            elif inspection.action in {"copied", "animated"}:
                record = record_base(inspection)
                record.update(
                    {
                        "status": "preserved",
                        "estimated_output_bytes": inspection.asset.source_bytes,
                        "estimated_output_mime_type": source_mime_type(inspection),
                        "estimated_output_width": inspection.width,
                        "estimated_output_height": inspection.height,
                        "reason": inspection.reason,
                    }
                )
                items.append(record)
            else:
                items.append(skipped_record(inspection))

    # Include missing source files explicitly.  They are not emitted and stay
    # remote when optimized mode is selected in the static-site builder.
    items.extend(missing)
    summary = report_summary(items, mode)
    report = {
        "version": REPORT_VERSION,
        "mode": mode,
        "report_path": report_path.relative_to(root).as_posix() if report_path.is_relative_to(root) else str(report_path),
        "source_directory": "site/assets/media",
        "output_directory": output_directory.relative_to(root).as_posix(),
        "settings": {
            "format": "webp",
            "quality": args.quality,
            "max_dimension": args.max_dimension,
            "workers": args.workers if args.write else 0,
            "animated_gif": "copied-byte-for-byte",
            "non_images": "skipped-and-left-remote",
        },
        "sampling": {
            "requested": args.sample if not args.write else 0,
            "measured": len(samples) if not args.write else 0,
            "method": "stratified by source format and whether downscaling is required" if not args.write else "full actual run",
        },
        "summary": summary,
        "items": items,
    }
    atomic_write_json(report_path, report)
    print_summary(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
