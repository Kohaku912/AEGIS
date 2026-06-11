# AEGIS — Ellie: Autonomous Multi-Device AI

Ellie is an event-driven, self-improving AI assistant that coordinates across multiple devices and servers.

## Architecture

Ellie consists of 6 gRPC-connected servers:
- **AI Server** (Python) — Central brain, event orchestration, LLM integration
- **PC Server** — PC control and monitoring
- **Android Server** (Kotlin) — Mobile device integration
- **Room Server** — Physical environment control
- **Browser Server** (Node.js) — Web automation and scraping
- **Dev Server** — Sandboxed development and self-improvement

## Getting Started

> ⚠️ Project is in early initialization phase. No runnable code yet.

See [AGENTS.md](./AGENTS.md) for development guidelines and [docs/](./docs/) for architecture details.

## Status

- **Phase**: Initialization
- **Last Updated**: 2026-06-11
