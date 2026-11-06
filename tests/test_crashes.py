from pathlib import Path

from fuzzharbor import crashes
from fuzzharbor.crashes import group_by_hash, inventory_crashes


def test_vcs_metadata_is_not_inventoried_as_a_crash_artifact(tmp_path):
    (tmp_path/".git").mkdir()
    (tmp_path/".git"/"blob").write_bytes(b"same")
    (tmp_path/"crash-001.bin").write_bytes(b"same")
    records = inventory_crashes(tmp_path)
    assert [Path(r["path"]).name for r in records] == ["crash-001.bin"]


def test_reported_size_matches_the_hashed_content(tmp_path):
    (tmp_path/"crash-001.bin").write_bytes(b"0123456789")
    records = inventory_crashes(tmp_path)
    assert records[0]["size"] == 10


def test_identical_artifacts_are_clustered(tmp_path):
    (tmp_path/"a.bin").write_bytes(b"same")
    (tmp_path/"b.bin").write_bytes(b"same")
    (tmp_path/"c.bin").write_bytes(b"different")
    clusters = crashes.cluster_crashes(inventory_crashes(tmp_path))
    assert clusters[0]["count"] == 2
    assert clusters[0]["paths"] == ["a.bin", "b.bin"]


def test_group_by_hash_ignores_malformed_records():
    assert group_by_hash([None, {"sha256": 5}, {"sha256": "x"}]) == [[{"sha256": "x"}]]


def test_crash_report_counts_artifacts_and_clusters(tmp_path):
    (tmp_path/"a.bin").write_bytes(b"same")
    (tmp_path/"b.bin").write_bytes(b"same")
    report = crashes.crash_report(tmp_path)
    assert report["artifacts"] == 2
    assert report["clusters"][0]["count"] == 2
    assert report["skipped"] == []
