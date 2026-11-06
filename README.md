# FuzzHarbor

> A reproducible local fuzzing campaign manager and crash triage toolkit.

**Status:** MVP scaffold / research prototype. Not production-certified.

## Features
- Index a corpus directory and group files by SHA-256 digest, with a duplicate count per digest.
- Never follow a symbolic link, so a scan cannot read outside the corpus or loop forever.
- Skip version-control bookkeeping directories (`.git`, `.svn`, `.hg`).
- Skip unreadable files and list them in a `skipped` section instead of aborting the run.
- Inventory crash artifacts with their digest and size, and cluster them by digest.
- Report every path relative to the scanned root, so a report does not leak the local directory layout.
- Count the reported file size from the bytes that were actually hashed.
- Emit a machine-readable JSON report with a `schema_version` field for CI pipelines.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
pytest
```

## Command-line usage

```bash
fuzzharbor corpus corpus-dir
fuzzharbor corpus corpus-dir --output corpus-report.json
fuzzharbor crashes crash-dir
fuzzharbor crashes crash-dir --output crash-report.json
```

| Command | Meaning |
| --- | --- |
| `corpus` | Index a corpus directory and report duplicate content |
| `crashes` | Inventory crash artifacts and cluster them by digest |

Both subcommands take the directory to scan as a required positional argument and
accept `--output PATH`, which writes the JSON report to a file in addition to
printing it.

| Exit code | Meaning |
| --- | --- |
| `0` | The directory was scanned and no error occurred |
| `1` | The report could not be written to `--output` |
| `2` | The command line was not valid, or the directory does not exist |

The report is JSON and carries `tool`, `mode`, and `schema_version`, so downstream
tooling can detect format changes.

## Python API

```python
from pathlib import Path

from fuzzharbor import (
    cluster_crashes,
    corpus_report,
    crash_report,
    group_by_hash,
    index_corpus,
    inventory_crashes,
)

index = index_corpus(Path("corpus"))           # digest groups with duplicate counts
corpus = corpus_report(Path("corpus"))          # index + file counts + skipped files

artifacts = inventory_crashes(Path("crashes"))  # path, sha256, and size per artifact
groups = group_by_hash(artifacts)               # records that share a digest
clusters = cluster_crashes(artifacts)           # clusters with a duplicate count
triage = crash_report(Path("crashes"))          # inventory + clusters + skipped files
```

`fuzzharbor.corpus.should_index(path, root)` is the scope decision helper: it skips
version-control metadata and rejects every symbolic link. The package exports a
stable public API (`fuzzharbor.__all__`) and reports its version as
`fuzzharbor.__version__` (`0.2.0`).

## Safety and scope
This MVP does not launch fuzzers or contact remote targets. It inspects local directories only, and it never follows a symbolic link. Integrations must be restricted to binaries and services explicitly owned or authorized by the operator.

## Roadmap
- [x] Stable public API and versioned schemas
- [x] More unit, integration and adversarial tests (19 passing, 2 skipped)
- [ ] Reproducible benchmarks and sample datasets
- [ ] Signed releases and dependency review
- [x] Documentation and contribution guide

## License
MIT. See [LICENSE](LICENSE). The LICENSE file now carries the complete MIT text, including the warranty and liability clauses.
