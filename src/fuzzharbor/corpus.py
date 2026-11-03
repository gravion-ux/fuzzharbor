import hashlib
from pathlib import Path


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def index_corpus(directory: Path):
    seen = {}
    for path in sorted(p for p in directory.rglob("*") if p.is_file()):
        sha = digest_file(path)
        seen.setdefault(sha, []).append(str(path))
    return [{"sha256": sha, "paths": paths, "duplicates": len(paths)-1}
            for sha, paths in seen.items()]
