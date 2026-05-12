"""ClawShell 2.0 — Broadcast engine"""
import asyncio
from datetime import datetime, timezone
from typing import Any, Optional
from loguru import logger
from shared.models import Insight, Knowledge, NodeID
from neural_bus import EventBus, MessageFactory


class BroadcastEngine:
    INSIGHT_INTERVAL = 300
    KNOWLEDGE_INTERVAL = 600

    def __init__(self, node_id: NodeID, event_bus: EventBus):
        self.node_id = node_id
        self.event_bus = event_bus
        self._insights_buffer: list[Insight] = []
        self._knowledge_buffer: list[Knowledge] = []
        self._broadcast_count = 0

    async def start(self, transport=None):
        asyncio.create_task(self._insight_loop(transport))
        asyncio.create_task(self._knowledge_loop(transport))
        logger.info("Broadcast engine started")

    async def queue_insight(self, insight: Insight):
        self._insights_buffer.append(insight)
        if len(self._insights_buffer) > 100:
            self._insights_buffer = self._insights_buffer[-50:]

    async def queue_knowledge(self, knowledge: Knowledge):
        self._knowledge_buffer.append(knowledge)
        if len(self._knowledge_buffer) > 200:
            self._knowledge_buffer = self._knowledge_buffer[-100:]

    async def _insight_loop(self, transport):
        while True:
            await asyncio.sleep(self.INSIGHT_INTERVAL)
            if not self._insights_buffer:
                continue
            recent = self._insights_buffer[-5:]
            for insight in recent:
                event = MessageFactory.insight_broadcast(
                    self.node_id, insight.model_dump(mode="json")
                )
                if transport:
                    await transport.broadcast(event)
                    self._broadcast_count += 1
            self._insights_buffer = [
                i for i in self._insights_buffer if i not in recent
            ]
            logger.info(f"Insight broadcast: {len(recent)}")

    async def _knowledge_loop(self, transport):
        while True:
            await asyncio.sleep(self.KNOWLEDGE_INTERVAL)
            if not self._knowledge_buffer:
                continue
            recent = self._knowledge_buffer[-10:]
            for k in recent:
                event = MessageFactory.knowledge_update(
                    self.node_id, k.model_dump(mode="json")
                )
                if transport:
                    await transport.broadcast(event)
                    self._broadcast_count += 1
            self._knowledge_buffer = [
                k for k in self._knowledge_buffer if k not in recent
            ]
            logger.info(f"Knowledge sync: {len(recent)}")

    async def generate_behavior_optimization(
        self, insights: list[Insight]
    ) -> Optional[str]:
        if not insights:
            return None
        lines = [
            "# ClawShell behavior optimization",
            f"# Generated: {datetime.now(timezone.utc).isoformat()}",
            f"# Based on {len(insights)} insights",
            "",
        ]
        for i in insights:
            if i.actionable and i.action:
                lines.extend([
                    f"## {i.title}",
                    "",
                    i.content,
                    "",
                    f"Action: {i.action}",
                    "",
                ])
        return "\n".join(lines)

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "broadcast_count": self._broadcast_count,
            "insights_queued": len(self._insights_buffer),
            "knowledge_queued": len(self._knowledge_buffer),
        }
