"""Crash artifact inventory and clustering for FuzzHarbor."""
from __future__ import annotations

from pathlib import Path

from .corpus import digest_and_size, display_path, iter_corpus_files

__all__ = ["cluster_crashes", "crash_report", "group_by_hash", "inventory_crashes"]


def inventory_crashes(directory: Path) -> list[dict]:
    """List the crash artifacts of a directory with their digest and size."""
    records: list[dict] = []
    for path in iter_corpus_files(directory):
        try:
            digest, size = digest_and_size(path)
        except OSError:
            continue
        records.append({"path": display_path(path, directory), "sha256": digest, "size": size})
    return records


def group_by_hash(records) -> list[list[dict]]:
    """Group crash records that share a digest."""
    groups: dict[str, list[dict]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        digest = record.get("sha256")
        if not isinstance(digest, str):
            continue
        groups.setdefault(digest, []).append(record)
    return list(groups.values())


def cluster_crashes(records) -> list[dict]:
    """Cluster crash records by digest, with the duplicate count per cluster."""
    clusters = []
    for group in group_by_hash(records):
        first = group[0]
        clusters.append(
            {
                "sha256": first.get("sha256"),
                "count": len(group),
                "paths": [record.get("path") for record in group],
                "records": group,
            }
        )
    return sorted(clusters, key=lambda cluster: (-cluster["count"], str(cluster.get("sha256"))))


def crash_report(directory: Path) -> dict:
    """Return the crash inventory, its clusters and the files that were skipped."""
    records: list[dict] = []
    skipped: list[dict] = []
    for path in iter_corpus_files(directory):
        try:
            digest, size = digest_and_size(path)
        except OSError as exc:
            skipped.append({"path": display_path(path, directory), "reason": str(exc.strerror or exc)})
            continue
        records.append({"path": display_path(path, directory), "sha256": digest, "size": size})
    clusters = cluster_crashes(records)
    return {
        "artifacts": len(records),
        "clusters": clusters,
        "records": records,
        "skipped": skipped,
    }
