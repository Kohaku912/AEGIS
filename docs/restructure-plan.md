# Repository Restructure Plan

> **Status**: Proposal (2026-06-11)  
> **Related**: [`AGENTS.md`](../AGENTS.md), [`architecture.md`](architecture.md)  
> **⚠️ IMPORTANT**: This document is a **plan only**. No files have been moved yet.

---

## 1. Current Directory Structure

```
AEGIS/
├── .gitignore
├── AGENTS.md                 # AI agent guidance
├── README.md                 # Project overview
├── Mermaid.md                # Standalone architecture diagram (should be in docs/)
├── ai-server/                # Python — Core AI
│   ├── src/.gitkeep
│   └── tests/.gitkeep
├── pc-server/                # PC control
│   ├── src/.gitkeep
│   └── tests/.gitkeep
├── android-server/           # Android (Kotlin)
│   └── .gitkeep
├── browser-server/           # Node.js + Playwright
│   ├── src/.gitkeep
│   └── tests/.gitkeep
├── room-server/              # Room/IoT control
│   ├── src/.gitkeep
│   └── tests/.gitkeep
├── dev-server/               # Dev sandbox
│   ├── src/.gitkeep
│   └── tests/.gitkeep
├── protos/                   # gRPC proto definitions
│   └── AEGIS/
│       ├── common.proto
│       └── ai_server.proto
└── docs/
    ├── architecture.md
    └── adr/.gitkeep
```

**File count**: 19 files (including `.gitkeep` placeholders)  
**Directory count**: 20 directories (excluding `.git/`)

---

## 2. Problems Identified

### 2.1 Root Clutter — No Separation of Concerns

Six server directories co-exist at root with documentation, design artifacts, and protocol definitions. As more servers are added, the root becomes noisy. A monorepo of this scale needs clear layering:

| Layer | Current location | Problem |
|-------|-----------------|---------|
| **Application code** (servers) | Root | Mixed with docs, protocols, meta files |
| **Shared libraries** (protos) | `protos/` at root | No `packages/` layer; shared code has no home |
| **Documentation** | `docs/` at root | `Mermaid.md` is at root instead of in `docs/` |
| **Infrastructure** | (none yet) | No `infra/` directory for Docker, CI, deployment |
| **Firmware** | (none yet) | Room Server's IoT code has no natural home |

### 2.2 Naming Inconsistency

| Current name | Architecture doc calls it | Issue |
|-------------|--------------------------|-------|
| `dev-server/` | Dev Sandbox Server | Name doesn't convey sandbox constraint |
| `room-server/` | Room Control Server | Ok, but could be more descriptive |

The architecture document (§3.6) emphasizes that the dev server is **sandboxed** — the directory name should reflect this critical safety property.

### 2.3 Design Artifacts at Root

`Mermaid.md` is a design/reference artifact. It belongs in `docs/` alongside `architecture.md`. Having it at root:
- Clutters the root directory
- Confuses tooling that scans root for config files
- Is inconsistent with `docs/architecture.md`

### 2.4 No `packages/` Layer for Shared Code

The architecture specifies shared gRPC protocol definitions as the **single source of truth** (§2.3). Currently `protos/` sits at root. In the future, there will also be shared Python libraries (e.g., a common gRPC client helper) and shared TypeScript types generated from protos. A `packages/` directory provides a natural home for all shared code.

### 2.5 Future Infrastructure Has No Home

The MVP roadmap (§9) calls for `docker-compose.yml`, CI configurations, and deployment scripts. These need an `infra/` directory.

### 2.6 Future Firmware Has No Home

Room Server's IoT device firmware (Arduino sketches, ESP32 code) has no designated directory.

---

## 3. Ideal Target Structure

```
AEGIS/
├── .gitignore                   # [STAYS] Must be at root
├── AGENTS.md                    # [STAYS] Must be at root (AI agents find it here)
├── README.md                    # [STAYS] Must be at root (GitHub convention)
│
├── apps/                        # [NEW] Application servers
│   ├── ai-server/               # [MOVED from ai-server/]
│   │   ├── src/
│   │   └── tests/
│   ├── pc-server/               # [MOVED from pc-server/]
│   │   ├── src/
│   │   └── tests/
│   ├── android-server/          # [MOVED from android-server/]
│   ├── browser-server/          # [MOVED from browser-server/]
│   │   ├── src/
│   │   └── tests/
│   ├── room-server/             # [MOVED from room-server/]
│   │   ├── src/
│   │   └── tests/
│   └── dev-sandbox-server/      # [MOVED+RENAMED from dev-server/]
│       ├── src/
│       └── tests/
│
├── packages/                    # [NEW] Shared libraries & protocol
│   ├── protocol/                # [MOVED from protos/]
│   │   └── AEGIS/
│   │       ├── common.proto
│   │       ├── ai_server.proto
│   │       └── (future proto files)
│   └── common/                  # [NEW] Shared runtime code (placeholder)
│       └── README.md            # Explains what goes here
│
├── docs/                        # [KEPT] Documentation
│   ├── architecture.md          # [STAYS]
│   ├── restructure-plan.md      # [STAYS — this file]
│   ├── Mermaid.md               # [MOVED from root Mermaid.md]
│   └── adr/                     # [STAYS]
│
├── infra/                       # [NEW] Infrastructure & deployment
│   └── README.md                # Explains what goes here (docker-compose.yml, CI, etc.)
│
└── firmware/                    # [NEW] IoT device firmware
    └── README.md                # Explains what goes here (Arduino, ESP32, etc.)
```

### 3.1 Rationale for Each Layer

| Layer | Purpose | What goes here |
|-------|---------|---------------|
| `apps/` | Runnable application servers | Each server is a self-contained app with its own `Dockerfile`, dependencies, and tests |
| `packages/` | Shared libraries | Proto definitions (`protocol/`), shared gRPC client code (`common/`), generated code |
| `docs/` | Documentation & design | Architecture, ADRs, diagrams, restructuring plans |
| `infra/` | Infrastructure as code | `docker-compose.yml`, CI/CD configs, deployment scripts, monitoring configs |
| `firmware/` | IoT device code | Arduino sketches, ESP32 firmware, PCB designs (for Room Server) |

---

## 4. File Movement List

### 4.1 Moves (using `git mv` to preserve history)

| # | Source | Destination | Type |
|---|--------|-------------|------|
| 1 | `ai-server/` | `apps/ai-server/` | Directory move |
| 2 | `pc-server/` | `apps/pc-server/` | Directory move |
| 3 | `android-server/` | `apps/android-server/` | Directory move |
| 4 | `browser-server/` | `apps/browser-server/` | Directory move |
| 5 | `room-server/` | `apps/room-server/` | Directory move |
| 6 | `dev-server/` | `apps/dev-sandbox-server/` | Directory move + rename |
| 7 | `protos/` | `packages/protocol/` | Directory move |
| 8 | `Mermaid.md` | `docs/Mermaid.md` | File move |

### 4.2 New Files to Create

| # | File | Content |
|---|------|---------|
| 9 | `packages/common/README.md` | Explanation of shared runtime code |
| 10 | `infra/README.md` | Explanation of infrastructure directory |
| 11 | `firmware/README.md` | Explanation of firmware directory |

### 4.3 Files That Stay in Place

| File | Reason |
|------|--------|
| `.gitignore` | Git requirement — must be at root |
| `AGENTS.md` | AI agents discover it at root; GitHub Copilot docs recommend root placement |
| `README.md` | GitHub convention — displayed on repo homepage |
| `docs/architecture.md` | Already in correct location |
| `docs/adr/.gitkeep` | Already in correct location |

---

## 5. Files That Should NOT Be Moved

| File/Dir | Why NOT move |
|----------|-------------|
| `.gitignore` | Git only reads root `.gitignore`. Moving would break ignore rules. |
| `AGENTS.md` | VS Code Copilot and other AI tools specifically look for `AGENTS.md` at repository root. Moving to `docs/` would cause AI agents to miss it. |
| `README.md` | GitHub requires it at root for repo homepage rendering. |
| `.git/` | Never touch `.git` directory manually. |

---

## 6. Phased Migration Plan

> **Principle**: Each phase is independently committable and reversible. No phase depends on another being "in progress."

### Phase 0: Pre-flight Checks (5 seconds)

```bash
# Verify clean working tree
git status

# Confirm current commit for rollback reference
git log --oneline -1
# Expected: 3cb845d Add architecture document and update AGENTS.md

# List all files (baseline for later comparison)
git ls-tree -r HEAD --name-only
```

**Success criteria**: Clean working tree, no uncommitted changes.

---

### Phase 1: Create Target Directories (instant)

**Goal**: Create the new directory structure without moving any files.

```bash
# Create target directories
mkdir -p apps
mkdir -p packages/protocol/AEGIS
mkdir -p packages/common
mkdir -p infra
mkdir -p firmware
```

**Files affected**: None (only empty directories created)  
**Risk**: Zero — no files moved or deleted  
**Verification**:
```bash
ls -d apps/ packages/ infra/ firmware/
# Should all exist
```
**Rollback**: `rmdir apps packages infra firmware` (only works if empty — they will be)

---

### Phase 2: Move Server Directories into `apps/` (using `git mv`)

**Goal**: Move all 6 server directories under `apps/`, preserving Git history.

```bash
# Move servers (git mv preserves history)
git mv ai-server/ apps/ai-server/
git mv pc-server/ apps/pc-server/
git mv android-server/ apps/android-server/
git mv browser-server/ apps/browser-server/
git mv room-server/ apps/room-server/

# Rename dev-server → dev-sandbox-server (clarity per architecture §3.6)
git mv dev-server/ apps/dev-sandbox-server/
```

**Files affected**: 13 `.gitkeep` files (paths changed)  
**Risk**: Very low — only empty directories with `.gitkeep` files  
**Verification**:
```bash
# All old paths should NOT exist
ls -d ai-server/ pc-server/ android-server/ browser-server/ room-server/ dev-server/ 2>&1
# Expected: "No such file or directory" for each

# All new paths should exist
ls -d apps/*/
# Expected: apps/ai-server/ apps/pc-server/ apps/android-server/ apps/browser-server/ apps/room-server/ apps/dev-sandbox-server/

# Git log should follow history
git log --follow apps/ai-server/src/.gitkeep
```
**Rollback**: `git reset --hard HEAD~1` (or `git mv` back)

---

### Phase 3: Move Protocol Definitions into `packages/protocol/` (using `git mv`)

**Goal**: Move proto files into the shared packages layer.

```bash
# Move the protos directory (contains actual .proto files)
git mv protos/AEGIS/ packages/protocol/AEGIS/

# Remove the now-empty protos/ directory
rmdir protos/
```

**Files affected**: 2 `.proto` files (`common.proto`, `ai_server.proto`)  
**Risk**: Low — proto files are skeleton placeholders with no generated code yet  
**⚠️ Caution**: Future proto generation scripts will need path updates  
**Verification**:
```bash
ls packages/protocol/AEGIS/
# Expected: common.proto  ai_server.proto

# Old path should not exist
ls protos/ 2>&1
# Expected: "No such file or directory"
```
**Rollback**: `git reset --hard HEAD~1`

---

### Phase 4: Move Design Artifact to `docs/` (using `git mv`)

**Goal**: Consolidate all documentation under `docs/`.

```bash
git mv Mermaid.md docs/Mermaid.md
```

**Files affected**: 1 file (`Mermaid.md`)  
**Risk**: Zero  
**Verification**:
```bash
ls docs/Mermaid.md
# Expected: docs/Mermaid.md

ls Mermaid.md 2>&1
# Expected: "No such file or directory"
```
**Rollback**: `git mv docs/Mermaid.md Mermaid.md`

---

### Phase 5: Create Placeholder READMEs for New Directories

**Goal**: Add documentation so future contributors understand the directory purpose.

```bash
# Create packages/common/README.md
cat > packages/common/README.md << 'EOF'
# packages/common

Shared runtime libraries used across multiple servers.

## What goes here

- Generated gRPC client/server stubs (Python, Node.js, Kotlin)
- Shared type definitions
- Common utility functions (logging, config, error handling)
- Shared test fixtures and mocks

## What does NOT go here

- Server-specific business logic (belongs in `apps/<server>/`)
- Proto definitions (belongs in `packages/protocol/`)
- Infrastructure configs (belongs in `infra/`)
EOF

# Create infra/README.md
cat > infra/README.md << 'EOF'
# infra

Infrastructure as code and deployment configuration.

## What goes here

- `docker-compose.yml` — multi-server orchestration
- `docker-compose.*.yml` — environment-specific overrides (dev, test, prod)
- CI/CD pipeline configs (GitHub Actions, etc.)
- Monitoring and observability configs (Prometheus, Grafana, etc.)
- Nginx/Traefik reverse proxy configs
- Database migration scripts

## What does NOT go here

- Application code (belongs in `apps/`)
- Documentation (belongs in `docs/`)
EOF

# Create firmware/README.md
cat > firmware/README.md << 'EOF'
# firmware

IoT device firmware for Room Server peripherals.

## What goes here

- Arduino sketches (`.ino`)
- ESP32 / ESP8266 firmware
- Raspberry Pi Pico code
- PCB design files (KiCad, Eagle)
- 3D printing models (STL) for sensor housings
- Sensor driver code

## What does NOT go here

- Room Server application logic (belongs in `apps/room-server/`)
- Protocol definitions (belongs in `packages/protocol/`)
EOF
```

**Files affected**: 3 new `README.md` files  
**Risk**: Zero — only creating new documentation files  
**Verification**:
```bash
ls packages/common/README.md infra/README.md firmware/README.md
```
**Rollback**: `rm packages/common/README.md infra/README.md firmware/README.md`

---

### Phase 6: Update Internal References

**Goal**: Fix all path references in existing documentation to match the new structure.

#### 6.1 Files to Update

| File | Old Reference | New Reference | Count |
|------|--------------|---------------|-------|
| `AGENTS.md` | `ai-server/` | `apps/ai-server/` | ~15 occurrences |
| `AGENTS.md` | `pc-server/` | `apps/pc-server/` | ~4 occurrences |
| `AGENTS.md` | `protos/` | `packages/protocol/` | ~8 occurrences |
| `AGENTS.md` | `dev-server/` | `apps/dev-sandbox-server/` | ~2 occurrences |
| `AGENTS.md` | `Mermaid.md` | `docs/Mermaid.md` | 1 occurrence |
| `docs/architecture.md` | `ai-server/` | `apps/ai-server/` | ~12 occurrences |
| `docs/architecture.md` | `protos/AEGIS/` | `packages/protocol/AEGIS/` | ~8 occurrences |
| `docs/architecture.md` | `dev-server/` | `apps/dev-sandbox-server/` | ~5 occurrences |
| `README.md` | `ai-server/` → etc. | `apps/ai-server/` → etc. | ~2 occurrences |
| `.gitignore` | `android-server/` | `apps/android-server/` | ~4 occurrences |
| `protos/AEGIS/ai_server.proto` | Go import path | Update | 1 occurrence |
| `protos/AEGIS/common.proto` | Go import path | Update | 1 occurrence |

#### 6.2 Update Commands

```bash
# Update AGENTS.md — all server paths
# (These are search-and-replace operations — do NOT blindly sed;
#  review each change. Use an editor with find-and-replace.)

# AGENTS.md → replace directory structure diagram
# AGENTS.md → replace all `cd ai-server` with `cd apps/ai-server`
# AGENTS.md → replace all `cd browser-server` with `cd apps/browser-server`
# AGENTS.md → replace `protos/` with `packages/protocol/`
# AGENTS.md → replace `dev-server/` with `apps/dev-sandbox-server/`
# AGENTS.md → replace `Mermaid.md` with `docs/Mermaid.md`

# docs/architecture.md → same path updates
# docs/architecture.md → update proto paths in module map (§5.1)

# README.md → update server list

# .gitignore → update android-server path if needed

# Proto files → update go_package option
# common.proto: go_package = "github.com/Kohaku912/AEGIS/packages/protocol/AEGIS";
# ai_server.proto: go_package = "github.com/Kohaku912/AEGIS/packages/protocol/AEGIS";
```

> **⚠️ WARNING**: This is the highest-risk phase. Do NOT use bulk sed — review every change. Commit after each file is updated.

**Verification**:
```bash
# Search for old paths — should return zero results
grep -r "ai-server/" --include="*.md" --include="*.proto" . | grep -v "apps/ai-server" | grep -v ".git/"
grep -r "pc-server/" --include="*.md" --include="*.proto" . | grep -v "apps/pc-server" | grep -v ".git/"
grep -r "protos/" --include="*.md" --include="*.proto" . | grep -v "packages/protocol" | grep -v ".git/"
grep -r "dev-server/" --include="*.md" --include="*.proto" . | grep -v "apps/dev-sandbox-server" | grep -v ".git/"
```
**Rollback**: `git reset --hard HEAD~1`

---

### Phase 7: Final Verification

```bash
# 1. Clean working tree
git status
# Expected: "nothing to commit, working tree clean"

# 2. All old directories gone
for d in ai-server pc-server android-server browser-server room-server dev-server protos; do
  if [ -d "$d" ]; then echo "ERROR: $d still exists"; fi
done

# 3. All new directories present
for d in apps apps/ai-server apps/pc-server apps/android-server apps/browser-server apps/room-server apps/dev-sandbox-server packages packages/protocol packages/common infra firmware docs; do
  if [ ! -d "$d" ]; then echo "ERROR: $d missing"; fi
done

# 4. Root is clean (only meta files + top-level dirs)
ls -1
# Expected: AGENTS.md  README.md  .gitignore  apps/  docs/  firmware/  infra/  packages/

# 5. No broken references in docs
grep -r "ai-server/" --include="*.md" . | grep -v "apps/" | grep -v ".git/"
# Expected: no output

# 6. Proto files accessible at new path
ls packages/protocol/AEGIS/common.proto packages/protocol/AEGIS/ai_server.proto

# 7. Mermaid.md accessible at new path
ls docs/Mermaid.md

# 8. Git history preserved
git log --follow apps/ai-server/src/.gitkeep
# Expected: shows the original commit that created the file
```

---

### Phase 8: Commit Each Phase Separately

Each phase should be a separate commit for clean history and easy rollback:

```
Phase 0: git commit -m "restructure: pre-flight baseline"            (no changes)
Phase 1: git commit -m "restructure: create apps/, packages/, infra/, firmware/ dirs"
Phase 2: git commit -m "restructure: move servers into apps/"
Phase 3: git commit -m "restructure: move protos/ into packages/protocol/"
Phase 4: git commit -m "restructure: move Mermaid.md into docs/"
Phase 5: git commit -m "restructure: add placeholder READMEs for new dirs"
Phase 6: git commit -m "restructure: update all path references"
Phase 7: git commit -m "restructure: final verification — structure complete"
```

---

## 7. Paths That Will Break After Restructure

### 7.1 Internal Documentation References

| File | Old Path Referenced | Must Be Updated |
|------|--------------------|-----------------|
| `AGENTS.md` | `ai-server/src/event_queue.py` | `apps/ai-server/src/event_queue.py` |
| `AGENTS.md` | `ai-server/src/safety.py` | `apps/ai-server/src/safety.py` |
| `AGENTS.md` | `cd ai-server && ...` | `cd apps/ai-server && ...` |
| `AGENTS.md` | `cd browser-server && ...` | `cd apps/browser-server && ...` |
| `docs/architecture.md` §5.1 | Module map paths | All `ai-server/src/` → `apps/ai-server/src/` |
| `docs/architecture.md` §9 | `browser-server/` | `apps/browser-server/` |
| `docs/architecture.md` §11 | File paths in gap analysis | All need updating |
| `README.md` | Server list | Update directory references |

### 7.2 Proto Imports

| File | Current | After |
|------|---------|-------|
| `ai_server.proto` | `import "AEGIS/common.proto";` | No change needed (relative import within same package) |
| `common.proto` | `option go_package = "github.com/Kohaku912/AEGIS/protos/AEGIS";` | `option go_package = "github.com/Kohaku912/AEGIS/packages/protocol/AEGIS";` |

### 7.3 `.gitignore` Patterns

The `.gitignore` file has no paths with directory prefixes currently, so no changes are needed. However, when patterns like `android-server/app/build/` are added, they MUST use the new path `apps/android-server/app/build/`.

### 7.4 Future Files That Will Be Affected

These files don't exist yet, but when created, MUST use new paths:

| Future File | MUST Use Path |
|-------------|--------------|
| `docker-compose.yml` | `apps/ai-server/`, `apps/browser-server/`, etc. for build contexts |
| `ai-server/pyproject.toml` | Package name independent of directory (can stay `ai_server`) |
| `browser-server/package.json` | `"name": "@aegis/browser-server"` |
| CI config (GitHub Actions) | `working-directory: apps/ai-server` |
| Proto generation scripts | Output to `packages/common/generated/` |

---

## 8. Verification Commands Summary

Run these after ALL phases complete:

```bash
# === Structural Verification ===

# 1. Root contains only meta files + top-level directories
ls -1 | sort

# 2. All apps present
ls -d apps/*/

# 3. All packages present
ls -d packages/*/

# 4. No old directories remain
test ! -d ai-server && test ! -d pc-server && test ! -d protos && echo "CLEAN"

# === Content Verification ===

# 5. No stale path references in markdown
grep -rn "ai-server/" --include="*.md" . | grep -v "apps/" | grep -v ".git/"
grep -rn "pc-server/" --include="*.md" . | grep -v "apps/" | grep -v ".git/"
grep -rn "protos/" --include="*.md" --include="*.proto" . | grep -v "packages/" | grep -v ".git/"
grep -rn "dev-server/" --include="*.md" . | grep -v "apps/dev-sandbox" | grep -v ".git/"

# 6. Proto files valid
ls packages/protocol/AEGIS/*.proto

# 7. Git history intact
git log --follow apps/ai-server/src/.gitkeep

# === Git Verification ===

# 8. Clean working tree
git status

# 9. Commit log shows all phases
git log --oneline -10
```

---

## 9. Rollback Procedure

If any phase fails or causes unexpected issues:

### Full Rollback (return to pre-restructure state)

```bash
# Option A: If you committed each phase separately, revert to pre-restructure commit
git reset --hard 3cb845d   # The commit BEFORE any restructure changes

# Option B: If all changes are in one commit
git revert <restructure-commit-hash>

# Verify rollback
ls -d ai-server/ pc-server/ protos/   # Should all exist
ls apps/ 2>&1                          # Should error "No such file or directory"
```

### Partial Rollback (undo a specific phase)

```bash
# Revert only Phase 2 (server moves)
git revert <phase-2-commit-hash>

# Revert only Phase 3 (proto move)
git revert <phase-3-commit-hash>
```

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `git mv` loses history | Very Low | Low | `git mv` preserves history by default; verified with `git log --follow` |
| Stale path references in docs | Medium | Low | Phase 6 explicitly searches and fixes all references |
| Proto import breakage | Very Low | Medium | No generated code exists yet; imports are relative within package |
| Breaking future tooling | Low | Medium | Documented expected paths in §7.4 for future files |
| Root clutter after adding files later | Low | High | `AGENTS.md` and this document guide all future file placement |

**Overall risk**: **LOW** — The repository contains only skeleton files. No running code, no dependencies, no build pipeline, no CI. This is the ideal time to restructure.

---

## 11. Decision: When to Execute

| Option | Recommendation |
|--------|---------------|
| **Execute now** | ✅ **Recommended** — Repo is empty skeletons. Zero risk to running code. Best time to get the structure right. |
| **Execute after Phase 1 implementation** | ❌ Not recommended — By then, files exist with imports, dependencies, and build configs. Restructuring becomes harder. |
| **Never execute** | ❌ Not recommended — Current flat structure doesn't scale with 6+ servers. |

---

## Appendix A: Comparison — Current vs Target

### Root directory before

```
.gitignore
AGENTS.md
README.md
Mermaid.md
ai-server/
android-server/
browser-server/
dev-server/
docs/
pc-server/
protos/
room-server/
```

### Root directory after

```
.gitignore
AGENTS.md
README.md
apps/
docs/
firmware/
infra/
packages/
```

**Reduction**: Root entries drop from **13** to **8** (meta files: 3, top-level dirs: 5). Clear, scannable, scalable.

---

## Appendix B: Related Documents

| Document | Path |
|----------|------|
| AGENTS.md (rules for agents) | `AGENTS.md` → stays at root |
| Architecture overview | `docs/architecture.md` |
| Architecture diagram (Mermaid) | `docs/Mermaid.md` → currently at root, moves to docs |
| This restructure plan | `docs/restructure-plan.md` |
