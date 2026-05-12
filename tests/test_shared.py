"""ClawShell 2.0 — Tests: shared module"""
import pytest
from shared.types import (NodeType, NodeStatus, Strategy, EventCategory, EventPriority,
    TaskStatus, TrustLevel, HealthStatus, RepairLayer, OpenClawVariant)
from shared.models import (NodeInfo, Task, EventMessage, Insight, Plugin, SystemPerception,
    NetworkPerception, Knowledge, Memory, HealthReport, RepairAction)

class TestTypes:
    def test_node_type(self): assert NodeType.CORTEX.value == "cortex"
    def test_strategy(self): assert Strategy.DEFAULT in list(Strategy)
    def test_priority_order(self): assert EventPriority.LOW.value < EventPriority.CRITICAL.value
    def test_variants(self): assert len(list(OpenClawVariant)) >= 8

class TestModels:
    def test_node_info_defaults(self):
        info = NodeInfo(node_id="test")
        assert info.node_type == NodeType.GANGLION
        assert info.status == NodeStatus.OFFLINE

    def test_task_defaults(self):
        task = Task(task_id="t1", title="Test")
        assert task.status == TaskStatus.PENDING
        assert task.max_retries == 3

    def test_event_message(self):
        evt = EventMessage(category=EventCategory.NODE, event_type="node.online", source="g1")
        assert evt.priority == EventPriority.NORMAL

    def test_insight(self):
        i = Insight(insight_id="i1", title="T", content="C", actionable=True)
        assert i.actionable

    def test_plugin(self):
        p = Plugin(plugin_id="n8n", name="N8N")
        assert p.health_status == HealthStatus.UNKNOWN

    def test_knowledge(self):
        k = Knowledge(knowledge_id="k1", title="T", content="C", tags=["test"])
        assert k.version == 1

    def test_memory(self):
        m = Memory(memory_id="m1", content="Hello", importance=0.8)
        assert m.importance == 0.8

    def test_health_report(self):
        r = HealthReport(node_id="test")
        assert r.overall == HealthStatus.UNKNOWN
