"""ClawShell 2.0 — Message codec and factory"""
import json
import uuid
from typing import Any
from shared.models import EventMessage
from shared.types import EventCategory, EventPriority, NodeID


class MessageCodec:
    @staticmethod
    def encode(message: EventMessage) -> str:
        data = message.model_dump(mode="json")
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def decode(raw: str | bytes) -> EventMessage:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        data = json.loads(raw)
        return EventMessage.model_validate(data)

    @staticmethod
    def encode_bytes(message: EventMessage) -> bytes:
        return MessageCodec.encode(message).encode("utf-8")


class MessageFactory:
    @staticmethod
    def create(
        category: EventCategory,
        event_type: str,
        source: NodeID,
        payload: dict[str, Any] | None = None,
        target: NodeID | None = None,
        priority: EventPriority = EventPriority.NORMAL,
        ttl_seconds: int = 60,
    ) -> EventMessage:
        return EventMessage(
            event_id=str(uuid.uuid4()),
            category=category,
            event_type=event_type,
            source=source,
            target=target,
            priority=priority,
            payload=payload or {},
            ttl_seconds=ttl_seconds,
        )

    @staticmethod
    def node_online(node_id: NodeID, node_info: dict) -> EventMessage:
        return MessageFactory.create(
            EventCategory.NODE,
            "node.online",
            node_id,
            node_info,
            priority=EventPriority.HIGH,
        )

    @staticmethod
    def node_offline(node_id: NodeID) -> EventMessage:
        return MessageFactory.create(
            EventCategory.NODE,
            "node.offline",
            node_id,
            priority=EventPriority.HIGH,
        )

    @staticmethod
    def node_heartbeat(node_id: NodeID, metrics: dict) -> EventMessage:
        return MessageFactory.create(
            EventCategory.NODE,
            "node.heartbeat",
            node_id,
            metrics,
            priority=EventPriority.LOW,
        )

    @staticmethod
    def task_created(
        task_id: str, source: NodeID, payload: dict
    ) -> EventMessage:
        return MessageFactory.create(
            EventCategory.TASK,
            "task.created",
            source,
            payload,
            priority=EventPriority.NORMAL,
        )

    @staticmethod
    def task_completed(
        task_id: str, source: NodeID, result: dict
    ) -> EventMessage:
        return MessageFactory.create(
            EventCategory.TASK,
            "task.completed",
            source,
            {"task_id": task_id, "result": result},
        )

    @staticmethod
    def insight_broadcast(source: NodeID, insight: dict) -> EventMessage:
        return MessageFactory.create(
            EventCategory.INSIGHT,
            "insight.broadcast",
            source,
            insight,
            priority=EventPriority.HIGH,
        )

    @staticmethod
    def error_alert(source: NodeID, error: dict) -> EventMessage:
        return MessageFactory.create(
            EventCategory.ERROR,
            "error.alert",
            source,
            error,
            priority=EventPriority.CRITICAL,
        )

    @staticmethod
    def strategy_change(source: NodeID, strategy: str) -> EventMessage:
        return MessageFactory.create(
            EventCategory.STRATEGY,
            "strategy.change",
            source,
            {"strategy": strategy},
            priority=EventPriority.HIGH,
        )

    @staticmethod
    def knowledge_update(source: NodeID, knowledge: dict) -> EventMessage:
        return MessageFactory.create(
            EventCategory.KNOWLEDGE,
            "knowledge.update",
            source,
            knowledge,
            priority=EventPriority.NORMAL,
        )
