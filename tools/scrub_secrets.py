#!/usr/bin/env python3
"""Redact credentials that were published in the archive.

Every secret is listed explicitly below rather than matched by a pattern: a
regex that rewrites unknown text across 379 posts is a good way to corrupt an
article, and the point here is a small, reviewable, auditable edit.

Each secret is replaced by a masked form that keeps its head and tail, so the
prose still reads as intended ("this is what the key looks like") while the
value itself is useless. The replacement is applied everywhere the archive keeps
a copy - the Markdown source, the immutable import record, and the HackMD
mirror - because scrubbing only one of them leaves the secret published.

The plaintext values are read from ``data/secrets-to-scrub.local.json``, which is
gitignored. Hard-coding them in this file would commit the very strings the tool
exists to remove.

Redacting here does not un-publish anything. The key must be revoked and the
password changed at the provider first; this only stops re-publishing it.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SECRETS_FILE = Path("data") / "secrets-to-scrub.local.json"


def load_secrets(root: Path) -> list[tuple[str, int, int, str]]:
    """Read the plaintext values from the gitignored local list."""
    path = root / SECRETS_FILE
    if not path.is_file():
        raise SystemExit(
            f"missing {SECRETS_FILE}. Create it with a 'secrets' list of "
            "{value, head, tail, note} objects; it is gitignored on purpose."
        )
    entries = json.loads(path.read_text(encoding="utf-8")).get("secrets", [])
    if not entries:
        raise SystemExit(f"{SECRETS_FILE} lists no secrets.")
    return [
        (str(entry["value"]), int(entry.get("head", 4)), int(entry.get("tail", 4)), str(entry.get("note", "secret")))
        for entry in entries
    ]


SEARCH_ROOTS = (
    Path("content") / "posts",
    Path("source") / "hackmd",
)
JSON_RECORDS = (Path("data") / "posts.json",)


def masked(secret: str, head: int, tail: int) -> str:
    """Keep the head and tail so the text still reads, drop the middle."""
    if head + tail >= len(secret):
        raise ValueError(f"mask would reveal the whole secret: {secret[:6]}…")
    return f"{secret[:head]}…{secret[-tail:]}"


def scrub_text(text: str, replacements: list[tuple[str, str]]) -> tuple[str, int]:
    total = 0
    for secret, replacement in replacements:
        count = text.count(secret)
        if count:
            text = text.replace(secret, replacement)
            total += count
    return text, total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dry-run", action="store_true", help="Report without writing.")
    args = parser.parse_args()
    root = args.root.resolve()

    secrets = load_secrets(root)
    replacements = [(secret, masked(secret, head, tail)) for secret, head, tail, _ in secrets]
    for (secret, _, _, note), (_, replacement) in zip(secrets, replacements):
        print(f"{note}: {replacement}")
    print()

    targets: list[Path] = []
    for folder in SEARCH_ROOTS:
        targets.extend(sorted((root / folder).glob("*.md")))
    targets.extend(root / record for record in JSON_RECORDS)

    changed_files = 0
    total_hits = 0
    remaining: list[str] = []
    for path in targets:
        if not path.is_file():
            continue
        original = path.read_text(encoding="utf-8")
        updated, hits = scrub_text(original, replacements)
        if not hits:
            continue
        total_hits += hits
        changed_files += 1
        print(f"  {hits:3} × {path.relative_to(root)}")
        if not args.dry_run:
            path.write_text(updated, encoding="utf-8")

    if not args.dry_run:
        # A JSON record must still parse after a textual replacement.
        for record in JSON_RECORDS:
            path = root / record
            if path.is_file():
                json.loads(path.read_text(encoding="utf-8"))

        for path in targets:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            remaining.extend(
                f"{path.relative_to(root)} still contains {note}"
                for secret, _, _, note in secrets
                if secret in text
            )

    print(f"\nreplacements={total_hits} files={changed_files}")
    if remaining:
        for line in remaining:
            print(f"  LEFTOVER: {line}")
        return 1
    if not args.dry_run:
        print("Rebuild the site so docs/ stops serving the old values:")
        print("  python3 tools/build_site.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
