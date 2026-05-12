"""ClawShell 2.0 — Tests: ganglion"""
import pytest
from shared.types import OpenClawVariant, HealthStatus, Strategy
from ganglion.perception import PerceptionEngine
from ganglion.adaptation import AdaptationEngine
from ganglion.plugin_manager import PluginManager
from ganglion.adapters.openclaw import OpenClawAdapter, ARCHITECTURE_PROFILES

class TestPerception:
    @pytest.mark.asyncio
    async def test_system(self):
        engine = PerceptionEngine(node_id="test")
        r = await engine.perceive_system()
        assert r.cpu_count >= 1

    @pytest.mark.asyncio
    async def test_network(self):
        engine = PerceptionEngine(node_id="test")
        r = await engine.perceive_network()
        assert r.hostname != ""

    @pytest.mark.asyncio
    async def test_full(self):
        engine = PerceptionEngine(node_id="test")
        from shared.types import PerceptionDimension
        results = await engine.full_perception()
        assert PerceptionDimension.SYSTEM in results

    @pytest.mark.asyncio
    async def test_detect_variant(self):
        engine = PerceptionEngine(node_id="test")
        v = await engine.detect_openclaw_variant()
        assert isinstance(v, OpenClawVariant)

class TestAdaptation:
    @pytest.mark.asyncio
    async def test_capabilities(self):
        engine = AdaptationEngine(node_id="test")
        caps = await engine.discover_capabilities()
        assert isinstance(caps, list)

    @pytest.mark.asyncio
    async def test_health(self):
        engine = AdaptationEngine(node_id="test")
        r = await engine.analyze_health()
        assert "cpu" in r.components

class TestPluginManager:
    @pytest.mark.asyncio
    async def test_discover(self):
        mgr = PluginManager(node_id="test")
        plugins = await mgr.discover()
        assert len(plugins) >= 4

    @pytest.mark.asyncio
    async def test_enable_disable(self):
        mgr = PluginManager(node_id="test")
        await mgr.discover()
        await mgr.disable("n8n")
        assert not mgr.get_plugin("n8n").enabled
        await mgr.enable("n8n")
        assert mgr.get_plugin("n8n").enabled

class TestOpenClawAdapter:
    def test_profiles(self):
        assert OpenClawVariant.OPENCLAW in ARCHITECTURE_PROFILES

    @pytest.mark.asyncio
    async def test_info(self):
        adapter = OpenClawAdapter(variant=OpenClawVariant.UNKNOWN)
        info = await adapter.get_architecture_info()
        assert "variant" in info
