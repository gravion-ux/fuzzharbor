from pathlib import Path

from fuzzharbor.crashes import inventory_crashes


def test_vcs_metadata_is_not_inventoried_as_a_crash_artifact(tmp_path):
    (tmp_path/".git").mkdir()
    (tmp_path/".git"/"blob").write_bytes(b"same")
    (tmp_path/"crash-001.bin").write_bytes(b"same")
    records = inventory_crashes(tmp_path)
    assert [Path(r["path"]).name for r in records] == ["crash-001.bin"]
