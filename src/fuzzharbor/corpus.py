import hashlib
from pathlib import Path

VCS_DIRS = {".git", ".svn", ".hg"}


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_vcs_metadata(path: Path, root: Path) -> bool:
    """Version-control bookkeeping is not corpus content."""
    try:
        parts = path.relative_to(root).parts[:-1]
    except ValueError:
        parts = path.parts[:-1]
    return any(part in VCS_DIRS for part in parts)


def index_corpus(directory: Path):
    seen = {}
    for path in sorted(p for p in directory.rglob("*")
                       if p.is_file() and not is_vcs_metadata(p, directory)):
        sha = digest_file(path)
        seen.setdefault(sha, []).append(str(path))
    return [{"sha256": sha, "paths": paths, "duplicates": len(paths)-1}
            for sha, paths in seen.items()]
