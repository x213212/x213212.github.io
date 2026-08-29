#!/usr/bin/env python3
"""Turn the published site into a maintenance notice, and back again.

GitHub Pages serves whatever the workflow last deployed, and that workflow
rebuilds ``docs/`` from source on every push. So a maintenance page cannot be
dropped into ``docs/`` by hand - the next build would erase it. Instead this
flips a flag in ``data/site-config.json``; ``build_site.py`` reads it and emits
the notice instead of the archive, which means the switch survives CI and is
turned off the same way it was turned on.

    python3 tools/maintenance_mode.py --on
    python3 tools/maintenance_mode.py --on --message "Restoring the media mirror"
    python3 tools/maintenance_mode.py --off
    python3 tools/maintenance_mode.py --status

Nothing is published until the change is committed and pushed.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CONFIG = Path("data") / "site-config.json"
DEFAULT_HEADING = "Under maintenance"
DEFAULT_MESSAGE = "The archive is being rebuilt and will be back shortly."


def load(root: Path) -> dict:
    path = root / CONFIG
    if not path.is_file():
        raise SystemExit(f"missing {CONFIG}")
    return json.loads(path.read_text(encoding="utf-8"))


def save(root: Path, config: dict) -> None:
    path = root / CONFIG
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def describe(config: dict) -> str:
    maintenance = config.get("maintenance", {})
    if not maintenance.get("enabled"):
        return "maintenance mode is OFF - the site publishes the archive"
    since = maintenance.get("since", "unknown")
    return (
        "maintenance mode is ON\n"
        f"  heading: {maintenance.get('heading', DEFAULT_HEADING)}\n"
        f"  message: {maintenance.get('message', DEFAULT_MESSAGE)}\n"
        f"  since:   {since}"
    )


def rebuild(root: Path) -> None:
    result = subprocess.run(
        [sys.executable, "tools/build_site.py", "--root", str(root)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "")
    if result.returncode != 0:
        raise SystemExit("build failed; the config change was still written")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--on", action="store_true", help="Publish the maintenance notice instead of the archive.")
    mode.add_argument("--off", action="store_true", help="Publish the archive again.")
    mode.add_argument("--status", action="store_true", help="Report the current state and exit.")
    parser.add_argument("--heading", default=DEFAULT_HEADING)
    parser.add_argument("--message", default=DEFAULT_MESSAGE)
    parser.add_argument("--no-build", action="store_true", help="Only change the config; do not rebuild docs/.")
    args = parser.parse_args()
    root = args.root.resolve()
    config = load(root)

    if args.status:
        print(describe(config))
        return 0

    if args.on:
        config["maintenance"] = {
            "enabled": True,
            "heading": args.heading,
            "message": args.message,
            "since": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    else:
        config["maintenance"] = {"enabled": False}

    save(root, config)
    print(describe(config))
    if not args.no_build:
        rebuild(root)
    print("\nCommit and push to apply it to the published site:")
    print("  git add data/site-config.json && git commit -m 'Toggle maintenance mode' && git push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
