from pathlib import Path

from .corpus import digest_file, is_vcs_metadata


def inventory_crashes(directory: Path):
    records = []
    for path in sorted(p for p in directory.rglob("*")
                       if p.is_file() and not is_vcs_metadata(p, directory)):
        records.append({"path": str(path), "sha256": digest_file(path), "size": path.stat().st_size})
    return records

def group_by_hash(records):
    groups = {}
    for record in records:
        groups.setdefault(record["sha256"], []).append(record)
    return list(groups.values())
