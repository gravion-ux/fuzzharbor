"""Corpus indexing for FuzzHarbor.

The indexer never follows symbolic links: a link inside a corpus can point
outside it, or back at a parent directory, which would make the scan read
unrelated files or never terminate.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

__all__ = [
    "CHUNK_SIZE",
    "VCS_DIRS",
    "corpus_report",
    "digest_file",
    "index_corpus",
    "is_vcs_metadata",
    "iter_corpus_files",
    "should_index",
]

VCS_DIRS = {".git", ".svn", ".hg"}
CHUNK_SIZE = 1024 * 1024


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_and_size(path: Path) -> tuple[str, int]:
    """Return the SHA-256 digest and the size of a file.

    The size is counted from the bytes that were hashed, so the reported size
    always belongs to the content that was digested.
    """
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def is_vcs_metadata(path: Path, root: Path) -> bool:
    """Version-control bookkeeping is not corpus content."""
    try:
        parts = path.relative_to(root).parts[:-1]
    except ValueError:
        parts = path.parts[:-1]
    return any(part in VCS_DIRS for part in parts)


def should_index(path: Path, root: Path) -> bool:
    """Decide whether a path is corpus content.

    Version-control bookkeeping is skipped, and symbolic links are never
    followed: a link can point outside the corpus or back at a parent
    directory.
    """
    if is_vcs_metadata(path, root):
        return False
    return not path.is_symlink()


def display_path(path: Path, root: Path) -> str:
    """Return a root-relative path, so a report does not leak the local layout."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def iter_corpus_files(directory: Path):
    """Yield the corpus files of a directory, in a stable order."""
    for dirpath, dirnames, filenames in os.walk(directory, followlinks=False):
        # A symlinked directory is listed by os.walk but never descended into.
        dirnames[:] = sorted(dirnames)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if should_index(path, directory):
                yield path


def index_corpus(directory: Path) -> list[dict]:
    """Index corpus files, grouped by content digest."""
    seen: dict[str, list[str]] = {}
    for path in iter_corpus_files(directory):
        try:
            sha = digest_file(path)
        except OSError:
            continue
        seen.setdefault(sha, []).append(display_path(path, directory))
    return [
        {"sha256": sha, "paths": paths, "duplicates": len(paths) - 1}
        for sha, paths in sorted(seen.items())
    ]


def corpus_report(directory: Path) -> dict:
    """Return the corpus index together with data-quality information."""
    seen: dict[str, list[str]] = {}
    skipped: list[dict] = []
    for path in iter_corpus_files(directory):
        try:
            sha = digest_file(path)
        except OSError as exc:
            skipped.append({"path": display_path(path, directory), "reason": str(exc.strerror or exc)})
            continue
        seen.setdefault(sha, []).append(display_path(path, directory))
    rows = [
        {"sha256": sha, "paths": paths, "duplicates": len(paths) - 1}
        for sha, paths in sorted(seen.items())
    ]
    return {
        "files": sum(len(paths) for paths in seen.values()),
        "unique": len(rows),
        "duplicates": sum(row["duplicates"] for row in rows),
        "corpus": rows,
        "skipped": skipped,
    }
