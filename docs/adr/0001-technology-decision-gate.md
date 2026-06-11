# ADR-0001: Technology Decision Gate

**Status**: Accepted  
**Date**: 2026-06-11  

## Context

AEGIS is a multi-server autonomous AI platform. Multiple technology choices exist for each server component:

- Browser automation: Playwright (Node.js) vs browser-use (Python)
- PC automation: OS-specific APIs vs cross-platform libraries
- Room control: MQTT vs Home Assistant integration vs custom
- LLM orchestration: LangGraph vs AutoGen vs CrewAI vs custom loop
- Memory/Vector DB: Chroma vs Qdrant vs SQLite vector
- Communication: gRPC (already decided) vs REST vs WebSocket

AI coding agents working on this project may default to their training data's common choices (e.g., Node.js + Playwright for browser automation). This can lead to:
1. Inconsistent technology choices across servers
2. Decisions that don't align with the user's preferences or constraints
3. Increased complexity from mixing too many different runtimes

## Decision

We introduce a **Technology Decision Gate**: AI coding agents MUST present a structured comparison and ask the user to decide when:

1. Multiple viable technology options exist for the same feature
2. The proposed choice differs from what's specified in `AGENTS.md` or `architecture.md`
3. A new external service, cloud API, or paid API is being introduced
4. Architecture shifts from local-only to cloud-dependent
5. Changes affect security, privacy, or data handling
6. Language, framework, database, or communication protocol changes are proposed

**Decision request format**: Present Option A, Option B (at minimum), a recommendation, impact assessment, and rollback difficulty.

**Already resolved**: The user has explicitly chosen:
- **browser-use** (Python) for Browser Server
- **gRPC** for all inter-server communication

## Consequences

### Positive
- Prevents inconsistent or unwanted technology choices
- Keeps the user in control of their project's stack
- Reduces rework from incorrect assumptions
- Documents technology decisions explicitly (via ADRs)

### Negative
- Slightly slower initial implementation (waiting for user input)
- May require the user to make decisions they hadn't anticipated

### Mitigation
- The decision format is designed to be quick to review
- Common decisions (like gRPC, Python for AI Server) are already resolved
- Implementation to existing proto contracts does NOT require asking
