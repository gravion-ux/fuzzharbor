import json

import pytest

from fuzzharbor import cli


def test_corpus_command_prints_a_report(tmp_path, capsys):
    (tmp_path / "a.bin").write_bytes(b"same")
    (tmp_path / "b.bin").write_bytes(b"same")
    code = cli.main(["corpus", str(tmp_path)])
    report = json.loads(capsys.readouterr().out)
    assert code == cli.EXIT_OK
    assert report["tool"] == "FuzzHarbor"
    assert report["mode"] == "corpus-index"
    assert report["schema_version"] == 1
    assert report["files"] == 2
    assert report["duplicates"] == 1


def test_crashes_command_clusters_artifacts(tmp_path, capsys):
    (tmp_path / "a.bin").write_bytes(b"same")
    (tmp_path / "b.bin").write_bytes(b"same")
    code = cli.main(["crashes", str(tmp_path)])
    report = json.loads(capsys.readouterr().out)
    assert code == cli.EXIT_OK
    assert report["mode"] == "crash-triage"
    assert report["artifacts"] == 2
    assert report["clusters"][0]["count"] == 2


def test_missing_directory_is_a_usage_error(tmp_path):
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["corpus", str(tmp_path / "absent")])
    assert excinfo.value.code == 2


def test_report_can_be_written_to_a_file(tmp_path, capsys):
    (tmp_path / "a.bin").write_bytes(b"same")
    output = tmp_path / "report.json"
    code = cli.main(["corpus", str(tmp_path), "--output", str(output)])
    capsys.readouterr()
    assert code == cli.EXIT_OK
    assert json.loads(output.read_text(encoding="utf-8"))["files"] == 1


def test_unwritable_output_path_is_reported_without_a_traceback(tmp_path, capsys):
    (tmp_path / "a.bin").write_bytes(b"same")
    output = tmp_path / "missing-directory" / "report.json"
    code = cli.main(["corpus", str(tmp_path), "--output", str(output)])
    captured = capsys.readouterr()
    assert code == cli.EXIT_INVALID_INPUT
    assert "fuzzharbor:" in captured.err
    assert "Traceback" not in captured.err
