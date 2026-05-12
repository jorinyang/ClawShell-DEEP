"""ClawShell 2.0 — EventBus core"""
import asyncio
import heapq
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional
from loguru import logger
from shared.models import EventMessage
from shared.types import NodeID

EventHandler = Callable[[EventMessage], Awaitable[None]]

@dataclass(order=True)
class _PrioritizedEvent:
    priority_order: int
    seq: int
    event: EventMessage = field(compare=False)

class EventBus:
    MAX_QUEUE_SIZE = 10_000
    PERSIST_DIR = Path("data/eventbus")

    def __init__(self, node_id: NodeID, persist: bool = True):
        self.node_id = node_id
        self._persist = persist
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)
        self._priority_queue: list[_PrioritizedEvent] = []
        self._lock = asyncio.Lock()
        self._seq = 0
        self._running = False
        self._processed_count = 0
        self._dropped_count = 0
        if persist: self.PERSIST_DIR.mkdir(parents=True, exist_ok=True)

    def subscribe(self, pattern: str, handler: EventHandler):
        async def wrapped(event: EventMessage):
            try: await handler(event)
            except Exception: logger.exception(f"Handler [{pattern}] error")
        self._subscribers[pattern].append(wrapped)

    async def publish(self, event: EventMessage) -> None:
        if not event.event_id:
            import uuid; event.event_id = str(uuid.uuid4())
        if self._expired(event):
            self._dropped_count += 1; return
        async with self._lock:
            if len(self._priority_queue) >= self.MAX_QUEUE_SIZE:
                self._dropped_count += 1; return
            self._seq += 1
            heapq.heappush(self._priority_queue,
                _PrioritizedEvent(-event.priority.value, self._seq, event))
        if self._persist: self._persist_event(event)

    async def dispatch_loop(self) -> None:
        self._running = True
        logger.info(f"EventBus dispatch started (node={self.node_id})")
        while self._running:
            event = await self._pop_event()
            if event is None:
                await asyncio.sleep(0.01); continue
            if self._expired(event):
                self._dropped_count += 1; continue
            matched = await self._route(event)
            self._processed_count += 1
        logger.info("EventBus dispatch stopped")

    async def stop(self): self._running = False

    async def _pop_event(self) -> Optional[EventMessage]:
        async with self._lock:
            if not self._priority_queue: return None
            return heapq.heappop(self._priority_queue).event

    async def _route(self, event: EventMessage) -> int:
        event_key = f"{event.category.value}.{event.event_type}"
        matched = 0
        for handler in self._subscribers.get(event_key, []):
            await self._safe_dispatch(handler, event); matched += 1
        for handler in self._subscribers.get(f"{event.category.value}.*", []):
            await self._safe_dispatch(handler, event); matched += 1
        for handler in self._subscribers.get("*", []):
            await self._safe_dispatch(handler, event); matched += 1
        return matched

    async def _safe_dispatch(self, handler: EventHandler, event: EventMessage):
        try: await handler(event)
        except Exception: logger.exception(f"Handler error: {event.event_id}")

    def _expired(self, event: EventMessage) -> bool:
        if event.ttl_seconds <= 0: return False
        from datetime import datetime, timezone
        age = (datetime.now(timezone.utc) - event.timestamp).total_seconds()
        return age > event.ttl_seconds

    def _persist_event(self, event: EventMessage):
        try:
            date_str = event.timestamp.strftime("%Y%m%d")
            path = self.PERSIST_DIR / f"events_{date_str}.jsonl"
            with open(path, "a", encoding="utf-8") as f:
                f.write(event.model_dump_json() + "\n")
        except Exception: logger.exception("Event persist failed")

    @property
    def stats(self) -> dict[str, Any]:
        return {"node_id": self.node_id, "running": self._running,
            "queue_size": len(self._priority_queue),
            "subscriber_count": sum(len(v) for v in self._subscribers.values()),
            "processed": self._processed_count, "dropped": self._dropped_count}
