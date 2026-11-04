from fuzzharbor.corpus import index_corpus


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
