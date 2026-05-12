"""ClawShell 2.0 — Cortex main"""
import asyncio
import signal
import sys
from loguru import logger
from shared.config import get_cortex_config
from cortex.core import CortexCore
from cortex.insight import InsightEngine
from cortex.terminal_manager import TerminalManager
from cortex.broadcast import BroadcastEngine

async def main():
    config = get_cortex_config()
    logger.info(f"ClawShell Cortex v2.0.0 — {config.node_id}")
    logger.info(f"Listening: {config.host}:{config.port}")
    core = CortexCore(node_id=config.node_id)
    insight_engine = InsightEngine(node_id=config.node_id, event_bus=core.event_bus)
    terminal_manager = TerminalManager(node_id=config.node_id, event_bus=core.event_bus)
    broadcast = BroadcastEngine(node_id=config.node_id, event_bus=core.event_bus)
    await core.start(host=config.host, port=config.port)
    await broadcast.start(transport=core.transport)

    async def insight_loop():
        while True:
            await asyncio.sleep(300)
            insight = await insight_engine.generate_periodic_insight()
            if insight:
                await insight_engine.publish_insight(insight)
                await broadcast.queue_insight(insight)
            for p in await insight_engine.analyze_patterns():
                await insight_engine.publish_insight(p)
                await broadcast.queue_insight(p)
            for k in await insight_engine.generate_knowledge():
                await broadcast.queue_knowledge(k)
    asyncio.create_task(insight_loop())

    def shutdown(sig, frame):
        logger.info(f"Signal {sig}, shutting down...")
        asyncio.create_task(core.stop())
        sys.exit(0)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while core.info.status.value != "offline": await asyncio.sleep(1)
    except asyncio.CancelledError: await core.stop()

if __name__ == "__main__": asyncio.run(main())
