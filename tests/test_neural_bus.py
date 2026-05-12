"""ClawShell 2.0 — Tests: neural_bus"""
import asyncio, pytest
from shared.models import EventMessage
from shared.types import EventCategory, EventPriority
from neural_bus.event_bus import EventBus
from neural_bus.protocol import MessageCodec, MessageFactory

class TestCodec:
    def test_roundtrip(self):
        evt = EventMessage(category=EventCategory.NODE, event_type="node.online", source="g1")
        enc = MessageCodec.encode(evt)
        dec = MessageCodec.decode(enc)
        assert dec.source == "g1"

    def test_bytes(self):
        evt = EventMessage(category=EventCategory.SYSTEM, event_type="startup", source="cortex")
        data = MessageCodec.encode_bytes(evt)
        assert isinstance(data, bytes)

class TestFactory:
    def test_create(self):
        msg = MessageFactory.create(EventCategory.NODE, "node.heartbeat", "g1", {"cpu": 50})
        assert msg.payload["cpu"] == 50

    def test_node_online(self):
        msg = MessageFactory.node_online("g1", {"hostname": "pc1"})
        assert msg.priority == EventPriority.HIGH

    def test_error_alert(self):
        msg = MessageFactory.error_alert("g1", {"message": "disk"})
        assert msg.priority == EventPriority.CRITICAL

class TestEventBus:
    @pytest.mark.asyncio
    async def test_publish_pop(self):
        bus = EventBus(node_id="test")
        evt = MessageFactory.create(EventCategory.TASK, "task.created", "test", {"tid": "t1"})
        await bus.publish(evt)
        popped = await bus._pop_event()
        assert popped is not None
        assert popped.payload["tid"] == "t1"

    @pytest.mark.asyncio
    async def test_priority_order(self):
        bus = EventBus(node_id="test")
        low = MessageFactory.create(EventCategory.SYSTEM, "test.low", "test", priority=EventPriority.LOW)
        critical = MessageFactory.create(EventCategory.SYSTEM, "test.critical", "test", priority=EventPriority.CRITICAL)
        await bus.publish(low); await bus.publish(critical)
        first = await bus._pop_event()
        assert first.priority == EventPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_stats(self):
        bus = EventBus(node_id="test")
        assert bus.stats["node_id"] == "test"
