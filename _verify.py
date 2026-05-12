import sys, asyncio
sys.path.insert(0, r"D:\ClawShell-DEEP")
errors = []

# 1. Types
try:
    from shared.types import NodeType, Strategy, EventCategory, OpenClawVariant
    assert NodeType.CORTEX.value == "cortex"
    assert len(list(OpenClawVariant)) == 9
    print("[PASS] types.py")
except Exception as e: errors.append(f"types: {e}")

# 2. Models
try:
    from shared.models import NodeInfo, Task, EventMessage, Insight
    info = NodeInfo(node_id="test")
    task = Task(task_id="t1", title="Test")
    print("[PASS] models.py")
except Exception as e: errors.append(f"models: {e}")

# 3. Config
try:
    from shared.config import ConfigLoader
    cfg = ConfigLoader().load_cortex()
    assert cfg.port == 9000
    print("[PASS] config.py")
except Exception as e: errors.append(f"config: {e}")

# 4. Protocol
try:
    from neural_bus.protocol import MessageCodec, MessageFactory
    from shared.types import EventCategory
    msg = MessageFactory.create(EventCategory.NODE, "test", "src")
    enc = MessageCodec.encode(msg)
    dec = MessageCodec.decode(enc)
    assert dec.source == "src"
    print("[PASS] protocol.py")
except Exception as e: errors.append(f"protocol: {e}")

# 5. EventBus
try:
    from neural_bus.event_bus import EventBus
    bus = EventBus(node_id="test")
    assert bus.stats["node_id"] == "test"
    print("[PASS] event_bus.py")
except Exception as e: errors.append(f"event_bus: {e}")

# 6. Core + Control Loop
try:
    from cortex.core import FeedbackControlLoop, StrategySwitcher
    loop = FeedbackControlLoop("test")
    loop.set_target(1.0)
    for _ in range(5): loop.update(0.98)
    assert loop.is_stable
    sw = StrategySwitcher()
    assert sw.evaluate(0.2, 0.5) == Strategy.EMERGENCY
    print("[PASS] cortex/core.py")
except Exception as e: errors.append(f"core: {e}")

# 7. Insight
try:
    from cortex.insight import InsightEngine
    from neural_bus.event_bus import EventBus
    bus2 = EventBus(node_id="test")
    engine = InsightEngine(node_id="test", event_bus=bus2)
    i = engine._create_insight("T", "C", actionable=True)
    assert i.actionable
    print("[PASS] cortex/insight.py")
except Exception as e: errors.append(f"insight: {e}")

# 8. Terminal Manager
try:
    from cortex.terminal_manager import TerminalManager
    from neural_bus.event_bus import EventBus
    bus3 = EventBus(node_id="cortex")
    mgr = TerminalManager(node_id="cortex", event_bus=bus3)
    mgr._adjust_trust("g1", 0.5)
    assert mgr._trust_scores["g1"] == 1.0
    print("[PASS] cortex/terminal_manager.py")
except Exception as e: errors.append(f"terminal: {e}")

# 9. Broadcast
try:
    from cortex.broadcast import BroadcastEngine
    from neural_bus.event_bus import EventBus
    bus4 = EventBus(node_id="cortex")
    be = BroadcastEngine(node_id="cortex", event_bus=bus4)
    print("[PASS] cortex/broadcast.py")
except Exception as e: errors.append(f"broadcast: {e}")

# 10. Perception
try:
    from ganglion.perception import PerceptionEngine
    pe = PerceptionEngine(node_id="test")
    print("[PASS] ganglion/perception.py")
except Exception as e: errors.append(f"perception: {e}")

# 11. Adaptation
try:
    from ganglion.adaptation import AdaptationEngine
    ae = AdaptationEngine(node_id="test")
    print("[PASS] ganglion/adaptation.py")
except Exception as e: errors.append(f"adaptation: {e}")

# 12. Plugin Manager
try:
    from ganglion.plugin_manager import PluginManager
    pm = PluginManager(node_id="test")
    print("[PASS] ganglion/plugin_manager.py")
except Exception as e: errors.append(f"plugin: {e}")

# 13. OpenClaw Adapter
try:
    from ganglion.adapters.openclaw import OpenClawAdapter, ARCHITECTURE_PROFILES
    assert OpenClawVariant.OPENCLAW in ARCHITECTURE_PROFILES
    print("[PASS] ganglion/adapters/openclaw.py")
except Exception as e: errors.append(f"openclaw: {e}")

# 14. Storage
try:
    from storage.knowledge_store import KnowledgeStore, MemoryStore
    print("[PASS] storage/knowledge_store.py")
except Exception as e: errors.append(f"storage: {e}")

# 15. main entrypoints
try:
    from cortex.main import main as cortex_main
    from ganglion.main import main as ganglion_main
    print("[PASS] main entrypoints")
except Exception as e: errors.append(f"main: {e}")

if errors:
    print(f"\nFAILURES: {len(errors)}")
    for e in errors: print(f"  {e}")
else:
    print(f"\nALL 15 MODULE TESTS PASSED")
