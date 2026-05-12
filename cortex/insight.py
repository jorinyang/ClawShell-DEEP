"""ClawShell 2.0 — Insight engine"""
import uuid
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from loguru import logger
from shared.models import EventMessage, Insight, Knowledge
from shared.types import EventCategory, EventPriority, NodeID
from neural_bus import EventBus

class InsightEngine:
    MAX_EVENT_HISTORY = 1000

    def __init__(self, node_id: NodeID, event_bus: EventBus):
        self.node_id = node_id; self.event_bus = event_bus
        self.event_history: deque[EventMessage] = deque(maxlen=self.MAX_EVENT_HISTORY)
        self.insights: list[Insight] = []
        self._error_count: dict[str, int] = {}
        event_bus.subscribe("error.alert", self._on_error)
        event_bus.subscribe("task.*", self._on_task_event)
        event_bus.subscribe("*", self._on_any_event)

    async def _on_error(self, event: EventMessage):
        self.event_history.append(event)
        self._error_count[event.source] = self._error_count.get(event.source, 0) + 1
        if self._error_count.get(event.source, 0) >= 5:
            insight = self._create_insight(
                title=f"Error storm on {event.source}",
                content=f"Node {event.source} had {self._error_count[event.source]} errors",
                category="alert", severity=EventPriority.CRITICAL,
                actionable=True, action={"type": "investigate", "target": event.source})
            await self.publish_insight(insight)

    async def _on_task_event(self, event: EventMessage):
        self.event_history.append(event)

    async def _on_any_event(self, event: EventMessage):
        self.event_history.append(event)

    async def generate_periodic_insight(self) -> Optional[Insight]:
        now = datetime.now(timezone.utc)
        recent = [e for e in self.event_history if now - e.timestamp < timedelta(minutes=5)]
        if not recent: return None
        errors = [e for e in recent if e.category == EventCategory.ERROR]
        tasks = [e for e in recent if e.category == EventCategory.TASK]
        nodes = set(e.source for e in recent)
        content = f"5-min summary: {len(nodes)} nodes, {len(tasks)} tasks, {len(errors)} errors"
        return self._create_insight(title=f"Summary {now.strftime('%H:%M')}",
            content=content, category="summary", severity=EventPriority.LOW)

    async def analyze_patterns(self) -> list[Insight]:
        now = datetime.now(timezone.utc)
        offline = [e for e in self.event_history
            if e.category == EventCategory.NODE and e.event_type == "node.offline"
            and now - e.timestamp < timedelta(hours=1)]
        if len(offline) >= 3:
            nodes = list(set(e.source for e in offline))
            return [self._create_insight(title=f"Multiple offline: {len(nodes)}",
                content=f"{len(nodes)} ganglions offline: {nodes}",
                category="pattern", severity=EventPriority.HIGH)]
        return []

    async def generate_knowledge(self) -> list[Knowledge]:
        return [Knowledge(knowledge_id=f"k-{i.insight_id}", title=i.title,
            content=i.content, category=i.category, tags=i.tags, source="insight")
            for i in self.insights[-10:] if i.actionable]

    def _create_insight(self, title: str, content: str, category: str = "general",
                        severity: EventPriority = EventPriority.NORMAL,
                        actionable: bool = False, action: Optional[dict] = None) -> Insight:
        insight = Insight(insight_id=str(uuid.uuid4()), title=title, content=content,
            category=category, severity=severity, source_node=self.node_id,
            actionable=actionable, action=action)
        self.insights.append(insight)
        return insight

    async def publish_insight(self, insight: Insight):
        from neural_bus import MessageFactory
        event = MessageFactory.insight_broadcast(self.node_id, insight.model_dump(mode="json"))
        await self.event_bus.publish(event)
        logger.info(f"Insight: {insight.title}")

    @property
    def stats(self) -> dict[str, Any]:
        return {"total_events": len(self.event_history),
            "total_insights": len(self.insights), "error_counts": self._error_count}
