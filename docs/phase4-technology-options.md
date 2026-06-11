# Phase 4 — Technology Options

> **Status**: Decision Required (2026-06-11)  
> **Related**: [`AGENTS.md`](../AGENTS.md) §Technology Decision Gate, [`architecture.md`](architecture.md)

This document presents technology options for Phase 4 components. **No implementation has started.** Each section requires user decision before proceeding.

---

## 1. PC Server

### Option A: Python + pyautogui / pynput / mss / pywin32

- **Overview**: Python-based PC automation using mature cross-platform libraries. Same language as AEGIS Core and Browser Server.
- **Pros**: Language consistency (Python across AI/Browser/PC). pyautogui is simple and well-documented for mouse/keyboard. mss for fast screenshots. pywin32 for Windows-specific deep integration.
- **Cons**: Python GUI automation libraries are slower than native Rust/Node alternatives. pyautogui lacks fine-grained control compared to OS APIs. Some operations require platform-specific code paths (Windows vs Mac vs Linux).
- **Impact**: `pc-server/` becomes a Python project. Shared tooling with `ai-server/` and `browser-server/`. New deps: pyautogui, pynput, mss, pywin32 (Windows only).

### Option B: Rust + OS-native APIs

- **Overview**: High-performance Rust binary with direct Win32/X11/AppKit API calls.
- **Pros**: Maximum performance and safety (memory safety). No runtime overhead. Direct OS API access without Python abstraction layers. Cross-compilation to single binary.
- **Cons**: Different language stack from the rest of AEGIS (Python/AI, Python/Browser, Kotlin/Android). Steeper learning curve. Smaller ecosystem for GUI automation (compared to Python/Node). Protobuf/gRPC support exists but less mature tooling.
- **Impact**: `pc-server/` becomes a Rust project. New build pipeline (Cargo). Team needs Rust expertise.

### Option C: Node.js + robotjs / nut.js

- **Overview**: Node.js-based PC automation.
- **Pros**: Event-driven model fits AEGIS architecture. nut.js provides cross-platform keyboard/mouse/screen APIs. Fast for I/O-heavy operations.
- **Cons**: Another language in the stack (Python AI + Kotlin Android + Node PC). robotjs requires native compilation (node-gyp). Less mature than Python alternatives for system-level automation.
- **Impact**: `pc-server/` becomes a Node.js project. New dependency management (npm). Previously deprecated for Browser Server.

### Recommended

**Option A (Python)** — Language consistency with AEGIS Core and Browser Server. Python's ecosystem (pyautogui, pynput, mss, pywin32) covers all required observe/action capabilities. Shared linting/testing tooling (ruff, pytest, mypy). Lower cognitive overhead for contributors.

> **DECISION REQUIRED**: Please choose Option A / B / C / Other (specify).
choose B
---

## 2. Android Server

### Option A: Kotlin Native + AccessibilityService + MediaProjection

- **Overview**: Pure Kotlin Android app using AccessibilityService for UI interaction and MediaProjection for screen capture.
- **Pros**: No external dependency on Appium server. AccessibilityService has deep OS integration (tap, swipe, UI tree). MediaProjection for high-quality screen capture. Runs on-device natively.
- **Cons**: AccessibilityService requires user to enable in Settings. MediaProjection shows system permission dialog on each capture. Limited to Android platform. Kotlin + gRPC setup more complex than Python alternatives.
- **Impact**: `android-server/` becomes a Kotlin Android project. Requires Android SDK + Gradle. New testing infrastructure (Android instrumentation tests). Already specified in architecture docs.

### Option B: Appium + UIAutomator2

- **Overview**: Appium server controlling Android device via UIAutomator2 driver.
- **Pros**: Cross-platform (also works with iOS). WebDriver-like API familiar to test engineers. No AccessibilityService permission needed for basic operations. Large community.
- **Cons**: Requires running Appium server (additional process). Slower than native AccessibilityService. Some advanced operations (overlay, notification access) require additional permissions anyway. Adds another server to manage.
- **Impact**: Appium server dependency. Different API paradigm from native Android. May need both Appium + AccessibilityService for full capability coverage.

### Option C: ADB-only

- **Overview**: Pure ADB commands via subprocess (screencap, input tap, input text, dumpsys).
- **Pros**: Simplest setup — ADB is always available for Android dev. No app installation needed on device (for basic ops).
- **Cons**: Very slow for frequent operations (screencap → pull → read). No UI tree access. No overlay support. Limited to debugging-enabled devices.
- **Impact**: Not suitable for production use — too slow and limited.

### Recommended

**Option A (Kotlin Native + AccessibilityService)** — Already specified in architecture docs and proto definitions. Native Android app with AccessibilityService provides the deepest integration. MediaProjection for screenshots. gRPC client connects to AEGIS Core.

> **DECISION REQUIRED**: Please choose Option A / B / C / Other (specify).
choose A
---

## 3. Room Server

### Option A: Custom gRPC Room Server + MQTT bridge

- **Overview**: Python-based gRPC server that bridges to IoT devices via MQTT. Custom firmware on ESP32/Arduino for sensors and actuators.
- **Pros**: Full control over device communication. MQTT is lightweight and well-suited for IoT. Same Python stack as other servers. Custom firmware allows any sensor/actuator combination.
- **Cons**: Requires writing firmware for ESP32/Arduino. MQTT broker needed (Mosquitto — lightweight). More development effort than Home Assistant integration.
- **Impact**: `room-server/` Python project. New `firmware/` directory for ESP32/Arduino code. Mosquitto MQTT broker as additional Docker service.

### Option B: Home Assistant Integration

- **Overview**: Use Home Assistant as the IoT hub, with AEGIS Room Server communicating via Home Assistant API.
- **Pros**: Leverages existing Home Assistant ecosystem (1000+ integrations). No firmware development needed. Web UI for manual control. Community support.
- **Cons**: Requires Home Assistant installation (another service). API is REST-based (not gRPC native). Less control over device timing and behavior. May introduce cloud dependency (Home Assistant Cloud).
- **Impact**: Home Assistant as external dependency. REST API calls from Room Server. Configuration complexity for users without Home Assistant.

### Option C: ESPHome Only

- **Overview**: ESPHome firmware on ESP32 devices, communicating directly with Room Server via native protocol.
- **Pros**: No MQTT broker needed (ESPHome native API). YAML-based device configuration. OTA updates built-in. Large device support.
- **Cons**: ESPHome API is not gRPC. Limited to ESP32/ESP8266 devices. Less flexible than custom firmware.
- **Impact**: ESPHome as firmware framework. Native API client in Room Server.

### Recommended

**Option A (Custom gRPC + MQTT)** — Maximum control and alignment with AEGIS contract-first architecture. MQTT is a standard IoT protocol. Custom firmware allows any hardware. Can add Home Assistant as an optional integration later.

> **DECISION REQUIRED**: Please choose Option A / B / C / Other (specify).
choose A
---

## 4. EventBus Persistence

### Option A: In-memory asyncio queue (current)

- **Overview**: Keep the current in-memory EventBus implementation. Events are queued in Python asyncio queues. No persistence across restarts.
- **Pros**: Zero dependencies. Fastest possible throughput. Simple to debug. Already implemented and tested.
- **Cons**: Events lost on server restart. No cross-process event sharing. No event replay capability. Memory usage grows with event volume.
- **Impact**: No changes needed. Accept that events are ephemeral.

### Option B: SQLite-backed queue

- **Overview**: Persist events to SQLite database for durability across restarts.
- **Pros**: Lightweight — SQLite is already in Python stdlib (or apsw). Events survive restarts. Can query historical events. Simple to set up.
- **Cons**: Write latency for each event. Database file grows over time (needs cleanup). Single-writer limitation of SQLite. Not suitable for distributed deployment.
- **Impact**: New dependency on SQLite library (or apsw). Event write path becomes synchronous (or async with aiosqlite). Event replay becomes possible.

### Option C: Redis Streams

- **Overview**: Use Redis Streams for event queuing and persistence.
- **Pros**: High throughput. Consumer groups for distributed processing. Event persistence with TTL. Widely used in production.
- **Cons**: Requires Redis server (additional Docker service). Adds operational complexity. Network dependency for event bus. Overkill for single-node deployment.
- **Impact**: New Docker service (Redis). Python redis client dependency. Event bus becomes network-dependent.

### Option D: NATS / MQTT

- **Overview**: Use NATS or MQTT as the event transport layer.
- **Pros**: NATS is designed for cloud-native messaging. MQTT fits IoT use cases (Room Server sensors). Both support pub/sub natively.
- **Cons**: Additional infrastructure. Complexity overhead. Not needed for single-node deployment.
- **Impact**: New messaging infrastructure. Different programming model (topics vs queues).

### Recommended

**Phase 4: Option A (in-memory)** — Maintains simplicity for MVP. Already implemented and tested.  
**Future: Option B (SQLite)** — Lightweight persistence without new infrastructure. Good fit for single-node deployment.

> **DECISION REQUIRED**: Please choose Option A / B / C / D / Other (specify).
choose A
---

## 5. Memory / RAG (Retrieval-Augmented Generation)

### Option A: SQLite only (current)

- **Overview**: Keep current JSONL-based memory with in-memory search. No vector embeddings.
- **Pros**: Zero new dependencies. Already implemented. Simple substring/keyword search works for small datasets.
- **Cons**: No semantic search. Doesn't scale beyond ~10K facts. No vector similarity. Cannot find "similar" concepts — only exact keyword matches.
- **Impact**: No changes. Accept limitation of keyword-only search.

### Option B: SQLite + sqlite-vec (embeddings)

- **Overview**: Add vector embeddings using sqlite-vec extension. Store embeddings alongside facts in SQLite.
- **Pros**: All-in-one SQLite — no separate vector DB service. Embeddings enable semantic search. Local-only, no cloud dependency.
- **Cons**: sqlite-vec is relatively new. Embedding model needed (sentence-transformers or OpenAI API). Embedding computation cost.
- **Impact**: New Python deps: sqlite-vec, sentence-transformers (or openai). Embedding generation pipeline. Existing JSONL memories migrated to SQLite.

### Option C: Chroma

- **Overview**: Dedicated vector database (Chroma) for semantic memory.
- **Pros**: Purpose-built for RAG. Simple Python API. Built-in embedding functions. Active development.
- **Cons**: Another service to run (or embedded mode). Less mature than alternatives. May require separate persistence.
- **Impact**: New Python dependency (chromadb). Embedded mode runs in-process (no separate service). Migration from JSONL to Chroma.

### Option D: Qdrant / LanceDB / pgvector

- **Overview**: Production-grade vector databases.
- **Pros**: Qdrant: high performance, filtering, quantization. LanceDB: embedded columnar format. pgvector: if Postgres is already used.
- **Cons**: Qdrant needs separate service. LanceDB requires Rust toolchain. pgvector requires Postgres. All add operational complexity.
- **Impact**: New infrastructure dependencies. Overkill for MVP.

### Recommended

**Phase 4: Option A (SQLite only)** — Keep it simple for MVP.  
**Phase 5+: Option B (sqlite-vec)** — Lightweight vector search without new services.  
**Future consideration**: Chroma if scale demands exceed SQLite capabilities.

> **DECISION REQUIRED**: Please choose Option A / B / C / D / Other (specify).
choose C
---

## 6. Support Agent

### Option A: Custom Rule Engine + Scheduler

- **Overview**: Pure Python implementation using TriggerEngine rules + Scheduler for proactive user assistance. No LLM framework dependency.
- **Pros**: Already partially implemented (TriggerEngine + Scheduler). No new dependencies. Deterministic behavior. Full control over decision logic.
- **Cons**: More code to write. Rule-based logic may miss nuanced situations that LLM-based agent would catch. Requires manual rule creation.
- **Impact**: Extends existing TriggerEngine and Scheduler. New SupportAgent class with rule definitions.

### Option B: LangGraph State Machine

- **Overview**: Use LangGraph for stateful agent workflows (check calendar → check weather → suggest action).
- **Pros**: Purpose-built for agent state management. Graph-based workflow visualization. Checkpointing and human-in-the-loop built-in. Growing ecosystem.
- **Cons**: New heavy dependency (langgraph, langchain). LLM-dependent — requires API calls for each step. Cloud LLM cost. Less deterministic than rules.
- **Impact**: New Python deps: langgraph, langchain. LLM API integration. Different programming model from existing TriggerEngine.

### Option C: AutoGen / CrewAI

- **Overview**: Multi-agent frameworks for collaborative AI.
- **Pros**: AutoGen (Microsoft): mature multi-agent conversations. CrewAI: role-based agent collaboration.
- **Cons**: Heavy dependencies. LLM-dependent for all decisions. May introduce uncontrolled agent autonomy. Not aligned with AEGIS structural safety model.
- **Impact**: Significant new dependencies. Potential conflict with PolicyEngine (LLM making safety decisions).

### Recommended

**Option A (Custom Rule Engine + Scheduler)** — Aligns with AEGIS architectural principles: deterministic safety, no LLM for critical decisions, existing code reuse. TriggerEngine rules are configurable and improvable (via SelfDevAgent). Can add LLM-based suggestions later as a non-critical enhancement.

> **DECISION REQUIRED**: Please choose Option A / B / C / Other (specify).
choose B
---

## Decision Summary

| # | Topic | Recommended | User Choice |
|---|-------|-------------|-------------|
| 1 | PC Server language | Python | __________ |
| 2 | Android Server approach | Kotlin Native + AccessibilityService | __________ |
| 3 | Room Server architecture | Custom gRPC + MQTT | __________ |
| 4 | EventBus persistence | In-memory (Phase 4) | __________ |
| 5 | Memory / RAG | SQLite only (Phase 4) | __________ |
| 6 | Support Agent | Custom Rule Engine + Scheduler | __________ |

**Next Step**: User reviews and provides decisions. No Phase 4 implementation starts until all decisions are resolved.
