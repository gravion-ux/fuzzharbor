# FuzzHarbor

> A reproducible local fuzzing campaign manager and crash triage toolkit.

**Status:** MVP scaffold / research prototype. Not production-certified.

## Features
- Local target registry.
- Corpus hashing and deduplication.
- Crash artifact metadata and clustering.
- Adapter contract for AFL++/libFuzzer integrations.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
pytest
```

## Safety and scope
This MVP does not launch fuzzers or contact remote targets. Integrations must be restricted to binaries and services explicitly owned or authorized by the operator.

## Roadmap
- [ ] Stable public API and versioned schemas
- [ ] More unit, integration and adversarial tests
- [ ] Reproducible benchmarks and sample datasets
- [ ] Signed releases and dependency review
- [ ] Documentation and contribution guide

## License
MIT. See [LICENSE](LICENSE).
