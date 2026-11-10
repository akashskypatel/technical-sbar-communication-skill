#!/usr/bin/env python3
"""Regenerate manifest.json hashes and sizes for this skill package.

The manifest deliberately excludes itself: hashing its own contents would be circular.
Existing metadata is preserved; only the ``files`` inventory is regenerated.
Requires Python 3.9+ and no third-party packages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "manifest.json"
IGNORED_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
IGNORED_FILES = {".DS_Store", "Thumbs.db"}


def package_files() -> list[Path]:
    """Find regular package files in deterministic relative-path order."""
    result = []
    for current_dir, subdirs, filenames in os.walk(ROOT, followlinks=False):
        base = Path(current_dir)
        for name in list(subdirs):
            path = base / name
            if name in IGNORED_DIRS:
                subdirs.remove(name)
            elif path.is_symlink():
                raise ValueError(f"Symlinked directory is not supported: {path}")
        subdirs.sort()
        for name in filenames:
            path = base / name
            if path == MANIFEST or name in IGNORED_FILES:
                continue
            if path.is_symlink():
                raise ValueError(f"Symlinked file is not supported: {path}")
            if not path.is_file():
                raise ValueError(f"Not a regular file: {path}")
            result.append(path)
    return sorted(result, key=lambda path: path.relative_to(ROOT).as_posix())


def record(path: Path) -> dict[str, object]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest.hexdigest(),
        "size_bytes": size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the manifest differs; do not write anything (useful in CI).",
    )
    args = parser.parse_args()
    try:
        if not MANIFEST.is_file():
            raise ValueError(f"Missing {MANIFEST}; existing package metadata is required")
        with MANIFEST.open("r", encoding="utf-8") as stream:
            manifest = json.load(stream)
        if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
            raise ValueError("manifest.json must contain a JSON object with a 'files' array")

        updated = dict(manifest)
        updated["files"] = [record(path) for path in package_files()]
        if updated == manifest:
            print(f"Manifest is current ({len(updated['files'])} files).")
            return 0
        if args.check:
            print("Manifest is out of date; run .tools/regenerate_manifest.py", file=sys.stderr)
            return 1

        serialized = json.dumps(updated, indent=2, ensure_ascii=False) + "\n"
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="\n",
                dir=ROOT, prefix=".manifest-", suffix=".tmp", delete=False,
            ) as stream:
                temporary = Path(stream.name)
                stream.write(serialized)
            os.replace(temporary, MANIFEST)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

        print(f"Updated {MANIFEST} ({len(updated['files'])} files).")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
