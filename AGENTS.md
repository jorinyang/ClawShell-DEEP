# ClawShell 2.0 — DEEP

> **One Cloud Multi-Edge Distributed Neural Architecture**
> Octopus-inspired: 1 Cortex (Cloud Brain) + N Ganglions (Edge Brains)

## Structure

```
cortex/          # Cloud brain — planning, insight, terminal mgmt, broadcast
  core.py        #   Control loop (PID) + strategy switcher
  insight.py     #   Insight engine — pattern analysis, error storm detection
  terminal_manager.py  # Registration, heartbeat, trust, niche matching
  broadcast.py   #   Insight broadcast + knowledge sync
  main.py / cli.py
  adapters/
    aliyun.py    #   Alibaba Cloud OSS signed upload
    memos.py     #   MemOS Cloud semantic memory
    github.py    #   GitHub repo read/write + issue suggestions
ganglion/        # Edge brain — perception, adaptation, plugins
  perception.py  #   System/network 4D perception + 8 variant detection
  adaptation.py  #   Self-discovery, health analysis, layered healing
  plugin_manager.py  # 5 builtin plugins (n8n/memos/comfyui/ollama/openclaw)
  main.py
  adapters/
    openclaw.py  # 8 OpenClaw variant adapters
neural_bus/      # Neural bus — EventBus + WebSocket transport
  event_bus.py   #   Priority heap queue + wildcard subscriptions + JSONL persistence
  protocol.py    #   MessageCodec + MessageFactory (13 factory methods)
  transport.py   #   CortexTransport (WS server) + GanglionTransport (WS client + reconnect)
shared/          # Shared — types, models, config
  types.py       #   17 enums, 4 type aliases
  models.py      #   20+ Pydantic models (NodeInfo, Task, EventMessage, Insight, etc.)
  config.py      #   YAML + ENV 3-level config for CortexConfig / GanglionConfig
storage/         # Storage — knowledge + memory
  knowledge_store.py  # KnowledgeStore (JSON + LRU) + MemoryStore (decay + importance ranking)
tests/           # 4 test files
scripts/
  install.py     # One-click install
```

## Core Principles

- **Cybernetics**: Information feedback, dynamic regulation, system holistic thinking
- **Heterogeneous Equivalence**: Different modules, equal efficacy
- **Non-invasive**: No modification to target system core code
- **Low Coupling**: EventBus + standardized Schema communication
- **High Robustness**: Multi-layer error recovery (self-healing > auto-repair > manual)
- **High Generality**: Perception abstraction, adapter pattern
- **High Collaboration**: EventBus + ecological niche matching (capability 40% + load 30% + trust 30%)
- **Portability**: Cross-platform, pip install -e .
- **Idempotency**: Repeated operations have no side effects
- **Edge-Cloud Version Decoupling**: Independent evolution, no mutual impact

## Quick Start

```bash
python scripts/install.py
clawshell init --mode ganglion
clawshell init --mode cortex
clawshell cortex --host 0.0.0.0 --port 9000
clawshell ganglion --cortex-host server-ip --cortex-port 9000
clawshell ganglion --offline
```

## Run Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Environment Variables

| Variable | Purpose |
|----------|--------|
| `ALIBABA_CLOUD_ACCESS_KEY_ID` | Alibaba Cloud AK |
| `ALIBABA_CLOUD_ACCESS_KEY_SECRET` | Alibaba Cloud SK |
| `GITHUB_TOKEN` | GitHub token |
| `MEMOS_CLOUD_API_KEY` | MemOS Cloud API key |
| `CLAWSHELL_CORTEX_HOST` | Cortex address |
| `CLAWSHELL_CORTEX_PORT` | Cortex port |
| `CLAWSHELL_OFFLINE` | Offline mode |

## Supported OpenClaw Variants

OpenClaw / Hermes / Work Buddy / QClaw / CoPaw / HiClaw / Wukong / EasyClaw

---

*ClawShell 2.0 — Cybernetics-driven self-evolving exoskeleton*
