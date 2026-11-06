import os

import pytest

from fuzzharbor import corpus
from fuzzharbor.corpus import index_corpus, is_vcs_metadata


def test_deduplicates_identical_inputs(tmp_path):
    (tmp_path/"a").write_bytes(b"same"); (tmp_path/"b").write_bytes(b"same")
    rows = index_corpus(tmp_path)
    assert len(rows) == 1 and rows[0]["duplicates"] == 1


def test_vcs_metadata_is_not_indexed_as_corpus_content(tmp_path):
    (tmp_path/".git").mkdir()
    (tmp_path/".git"/"blob").write_bytes(b"same")
    (tmp_path/"seed.bin").write_bytes(b"same")
    rows = index_corpus(tmp_path)
    assert len(rows) == 1 and rows[0]["duplicates"] == 0


# --- paths are reported relative to the scanned root -------------------------


def test_paths_are_relative_to_the_scanned_root(tmp_path):
    (tmp_path/"seed.bin").write_bytes(b"same")
    rows = index_corpus(tmp_path)
    assert rows[0]["paths"] == ["seed.bin"]


def test_report_paths_are_relative_to_the_scanned_root(tmp_path):
    (tmp_path/"seed.bin").write_bytes(b"same")
    report = corpus.corpus_report(tmp_path)
    assert report["corpus"][0]["paths"] == ["seed.bin"]
    assert report["files"] == 1 and report["unique"] == 1 and report["duplicates"] == 0


# --- symbolic links are never followed ---------------------------------------


class _FakeSymlink:
    """Minimal path-like object that reports itself as a symbolic link."""

    def __init__(self, parts):
        self._parts = tuple(parts)

    @property
    def parts(self):
        return self._parts

    def relative_to(self, other):
        return self

    def is_symlink(self):
        return True


def test_should_index_rejects_a_symbolic_link():
    assert corpus.should_index(_FakeSymlink(("corpus", "link.txt")), "/corpus") is False


def test_should_index_accepts_an_ordinary_file(tmp_path):
    path = tmp_path / "seed.bin"
    path.write_bytes(b"same")
    assert corpus.should_index(path, tmp_path) is True


def test_should_index_rejects_version_control_metadata(tmp_path):
    path = tmp_path / ".git" / "blob"
    path.parent.mkdir()
    path.write_bytes(b"same")
    assert corpus.should_index(path, tmp_path) is False


def test_is_vcs_metadata_only_looks_at_directory_components(tmp_path):
    path = tmp_path / "notgit"
    path.write_bytes(b"same")
    assert is_vcs_metadata(path, tmp_path) is False


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="platform has no symlink support")
def test_symlinked_file_outside_the_corpus_is_not_indexed(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.bin").write_bytes(b"secret")
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    try:
        (corpus_dir / "link.bin").symlink_to(outside / "secret.bin")
    except OSError:
        pytest.skip("symbolic links require an extra privilege on this platform")
    rows = index_corpus(corpus_dir)
    assert rows == []


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="platform has no symlink support")
def test_symlinked_directory_is_not_followed(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.bin").write_bytes(b"secret")
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    try:
        (corpus_dir / "linked").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symbolic links require an extra privilege on this platform")
    rows = index_corpus(corpus_dir)
    assert rows == []


# --- data quality -----------------------------------------------------------


def test_unreadable_file_is_skipped_instead_of_aborting(tmp_path, monkeypatch):
    (tmp_path / "a.bin").write_bytes(b"same")
    (tmp_path / "b.bin").write_bytes(b"same")

    original = corpus.digest_file

    def flaky(path):
        if path.name == "b.bin":
            raise PermissionError(13, "Permission denied")
        return original(path)

    monkeypatch.setattr(corpus, "digest_file", flaky)
    report = corpus.corpus_report(tmp_path)
    assert report["files"] == 1
    assert report["skipped"] and report["skipped"][0]["path"] == "b.bin"
