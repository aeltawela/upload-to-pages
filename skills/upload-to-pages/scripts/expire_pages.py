#!/usr/bin/env python3
"""Remove expired share folders from the GitHub Pages source directory."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def parse_now(value: str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("--now must include a timezone offset")
    return parsed


def expiry_for(metadata_path: Path) -> tuple[date, ZoneInfo]:
    data = json.loads(metadata_path.read_text(encoding="utf-8"))
    expires_on = date.fromisoformat(data["expires_on"])
    zone = ZoneInfo(data["timezone"])
    return expires_on, zone


def remove_expired_shares(root: Path, now: datetime) -> tuple[int, int]:
    site = root / "site"
    shares = site / "shares"
    if site.is_symlink() or shares.is_symlink() or not shares.is_dir():
        return 0, 0

    removed = 0
    kept = 0
    for share_dir in sorted(shares.iterdir()):
        if share_dir.is_symlink() or not share_dir.is_dir():
            continue

        metadata_path = share_dir / "expiry.json"
        if metadata_path.is_symlink() or not metadata_path.is_file():
            kept += 1
            continue

        try:
            expires_on, zone = expiry_for(metadata_path)
        except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError, ZoneInfoNotFoundError) as error:
            print(f"Skipping invalid expiry metadata {metadata_path}: {error}", file=sys.stderr)
            kept += 1
            continue

        if now.astimezone(zone).date() > expires_on:
            shutil.rmtree(share_dir)
            print(f"Removed expired share: {share_dir.relative_to(root)}")
            removed += 1
        else:
            kept += 1

    return removed, kept


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument(
        "--now",
        help="timezone-aware ISO timestamp for testing; normally uses the current time",
    )
    args = parser.parse_args()

    try:
        now = parse_now(args.now)
    except ValueError as error:
        parser.error(str(error))

    removed, kept = remove_expired_shares(args.root, now)
    print(f"Expired shares removed: {removed}; active shares kept: {kept}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
