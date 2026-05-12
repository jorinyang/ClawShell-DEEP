"""ClawShell 2.0 — Ganglion main"""
import asyncio
import signal
import sys
import uuid
from loguru import logger
from shared.config import get_ganglion_config
from shared.models import NodeInfo
from shared.types import NodeType
from neural_bus import EventBus, GanglionTransport
from ganglion.perception import PerceptionEngine
from ganglion.adaptation import AdaptationEngine
from ganglion.plugin_manager import PluginManager
from ganglion.adapters.openclaw import OpenClawAdapter

async def main():
    config = get_ganglion_config()
    node_id = config.node_id or f"ganglion-{uuid.uuid4().hex[:8]}"
    config.node_id = node_id
    logger.info(f"ClawShell Ganglion v2.0.0 — {node_id}")
    logger.info(f"Cortex: {config.cortex_host}:{config.cortex_port} | Offline: {config.offline_mode}")

    perception = PerceptionEngine(node_id=node_id)
    variant = await perception.detect_openclaw_variant()
    config.variant = variant
    logger.info(f"Architecture: {variant.value}")

    presults = await perception.full_perception()
    from shared.types import PerceptionDimension
    sd = presults.get(PerceptionDimension.SYSTEM)
    if sd:
        logger.info(f"System: CPU={sd.data.get('cpu_percent',0):.0f}% MEM={sd.data.get('memory_percent',0):.0f}%")

    adaptation = AdaptationEngine(node_id=node_id, variant=variant)
    adapter = OpenClawAdapter(variant=variant, install_path=config.variant_path)
    arch_info = await adapter.get_architecture_info()
    agents = await adapter.read_agents_file()
    await adapter.install_bridge_script()
    caps = await adaptation.discover_capabilities()
    health = await adaptation.analyze_health()
    logger.info(f"Health: {health.overall.value} | Capabilities: {len(caps)} domains")

    plugin_mgr = PluginManager(node_id=node_id, plugins_dir=config.plugins_dir)
    plugins = await plugin_mgr.discover()
    phealth = await plugin_mgr.health_check()
    healthy = sum(1 for s in phealth.values() if s.value == "healthy")
    logger.info(f"Plugins: {len(plugins)} total, {healthy} healthy")

    import platform as _plat
    node_info = NodeInfo(node_id=node_id, node_type=NodeType.GANGLION, variant=variant,
        hostname=sd.data.get("hostname", "") if sd else "",
        os=_plat.system(),
        capabilities=[f"{c['domain']}" for c in caps],
        plugins=[p.plugin_id for p in plugins if p.enabled])

    event_bus = EventBus(node_id=node_id)
    asyncio.create_task(event_bus.dispatch_loop())

    transport = GanglionTransport(node_id=node_id, event_bus=event_bus, node_info=node_info,
        cortex_host=config.cortex_host, cortex_port=config.cortex_port,
        heartbeat_interval=config.heartbeat_interval)

    if not config.offline_mode:
        await transport.start()
        logger.info("Transport connected to cortex")

    asyncio.create_task(perception.perception_loop(config.perception_interval))

    async def health_loop():
        while True:
            await asyncio.sleep(60)
            report = await adaptation.analyze_health()
            if report.overall.value in ("critical", "warning"):
                for issue in report.issues:
                    escalate, layer = await adaptation.should_escalate(issue)
                    if layer.value == "self_healing":
                        await adaptation.self_heal(issue)
                        adaptation.record_healing(issue.get("component", ""))
                    elif layer.value == "auto_repair":
                        adaptation.record_repair(issue.get("component", ""))
    asyncio.create_task(health_loop())

    def shutdown(sig, frame):
        logger.info(f"Signal {sig}, shutting down...")
        asyncio.create_task(transport.stop())
        asyncio.create_task(event_bus.stop())
        sys.exit(0)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    logger.info("Ganglion ready")
    try:
        while True: await asyncio.sleep(1)
    except asyncio.CancelledError:
        await transport.stop()
        await event_bus.stop()

if __name__ == "__main__": asyncio.run(main())
