"""ClawShell 2.0 — Tests: cortex"""
import pytest
from shared.types import Strategy, TrustLevel
from neural_bus import EventBus
from cortex.core import FeedbackControlLoop, StrategySwitcher
from cortex.insight import InsightEngine
from cortex.terminal_manager import TerminalManager

class TestControlLoop:
    def test_initial(self):
        loop = FeedbackControlLoop("test")
        assert not loop.is_stable

    def test_converge(self):
        loop = FeedbackControlLoop("test", tolerance=0.1)
        loop.set_target(1.0)
        for _ in range(5): loop.update(0.98)
        assert loop.is_stable

class TestStrategySwitcher:
    def test_emergency(self):
        sw = StrategySwitcher()
        assert sw.evaluate(0.2, 0.5) == Strategy.EMERGENCY

    def test_stable(self):
        sw = StrategySwitcher()
        assert sw.evaluate(0.9, 0.2) is None

class TestInsight:
    @pytest.mark.asyncio
    async def test_create(self):
        bus = EventBus(node_id="test")
        engine = InsightEngine(node_id="test", event_bus=bus)
        i = engine._create_insight("T", "C", actionable=True)
        assert i.actionable

    @pytest.mark.asyncio
    async def test_patterns_empty(self):
        bus = EventBus(node_id="test")
        engine = InsightEngine(node_id="test", event_bus=bus)
        assert await engine.analyze_patterns() == []

class TestTerminalManager:
    def test_trust_adjust(self):
        bus = EventBus(node_id="cortex")
        mgr = TerminalManager(node_id="cortex", event_bus=bus)
        mgr._adjust_trust("g1", +0.1)
        assert mgr._trust_scores["g1"] == 0.6

    def test_trust_level(self):
        bus = EventBus(node_id="cortex")
        mgr = TerminalManager(node_id="cortex", event_bus=bus)
        mgr._trust_scores["g1"] = 0.95
        assert mgr.get_trust_level("g1") == TrustLevel.FULL
