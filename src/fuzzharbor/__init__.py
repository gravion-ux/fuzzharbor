"""FuzzHarbor: reproducible local fuzzing campaign manager and crash triage.

Public API
----------
``index_corpus``     corpus index grouped by content digest
``corpus_report``    corpus index with file counts and skipped files
``inventory_crashes`` crash artifacts with digest and size
``cluster_crashes``  crash artifacts grouped by digest
"""
from .corpus import corpus_report, digest_file, index_corpus, is_vcs_metadata, iter_corpus_files
from .crashes import cluster_crashes, crash_report, group_by_hash, inventory_crashes

__all__ = [
    "__version__",
    "cluster_crashes",
    "corpus_report",
    "crash_report",
    "digest_file",
    "group_by_hash",
    "index_corpus",
    "inventory_crashes",
    "is_vcs_metadata",
    "iter_corpus_files",
]

__version__ = "0.2.0"
