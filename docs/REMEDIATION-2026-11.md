# Remediation notes — 2026-11

This document records the audit and remediation applied to FuzzHarbor in November 2026.
It is additive: the original README, SECURITY.md, and CONTRIBUTING.md remain in the
repository and were updated only where they were inaccurate or inconsistent.

## Method

Every source file was read line by line and each suspected defect was confirmed with
an executable regression test. The new tests were first run against the previously
published revision to confirm the defect was real (red phase: 14 failing tests), and
only then were the fixes applied (green phase: 19 passing and 2 skipped tests, up
from 3).

The two skipped tests are the symbolic-link integration tests. They need the symlink
privilege that this Windows host does not grant, and they run in GitHub Actions on
ubuntu.

## Defects fixed

| Severity | Defect | Fix |
| --- | --- | --- |
| High | The corpus scanner used `rglob` and followed symlinked directories, so a scan could read files outside the corpus or loop forever | `iter_corpus_files` walks with `os.walk(followlinks=False)`, and `should_index` rejects every symbolic link |
| Medium | One unreadable file aborted the whole run | Unreadable files are skipped and reported in the `skipped` list of `corpus_report` and `crash_report` |
| Medium | `group_by_hash` was unreachable from the command line, so crash clustering could not be used | The `crashes` subcommand, `crash_report`, and `cluster_crashes` make clustering reachable |
| Medium | Reports leaked absolute local paths | Paths are reported relative to the scanned root, in POSIX form |
| Low | The file size was taken from a separate `stat` call after hashing, so the reported size could belong to different content | `digest_and_size` counts the size from the bytes that were actually hashed |
| Low | A report could not be written to a file | `--output`, with an explicit error when the report cannot be written |
| Low | The package exposed no public API, and the report carried no format marker | `fuzzharbor.__all__`, `fuzzharbor.__version__`, and `schema_version` in the report |

## Documentation and spelling corrections

- `LICENSE` shipped a truncated MIT text: the warranty and liability paragraphs were
  missing. The complete, canonical MIT text is now in place, and the original
  copyright holder line is preserved.
- Spelling was inconsistent across the same file set. The prose now uses one
  convention throughout: American English. Dated records were left untouched.
- The roadmap listed "Stable public API and versioned schemas" and "Documentation and
  contribution guide" as unfinished while the package exposes `__all__`,
  `__version__`, and a versioned report schema, and while `CONTRIBUTING.md`,
  `SECURITY.md`, and this file exist. The checklist now reflects reality.
- The README documented no command-line usage and no Python API, although the project
  ships a console script with two subcommands and a public API. Both are now
  documented. The earlier feature list also described a target registry and an
  adapter contract that the code does not implement; the list now matches the code.
- A dictionary spelling scan (`codespell`) now reports no misspelling in this
  repository.

## Continuous integration hardening

The workflow previously ran the test suite only. It now also runs a credential scan
on every push and pull request.

| Job | What it does |
| --- | --- |
| `secret-scan` | Runs `scripts/scan-secrets.py`, which fails the build when the repository contains a high-confidence credential pattern (cloud keys, tokens, private key blocks, JWTs) or a file that must never be committed (`.env`, `*.pem`, `*.key`, `*.p12`, `id_rsa`, credential files) |

The scanner is the one already used by the Gravion Toolkit split repositories, so
every toolkit project now shares one definition of what counts as a secret. A
"soft" match, such as a dummy `api_key` inside a test fixture, is reported for
review but does not fail the build.

## Verification

| Check | Before | After |
| --- | --- | --- |
| Secret scan in CI | absent | present |
| Tests | 14 failing in the red phase | 19 passing, 2 skipped |
| Symlinked directories | followed | never followed |
| Unreadable files | aborted the run | skipped and reported in `skipped` |
| Crash clustering | unreachable from the CLI | `crashes` subcommand, `crash_report`, `cluster_crashes` |
| Reported paths | absolute | relative to the scanned root, in POSIX form |
| Reported file size | taken from a separate `stat` call | counted from the hashed bytes |
| Public API | none | `__all__` and `__version__` `0.2.0` |
| Report format marker | none | `schema_version: 1` |

## Residual limitations

- FuzzHarbor does not launch fuzzers. It does not build a corpus, run AFL++ or
  libFuzzer, or contact a remote target; it only inspects directories that already
  exist on the local disk.
- `index_corpus` and `inventory_crashes` still skip an unreadable file silently. Use
  `corpus_report` or `crash_report` when the `skipped` list matters.
- The crash inventory carries the digest, the size, and the path. It does not parse
  the artifact, so it cannot tell a real crash from any other file, and it performs
  no symbolization.
- Clustering groups by SHA-256 digest only. Two different faults that produce
  identical bytes land in one cluster, and a fault whose output varies between runs
  is split into many clusters.
- The scan covers regular files below the given directory. It does not follow a
  symbolic link, so content reachable only through one is never inventoried.
