# ClawShell 2.0 — DEEP Changelog

## v1.0.0 (2026-05-13) — Initial Release

### Architecture

**One Cloud Multi-Edge Distributed Neural Architecture**

Octopus-inspired design: 1 Cortex (Cloud Brain) + N Ganglions (Edge Brains).

- **Cortex**: Architecture planning, deep thinking, insight analysis, review & summary, result broadcasting, terminal management. Consensus knowledge deployed to Alibaba Cloud ECS/OSS + GitHub + MemOS Cloud.
- **Ganglion**: Installed on endpoints, auto-adapts to 8 OpenClaw-like architectures, self-discovers plugins/tools, connects to Cortex for task/skill/knowledge/memory sharing. Runs independently when offline.

### Core Principles

| Principle | Implementation |
|-----------|---------------|
| Cybernetics | PID feedback control loop, dynamic strategy switching, system holistic thinking |
| Heterogeneous Equivalence | 8 OpenClaw variant adapters, unified EventBus protocol |
| Non-invasive | Bridge script injection, never modifies target core code |
| Low Coupling | EventBus pub/sub + standardized Pydantic Schema communication |
| High Robustness | 3-layer repair escalation: self-healing > auto-repair > manual |
| High Generality | Perception abstraction layer, adapter pattern |
| High Collaboration | Ecological niche matching (capability 40% + load 30% + trust 30%) |
| Portability | pip install -e ., cross-platform |
| Idempotency | Repeated install/register has no side effects |
| Edge-Cloud Version Decoupling | Independent config, independent evolution |

### Modules (28 Source Files)

#### shared — Core Data Layer
- `types.py`: 17 enums (NodeType, Strategy, EventCategory, TrustLevel, RepairLayer, 8 OpenClawVariant, etc.) + 4 type aliases
- `models.py`: 20+ Pydantic v2 models (NodeInfo, Task, EventMessage, Insight, Plugin, PerceptionResult, Knowledge, Memory, HealthReport, RepairAction, CortexConfig, GanglionConfig, etc.)
- `config.py`: YAML + environment variable 3-level configuration loader with global singletons

#### neural_bus — Communication Layer
- `protocol.py`: MessageCodec JSON encoder/decoder + MessageFactory with 10 factory methods
- `event_bus.py`: Priority heap queue (CRITICAL > HIGH > NORMAL > LOW), wildcard subscriptions (task.*, *), JSONL persistence, TTL expiry
- `transport.py`: CortexTransport (WebSocket Server) + GanglionTransport (WebSocket Client with auto-reconnect, exponential backoff, offline buffer)

#### cortex — Cloud Brain
- `core.py`: CortexCore lifecycle manager + FeedbackControlLoop (PID controller) + StrategySwitcher (5 strategies with state machine transitions) + health loop
- `insight.py`: InsightEngine — real-time event stream analysis, error storm detection (>=5 errors triggers alert), pattern analysis, periodic summarization, knowledge extraction
- `terminal_manager.py`: TerminalManager — ganglion registration/heartbeat/trust scoring, ecological niche matching (capability 40% + load 30% + trust 30%), heartbeat timeout detection
- `broadcast.py`: BroadcastEngine — periodic insight broadcasting (5 min), knowledge synchronization (10 min), Agent.md optimization suggestion generation
- `adapters/aliyun.py`: Alibaba Cloud OSS adapter with HMAC-SHA1 signed upload/download
- `adapters/memos.py`: MemOS Cloud adapter — semantic memory storage/retrieval, context recall
- `adapters/github.py`: GitHub API adapter — file read/write, version comparison, optimization via Issues
- `main.py` + `cli.py`: Typer CLI with cortex, ganglion, init, version commands

#### ganglion — Edge Brain
- `perception.py`: PerceptionEngine — 4-dimension perception (system/network/cloud/internet), port scanning, 8 OpenClaw variant auto-detection
- `adaptation.py`: AdaptationEngine — self-discovery (pip packages, CLI tools, OpenClaw skills), health analysis (CPU/memory/disk), 3-layer repair, strategy degradation
- `plugin_manager.py`: PluginManager — 5 builtin plugins (n8n, MemOS, ComfyUI, Ollama, OpenClaw Skills), YAML-based custom plugin discovery, health checking
- `adapters/openclaw.py`: OpenClawAdapter — 8 architecture variant profiles, agent file reading, skill/tool discovery, non-invasive bridge script installation
- `main.py`: Full startup flow — perception > adaptation > plugin discovery > cortex connection (offline fallback)

#### storage — Persistence Layer
- `knowledge_store.py`: KnowledgeStore (JSON persistence + LRU eviction, keyword search) + MemoryStore (JSON persistence + time decay + importance ranking + TTL expiry)

#### tests — 38 Test Functions
- `test_shared.py`: Type enums, Pydantic model validation
- `test_neural_bus.py`: Codec roundtrip, factory methods, priority ordering, wildcard routing
- `test_cortex.py`: PID convergence, strategy state machine, insight creation, trust scoring
- `test_ganglion.py`: System/network perception, health analysis, plugin management, adapter profiles

### Supported OpenClaw Variants

OpenClaw | Hermes | Work Buddy | QClaw | CoPaw | HiClaw | Wukong | EasyClaw

### Quick Start

```bash
python scripts/install.py
clawshell init --mode ganglion
clawshell init --mode cortex
clawshell cortex --host 0.0.0.0 --port 9000
clawshell ganglion --cortex-host <server-ip> --cortex-port 9000
clawshell ganglion --offline
pytest tests/ -v
```

### Environment Variables

| Variable | Purpose |
|----------|--------|
| ALIBABA_CLOUD_ACCESS_KEY_ID | Alibaba Cloud AK |
| ALIBABA_CLOUD_ACCESS_KEY_SECRET | Alibaba Cloud SK |
| GITHUB_TOKEN | GitHub PAT |
| MEMOS_CLOUD_API_KEY | MemOS Cloud API Key |
| CLAWSHELL_CORTEX_HOST | Cortex address |
| CLAWSHELL_CORTEX_PORT | Cortex port (default: 9000) |
| CLAWSHELL_OFFLINE | Set "true" for offline |

### Build Stats

| Metric | Count |
|--------|-------|
| Source files | 28 |
| Lines of code | 2,238 |
| Enumerations | 17 |
| Pydantic models | 20+ |
| Strategy states | 5 |
| OpenClaw variants | 8 |
| Builtin plugins | 5 |
| Test functions | 38 |
| Repair layers | 3 |
| Perception dimensions | 6 |
