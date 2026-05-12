"""ClawShell 2.0 — Transport layer (WebSocket)"""
import asyncio
import time
from typing import Optional
import websockets
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed
from loguru import logger
from shared.models import EventMessage, NodeHeartbeat, NodeInfo
from shared.types import NodeID, NodeStatus
from .event_bus import EventBus
from .protocol import MessageCodec, MessageFactory

class NeuralTransport:
    def __init__(self, node_id: NodeID, event_bus: EventBus):
        self.node_id = node_id; self.event_bus = event_bus; self._running = False
    async def start(self): raise NotImplementedError
    async def stop(self): raise NotImplementedError
    async def send(self, target: NodeID, message: EventMessage): raise NotImplementedError
    async def broadcast(self, message: EventMessage): raise NotImplementedError

class CortexTransport(NeuralTransport):
    def __init__(self, node_id: NodeID, event_bus: EventBus,
                 host: str = "0.0.0.0", port: int = 9000, heartbeat_interval: int = 30):
        super().__init__(node_id, event_bus)
        self.host = host; self.port = port; self.heartbeat_interval = heartbeat_interval
        self._connections: dict[NodeID, ServerConnection] = {}
        self._ganglion_info: dict[NodeID, NodeInfo] = {}
        self._server: Optional[websockets.WebSocketServer] = None

    async def start(self):
        self._running = True
        self._server = await websockets.serve(self._handle_connection, self.host, self.port)
        logger.info(f"Cortex transport ws://{self.host}:{self.port}")
        asyncio.create_task(self._heartbeat_checker())

    async def stop(self):
        self._running = False
        if self._server: self._server.close(); await self._server.wait_closed()
        for conn in list(self._connections.values()): await conn.close()
        self._connections.clear()

    async def send(self, target: NodeID, message: EventMessage):
        conn = self._connections.get(target)
        if conn:
            try: await conn.send(MessageCodec.encode_bytes(message))
            except ConnectionClosed: await self._remove_ganglion(target)

    async def broadcast(self, message: EventMessage):
        for node_id, conn in list(self._connections.items()):
            try: await conn.send(MessageCodec.encode_bytes(message))
            except ConnectionClosed: await self._remove_ganglion(node_id)

    async def _handle_connection(self, ws: ServerConnection):
        node_id = "unknown"
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=10.0)
            msg = MessageCodec.decode(raw)
            if msg.category.value != "node" or msg.event_type != "node.register":
                await ws.close(1008, "Expected register"); return
            node_id = msg.source
            info = NodeInfo.model_validate(msg.payload)
            self._connections[node_id] = ws
            self._ganglion_info[node_id] = info
            online = MessageFactory.node_online(node_id, msg.payload)
            await self.event_bus.publish(online)
            logger.info(f"Ganglion connected: {node_id}")
            async for raw in ws:
                try:
                    event = MessageCodec.decode(raw)
                    await self.event_bus.publish(event)
                except Exception: logger.exception(f"Decode error from {node_id}")
        except asyncio.TimeoutError: pass
        except ConnectionClosed: pass
        finally: await self._remove_ganglion(node_id)

    async def _remove_ganglion(self, node_id: NodeID):
        if node_id in self._connections: del self._connections[node_id]
        if node_id in self._ganglion_info: del self._ganglion_info[node_id]
        offline = MessageFactory.node_offline(node_id)
        await self.event_bus.publish(offline)

    async def _heartbeat_checker(self):
        while self._running:
            await asyncio.sleep(self.heartbeat_interval)
            now = time.time()
            for nid, info in list(self._ganglion_info.items()):
                age = now - info.last_heartbeat.timestamp()
                if age > self.heartbeat_interval * 3:
                    logger.warning(f"Heartbeat timeout: {nid} ({age:.0f}s)")
                    info.status = NodeStatus.OFFLINE

    @property
    def connected_ganglions(self) -> list[NodeInfo]:
        return list(self._ganglion_info.values())

class GanglionTransport(NeuralTransport):
    def __init__(self, node_id: NodeID, event_bus: EventBus, node_info: NodeInfo,
                 cortex_host: str = "localhost", cortex_port: int = 9000,
                 heartbeat_interval: int = 30, reconnect_interval: int = 5,
                 max_reconnect_interval: int = 60):
        super().__init__(node_id, event_bus)
        self.node_info = node_info
        self.cortex_host = cortex_host; self.cortex_port = cortex_port
        self.heartbeat_interval = heartbeat_interval
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_interval = max_reconnect_interval
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._offline_buffer: list[EventMessage] = []
        self._connected = False

    async def start(self):
        self._running = True
        asyncio.create_task(self._connect_loop())

    async def stop(self):
        self._running = False
        if self._ws: await self._ws.close()

    async def send(self, target: NodeID, message: EventMessage):
        if self._ws and self._connected:
            try: await self._ws.send(MessageCodec.encode_bytes(message))
            except ConnectionClosed: self._buffer_offline(message)
        else: self._buffer_offline(message)

    async def broadcast(self, message: EventMessage):
        await self.send(self.node_id, message)

    def _buffer_offline(self, message: EventMessage):
        if len(self._offline_buffer) < 1000:
            self._offline_buffer.append(message)

    async def _connect_loop(self):
        retry_delay = self.reconnect_interval
        while self._running:
            try:
                uri = f"ws://{self.cortex_host}:{self.cortex_port}"
                async with websockets.connect(uri) as ws:
                    self._ws = ws; self._connected = True
                    retry_delay = self.reconnect_interval
                    logger.info(f"Connected to cortex {uri}")
                    from shared.types import EventCategory, EventPriority
                    register = MessageFactory.create(
                        EventCategory.NODE, "node.register", self.node_id,
                        self.node_info.model_dump(mode="json"),
                        priority=EventPriority.HIGH)
                    await ws.send(MessageCodec.encode_bytes(register))
                    while self._offline_buffer:
                        await ws.send(MessageCodec.encode_bytes(self._offline_buffer.pop(0)))
                    hb_task = asyncio.create_task(self._heartbeat(ws))
                    async for raw in ws:
                        try:
                            event = MessageCodec.decode(raw)
                            await self.event_bus.publish(event)
                        except Exception: logger.exception("Decode error")
                    hb_task.cancel()
            except (ConnectionRefusedError, OSError, asyncio.TimeoutError) as e:
                logger.warning(f"Connect failed: {e}, retry in {retry_delay}s")
                self._connected = False; await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, self.max_reconnect_interval)
            except Exception:
                logger.exception("Transport error")
                self._connected = False; await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, self.max_reconnect_interval)

    async def _heartbeat(self, ws):
        while self._connected:
            await asyncio.sleep(self.heartbeat_interval)
            try:
                import psutil
                hb = NodeHeartbeat(node_id=self.node_id,
                    cpu_percent=psutil.cpu_percent(),
                    memory_percent=psutil.virtual_memory().percent,
                    disk_percent=psutil.disk_usage("/").percent)
                event = MessageFactory.node_heartbeat(self.node_id, hb.model_dump(mode="json"))
                await ws.send(MessageCodec.encode_bytes(event))
            except ConnectionClosed: break
            except Exception: logger.exception("Heartbeat error")

    @property
    def is_connected(self) -> bool: return self._connected
