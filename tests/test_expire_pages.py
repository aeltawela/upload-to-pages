import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "skills" / "upload-to-pages" / "scripts" / "expire_pages.py"


def add_share(site: Path, name: str, expires_on: str, timezone: str = "Europe/Berlin") -> Path:
    folder = site / "site" / "shares" / name
    folder.mkdir(parents=True)
    (folder / "expiry.json").write_text(
        json.dumps({"expires_on": expires_on, "timezone": timezone}),
        encoding="utf-8",
    )
    (folder / "index.html").write_text("share", encoding="utf-8")
    return folder


def cleanup(site: Path, now: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(site), "--now", now],
        check=False,
        capture_output=True,
        text=True,
    )


class ExpirePagesTests(unittest.TestCase):
    def test_does_not_follow_a_symlinked_shares_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            site = temporary_root / "repo"
            outside = temporary_root / "outside"
            outside.mkdir()
            share = outside / "share"
            share.mkdir()
            (share / "expiry.json").write_text(
                json.dumps({"expires_on": "2026-10-31", "timezone": "UTC"}),
                encoding="utf-8",
            )
            shares = site / "site" / "shares"
            shares.parent.mkdir(parents=True)
            shares.symlink_to(outside, target_is_directory=True)

            result = cleanup(site, "2026-11-01T12:00:00+00:00")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((share / "expiry.json").exists())

    def test_expiry_runs_after_the_selected_local_date_ends(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            folder = add_share(site, "share-a", "2026-10-31")

            before_local_midnight = cleanup(site, "2026-10-31T22:30:00+00:00")
            self.assertEqual(before_local_midnight.returncode, 0, before_local_midnight.stderr)
            self.assertTrue(folder.exists())

            after_local_midnight = cleanup(site, "2026-10-31T23:30:00+00:00")
            self.assertEqual(after_local_midnight.returncode, 0, after_local_midnight.stderr)
            self.assertFalse(folder.exists())

    def test_keeps_future_shares_and_ignores_invalid_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            future = add_share(site, "future", "2026-11-02")
            invalid = add_share(site, "invalid", "not-a-date")
            unrelated = site / "about.html"
            unrelated.write_text("keep", encoding="utf-8")

            result = cleanup(site, "2026-11-01T12:00:00+00:00")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(future.exists())
            self.assertTrue(invalid.exists())
            self.assertTrue(unrelated.exists())

    def test_does_not_follow_a_share_directory_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            site = temporary_root / "repo"
            outside = temporary_root / "outside"
            outside.mkdir()
            (outside / "keep.txt").write_text("keep", encoding="utf-8")
            shares = site / "site" / "shares"
            shares.mkdir(parents=True)
            (shares / "linked").symlink_to(outside, target_is_directory=True)

            result = cleanup(site, "2026-11-01T12:00:00+00:00")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((outside / "keep.txt").exists())


if __name__ == "__main__":
    unittest.main()
