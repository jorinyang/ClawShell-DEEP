"""ClawShell 2.0 — Terminal manager"""
import asyncio, time
from typing import Any, Optional
from loguru import logger
from shared.models import EventMessage, NodeHeartbeat, NodeInfo, Task, TaskResult
from shared.types import EventCategory, EventPriority, NodeStatus, NodeID, TrustLevel, TaskStatus
from neural_bus import EventBus, MessageFactory

class TerminalManager:
    HEARTBEAT_TIMEOUT = 90
    CLEANUP_INTERVAL = 60

    def __init__(self, node_id: NodeID, event_bus: EventBus):
        self.node_id = node_id; self.event_bus = event_bus
        self._ganglions: dict[NodeID, NodeInfo] = {}
        self._heartbeats: dict[NodeID, NodeHeartbeat] = {}
        self._trust_scores: dict[NodeID, float] = {}
        self._cleanup_task = None
        event_bus.subscribe("node.register", self._on_register)
        event_bus.subscribe("node.heartbeat", self._on_heartbeat)
        event_bus.subscribe("node.offline", self._on_offline)

    async def start(self):
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        if self._cleanup_task:
            self._cleanup_task.cancel()

    async def _on_register(self, event: EventMessage):
        try:
            info = NodeInfo.model_validate(event.payload)
            info.last_heartbeat = event.timestamp
            info.status = NodeStatus.ONLINE
            self._ganglions[info.node_id] = info
            self._trust_scores[info.node_id] = 0.5
            logger.info(f"Registered: {info.node_id}")
        except Exception: logger.exception("Register parse error")

    async def _on_heartbeat(self, event: EventMessage):
        nid = event.source
        if nid in self._ganglions:
            try:
                hb = NodeHeartbeat.model_validate(event.payload)
                self._heartbeats[nid] = hb
                self._ganglions[nid].last_heartbeat = event.timestamp
                self._ganglions[nid].status = NodeStatus.ONLINE
                self._adjust_trust(nid, +0.01)
            except Exception: pass

    async def _on_offline(self, event: EventMessage):
        nid = event.source
        if nid in self._ganglions:
            self._ganglions[nid].status = NodeStatus.OFFLINE

    async def _cleanup_loop(self):
        while True:
            await asyncio.sleep(self.CLEANUP_INTERVAL)
            now = time.time()
            for nid, info in list(self._ganglions.items()):
                if now - info.last_heartbeat.timestamp() > self.HEARTBEAT_TIMEOUT:
                    info.status = NodeStatus.OFFLINE
                    self._adjust_trust(nid, -0.05)

    def _adjust_trust(self, node_id: NodeID, delta: float):
        c = self._trust_scores.get(node_id, 0.5)
        self._trust_scores[node_id] = max(0.0, min(1.0, c + delta))

    def get_trust_level(self, node_id: NodeID) -> TrustLevel:
        s = self._trust_scores.get(node_id, 0.0)
        if s < 0.2: return TrustLevel.UNTRUSTED
        if s < 0.4: return TrustLevel.LOW
        if s < 0.7: return TrustLevel.MEDIUM
        if s < 0.9: return TrustLevel.HIGH
        return TrustLevel.FULL

    async def find_best_ganglion(self, task: Task) -> Optional[NodeID]:
        candidates = [(nid, info) for nid, info in self._ganglions.items()
            if info.status == NodeStatus.ONLINE]
        if not candidates: return None
        scored = []
        for nid, info in candidates:
            hb = self._heartbeats.get(nid)
            load = hb.active_tasks if hb else 0
            trust = self._trust_scores.get(nid, 0.5)
            cap_score = 0.0
            if task.tags and info.capabilities:
                m = set(task.tags) & set(info.capabilities)
                cap_score = len(m) / max(len(task.tags), 1)
            load_score = 1.0 - min(load / 10.0, 1.0)
            total = cap_score * 0.4 + load_score * 0.3 + trust * 0.3
            scored.append((total, nid))
        scored.sort(reverse=True)
        return scored[0][1]

    async def dispatch_task(self, task: Task) -> Optional[NodeID]:
        target = await self.find_best_ganglion(task)
        if target:
            task.assigned_to = target
            task.status = TaskStatus.ASSIGNED
        return target

    def get_ganglion(self, node_id: NodeID) -> Optional[NodeInfo]:
        return self._ganglions.get(node_id)

    @property
    def online_ganglions(self) -> list[NodeInfo]:
        return [i for i in self._ganglions.values() if i.status == NodeStatus.ONLINE]

    @property
    def stats(self) -> dict[str, Any]:
        return {"total": len(self._ganglions),
            "online": len(self.online_ganglions),
            "trust_scores": dict(self._trust_scores)}
