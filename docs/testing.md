# Testing Guide

> **Status**: Phase 3.x (2026-06-11)

## Quick Start

```bash
# Unit tests (fast, no external deps)
cd ai-server && pytest -m "not e2e"

# Full suite including E2E tests
cd ai-server && pytest

# E2E tests only (approval flow, integration)
cd ai-server && pytest -m e2e

# With coverage
cd ai-server && pytest --cov=src --cov-report=term-missing
```

## Test Categories

| Marker | Description | CI | Local |
|--------|-------------|----|-------|
| (default) | Unit tests — fast, deterministic | ✅ | ✅ |
| `e2e` | End-to-end approval flow tests | ❌ (heavy) | ✅ |

## CI Configuration (GitHub Actions)

```yaml
# .github/workflows/test.yml (planned)
jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -e ".[dev]"
      - run: pytest -m "not e2e"

  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -e ".[dev]"
      - run: pytest -m e2e
```

## E2E Scenarios Covered

| # | Scenario | Level | Expected Result |
|---|----------|-------|-----------------|
| 1 | Read-only browser research | 0 | Auto-allow, execute |
| 2 | Safe browser action | 1 | Auto-allow + audit |
| 3 | Approval-required action | 2 | APPROVAL_NEEDED → approve → execute |
| 4 | Rejected action | 2 | APPROVAL_NEEDED → reject → DENIED |
| 5 | Restricted action | 3 | DENIED |
| 6 | Unknown capability | — | NOT_FOUND |
| 7 | AutonomousLoop pause | 2 | Loop stops on APPROVAL_NEEDED |

## Docker E2E Testing

```bash
# Start all services
docker compose up -d

# Run E2E tests against running services
cd ai-server && pytest -m e2e --aegis-host=localhost:50051

# Stop services
docker compose down
```

## Local Development

```bash
# Watch mode
cd ai-server && ptw -- -m "not e2e"

# Single test file
cd ai-server && pytest tests/test_approval_integration.py -v

# Single test
cd ai-server && pytest tests/test_approval_integration.py::TestReadOnlyAutoAllow -v
```
