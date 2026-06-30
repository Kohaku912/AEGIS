# ADR-0002: Browser Server — Python + browser-use

**Status**: Accepted  
**Date**: 2026-06-11  
**Supersedes**: Previous Node.js + Playwright approach (reverted)  

## Context

The Browser Server provides web automation capabilities for AEGIS. Two primary technology stacks were evaluated:

### Previous approach: Node.js + Playwright
- Language: TypeScript/Node.js
- Browser engine: Playwright (direct CDP/WebSocket control)
- AI integration: Manual — AEGIS Core would decompose tasks into Playwright API calls

### New approach: Python + browser-use
- Language: Python (same as AEGIS Core, shared tooling)
- Browser engine: browser-use (AI-agent-first abstraction over Playwright)
- AI integration: browser-use Agent handles natural language tasks within safety boundaries

## Decision

**Python + browser-use** is the chosen stack for the Browser Server.

### Reasons
1. **AI-native abstraction**: browser-use provides agent-level browser control (open page, extract text, click, fill form via natural language) rather than requiring AEGIS Core to manually decompose every web interaction into Playwright API calls.
2. **Language consistency**: Python is already used for AEGIS Core, shared schemas, and likely PC/Room servers. Reduces polyglot complexity.
3. **Local-first**: browser-use[core] runs entirely locally using Playwright under the hood. No cloud dependency.
4. **Safety isolation**: browser-use can be configured to run in read-only mode, with actions gated through AEGIS PolicyEngine.

### What browser-use wraps internally
browser-use uses Playwright internally for browser control. This is acceptable — AEGIS does NOT directly call Playwright APIs. All Playwright interaction is mediated by browser-use.

## Consequences

### Positive
- Single language ecosystem (Python) for AI Server + Browser Server
- browser-use Agent can handle research tasks with less manual decomposition
- Read-only mode aligns with AEGIS safety levels
- Local execution — no cloud API keys required

### Negative
- browser-use is newer/less mature than raw Playwright
- Adds an abstraction layer that may limit fine-grained control
- Playwright is still installed as a transitive dependency

### Migration
- Previous Node.js scaffold (package.json, tsconfig, TypeScript source) was removed
- Dockerfile updated from Node.js → Python
- Architecture docs updated

### Cloud version
- **NOT using** browser-use cloud at this time
- If cloud version is needed in the future, will require explicit user approval per Technology Decision Gate
- Cloud version would require `BROWSER_USE_API_KEY` — currently NOT required

## Safety constraints

1. **No CAPTCHA solving**: Do not enable browser-use's CAPTCHA handling features
2. **No ToS bypass**: Do not use for automating actions that violate website terms
3. **No stealth**: Do not enable stealth/proxy/residential proxy features
4. **No credential storage**: Do not persist cookies or authentication tokens
5. **No sensitive logging**: Redact Authorization, Set-Cookie, and credential headers
6. **PolicyEngine gate**: All browser actions go through AEGIS PolicyEngine
7. **Read-only by default**: Agent tasks default to read-only; write operations require Level 2 approval

## References
- [browser-use GitHub](https://github.com/browser-use/browser-use)
- [AGENTS.md Technology Decision Gate](../../AGENTS.md)
- [Browser Safety](../browser-safety.md)
