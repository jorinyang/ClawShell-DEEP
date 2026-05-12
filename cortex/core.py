"""ClawShell 2.0 — Cortex core engine"""
import asyncio
import time
from typing import Any, Optional
from loguru import logger
from shared.models import CortexInfo, EventMessage, Task
from shared.types import (
    NodeStatus,
    NodeID,
    Strategy,
    TaskStatus,
)
from neural_bus import EventBus, CortexTransport, MessageFactory


class FeedbackControlLoop:
    def __init__(self, name: str, tolerance: float = 0.1):
        self.name = name
        self.tolerance = tolerance
        self.expected: float = 0.0
        self.actual: float = 0.0
        self.deviation: float = 0.0
        self.iteration_count: int = 0
        self.stable_count: int = 0

    def update(self, actual: float) -> float:
        self.actual = actual
        self.deviation = self.expected - actual
        self.iteration_count += 1
        if abs(self.deviation) <= self.tolerance:
            self.stable_count += 1
        else:
            self.stable_count = 0
        return self._compute_signal()

    def set_target(self, target: float):
        self.expected = target

    def _compute_signal(self) -> float:
        kp = 0.5
        ki = 0.1
        signal = kp * self.deviation + ki * self.deviation * min(
            self.iteration_count, 10
        )
        return max(-1.0, min(1.0, signal))

    @property
    def is_stable(self) -> bool:
        return self.stable_count >= 3


class StrategySwitcher:
    TRANSITIONS = {
        Strategy.DEFAULT: [Strategy.EMERGENCY, Strategy.ECONOMY, Strategy.AGGRESSIVE],
        Strategy.EMERGENCY: [Strategy.DEFAULT, Strategy.CONSERVATIVE],
        Strategy.ECONOMY: [Strategy.DEFAULT],
        Strategy.AGGRESSIVE: [Strategy.DEFAULT, Strategy.EMERGENCY],
        Strategy.CONSERVATIVE: [Strategy.DEFAULT],
    }

    def __init__(self, initial: Strategy = Strategy.DEFAULT):
        self.current = initial
        self.history: list[tuple[Strategy, float, str]] = []

    def evaluate(
        self, health_score: float, resource_pressure: float
    ) -> Optional[Strategy]:
        new = self.current
        if health_score < 0.3:
            new = Strategy.EMERGENCY
        elif resource_pressure > 0.8:
            new = Strategy.ECONOMY
        elif health_score > 0.8 and resource_pressure < 0.3:
            if self.current in (Strategy.EMERGENCY, Strategy.ECONOMY):
                new = Strategy.DEFAULT
        if new != self.current and new in self.TRANSITIONS.get(self.current, []):
            return new
        return None

    def switch(self, new_strategy: Strategy, reason: str):
        old = self.current
        self.current = new_strategy
        self.history.append((new_strategy, time.time(), reason))
        logger.info(f"Strategy: {old.value} -> {new_strategy.value} ({reason})")


class CortexCore:
    def __init__(self, node_id: NodeID = "cortex-01"):
        self.node_id = node_id
        self.info = CortexInfo(node_id=node_id)
        self.event_bus = EventBus(node_id=node_id)
        self.transport: Optional[CortexTransport] = None
        self.strategy = StrategySwitcher()
        self.control_loops: dict[str, FeedbackControlLoop] = {}
        self._start_time = time.time()
        self._health_score: float = 1.0
        self._resource_pressure: float = 0.0
        self._tasks: dict[str, Task] = {}

    async def start(self, host: str = "0.0.0.0", port: int = 9000):
        logger.info(f"Cortex starting: {self.node_id}")
        asyncio.create_task(self.event_bus.dispatch_loop())
        self.transport = CortexTransport(
            node_id=self.node_id,
            event_bus=self.event_bus,
            host=host,
            port=port,
        )
        await self.transport.start()
        self.control_loops["health"] = FeedbackControlLoop(
            "system_health", tolerance=0.05
        )
        self.control_loops["health"].set_target(1.0)
        self.event_bus.subscribe("node.online", self._on_node_online)
        self.event_bus.subscribe("node.offline", self._on_node_offline)
        self.event_bus.subscribe("node.heartbeat", self._on_node_heartbeat)
        self.event_bus.subscribe("error.alert", self._on_error_alert)
        self.event_bus.subscribe("task.completed", self._on_task_completed)
        asyncio.create_task(self._health_loop())
        logger.info("Cortex ready")
        self.info.status = NodeStatus.ONLINE

    async def stop(self):
        logger.info("Cortex stopping...")
        await self.event_bus.stop()
        if self.transport:
            await self.transport.stop()
        self.info.status = NodeStatus.OFFLINE

    async def _on_node_online(self, event: EventMessage):
        self.info.connected_ganglions += 1

    async def _on_node_offline(self, event: EventMessage):
        self.info.connected_ganglions = max(
            0, self.info.connected_ganglions - 1
        )

    async def _on_node_heartbeat(self, event: EventMessage):
        if self.transport:
            self.info.connected_ganglions = len(
                self.transport.connected_ganglions
            )

    async def _on_error_alert(self, event: EventMessage):
        self._health_score = max(0.0, self._health_score - 0.05)
        await self._evaluate_strategy()

    async def _on_task_completed(self, event: EventMessage):
        tid = event.payload.get("task_id", "")
        if tid in self._tasks:
            self._tasks[tid].status = TaskStatus.COMPLETED

    async def _health_loop(self):
        while self.info.status != NodeStatus.OFFLINE:
            await asyncio.sleep(30)
            self.info.uptime_seconds = time.time() - self._start_time
            loop = self.control_loops.get("health")
            if loop:
                loop.update(self._health_score)
            await self._evaluate_strategy()

    async def _evaluate_strategy(self):
        new = self.strategy.evaluate(
            self._health_score, self._resource_pressure
        )
        if new:
            self.strategy.switch(new, "auto")
            event = MessageFactory.strategy_change(
                self.node_id, new.value
            )
            await self.event_bus.publish(event)
            if self.transport:
                await self.transport.broadcast(event)

    async def create_task(self, task: Task) -> Task:
        self._tasks[task.task_id] = task
        event = MessageFactory.task_created(
            task.task_id, self.node_id, task.model_dump(mode="json")
        )
        await self.event_bus.publish(event)
        if self.transport:
            await self.transport.broadcast(event)
        return task

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "uptime": self.info.uptime_seconds,
            "strategy": self.strategy.current.value,
            "health_score": self._health_score,
            "connected_ganglions": self.info.connected_ganglions,
            "active_tasks": sum(
                1
                for t in self._tasks.values()
                if t.status.value in ("pending", "assigned", "running")
            ),
            "eventbus": self.event_bus.stats,
        }
