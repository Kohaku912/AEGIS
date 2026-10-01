"""Every Dockerfile must be referenced by a compose file, or explicitly recorded here.

Measured 2026-10-01 (`docker-compose config --quiet` rc=0 for both compose files):

* `docker-compose.yml` builds `infra/docker/{ai-server,browser-server,room-server}.Dockerfile`.
* The repo *also* ships `ai-server/Dockerfile` (2026-08-14) and `browser-server/Dockerfile`
  (2026-07-26), which **no** compose file, script or CI step references — and which have
  **diverged** from the live ones: the ai-server one has no web-ui build stage, no HEALTHCHECK and
  runs `aegis_ai.main` instead of `aegis_ai.docker_entrypoint`; the browser-server one apt-installs
  `chromium` and sets `DISPLAY=:99` instead of `playwright install --with-deps`. A reader who builds
  them gets a **different image**, silently.
* `infra/docker/pc-server.Dockerfile` is unreferenced too, but its header declares it a deliberate
  placeholder ("NOT used by docker-compose.yml"). That is the whole distinction this pin encodes:
  an unreferenced Dockerfile is allowed only if it is **recorded here**.

`docker-compose.yml.archive` is not scanned: it is a deliberately frozen rollback artefact
(`docs/agents/rollback.md`), and it still names `infra/docker/dev-server.Dockerfile`, which was
deleted on purpose. Live compose files are `*.yml`/`*.yaml`; the archive's extension keeps it out
*structurally* rather than by an exclusion list.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[2]

_SKIP_DIRS = frozenset({".git", ".venv", "node_modules", "__pycache__", ".workbuddy-ai"})

_RECORDED_UNREFERENCED: frozenset[str] = frozenset(
    {
        # Deliberate placeholder — its own header says docker-compose.yml must not build it.
        "infra/docker/pc-server.Dockerfile",
        # Drift (measured 2026-10-01): pre-refactor variants, referenced by no build path, and
        # divergent from the live files. Kept pending an owner call — DELEGATION.md §4 item 17.
        "ai-server/Dockerfile",
        "browser-server/Dockerfile",
    }
)


@lru_cache(maxsize=1)
def _shipped_files() -> tuple[Path, ...]:
    """Every file under the repo except the skipped trees.

    `Path.rglob` cannot prune, so it would walk `.venv/` and `.git/`; and the three callers below
    would each pay for a fresh walk (measured: ~2.3 s over 25 k files, paid once here).
    """
    out: list[Path] = []
    for root, dirs, files in os.walk(_REPO):
        dirs[:] = sorted(d for d in dirs if d not in _SKIP_DIRS)
        out.extend(Path(root) / name for name in files)
    return tuple(out)


def _is_dockerfile(path: Path) -> bool:
    """`Dockerfile`, or `something.Dockerfile` — never a name that merely *contains* the word.

    Windows is case-insensitive, so a `*Dockerfile*` glob also matched this very file
    (`test_dockerfiles_are_owned.py`) the first time it ran.
    """
    return path.name == "Dockerfile" or path.name.endswith(".Dockerfile")


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(_REPO).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _compose_files() -> list[Path]:
    return sorted(
        path
        for path in _shipped_files()
        if path.suffix in {".yml", ".yaml"} and path.name.startswith("docker-compose")
    )


def _dockerfile_references() -> dict[Path, list[tuple[str, Path]]]:
    """compose file -> [(service, resolved dockerfile path)].

    `dockerfile:` is relative to the service's build **context**, not to the compose file.
    """
    refs: dict[Path, list[tuple[str, Path]]] = {}
    for compose in _compose_files():
        data = yaml.safe_load(compose.read_text(encoding="utf-8")) or {}
        for name, service in (data.get("services") or {}).items():
            build = (service or {}).get("build")
            if build is None:
                continue
            if isinstance(build, str):
                context, dockerfile = build, "Dockerfile"
            else:
                context = build.get("context", ".")
                dockerfile = build.get("dockerfile", "Dockerfile")
            refs.setdefault(compose, []).append(
                (name, (compose.parent / context / dockerfile).resolve())
            )
    return refs


def _discovered_dockerfiles() -> list[Path]:
    return sorted(path for path in _shipped_files() if _is_dockerfile(path))


def test_every_referenced_dockerfile_exists() -> None:
    refs = _dockerfile_references()
    total = sum(len(entries) for entries in refs.values())
    assert total >= 3, (
        f"found only {total} dockerfile references across {len(refs)} compose files — the scan is "
        "not reading the shipped tree, so the assertion below would pass vacuously"
    )
    missing = [
        f"{_rel(compose)}: service {name!r} -> {_rel(target)} does not exist"
        for compose, entries in refs.items()
        for name, target in entries
        if not target.is_file()
    ]
    assert not missing, (
        "a compose file points at a Dockerfile that is not in the tree — `docker compose build` "
        "fails with a path error, which is exactly how the deleted dev-server.Dockerfile behaved:\n  "
        + "\n  ".join(missing)
    )


def test_unreferenced_dockerfiles_match_the_recorded_set() -> None:
    discovered = _discovered_dockerfiles()
    assert len(discovered) >= 4, (
        f"found only {len(discovered)} Dockerfiles — the scan is not reading the shipped tree"
    )
    referenced = {
        _rel(target) for entries in _dockerfile_references().values() for _, target in entries
    }
    observed = {_rel(path) for path in discovered} - referenced
    assert observed == _RECORDED_UNREFERENCED, (
        "the set of unreferenced Dockerfiles changed.\n"
        "  newly unreferenced (a build path was removed, or a stray file was added): "
        f"{sorted(observed - _RECORDED_UNREFERENCED)}\n"
        "  no longer unreferenced (now built, or deleted): "
        f"{sorted(_RECORDED_UNREFERENCED - observed)}\n"
        "Either wire it into a compose file or record it above with the reason."
    )
