"""ClawShell 2.0 — Perception engine"""
import asyncio
import socket
from pathlib import Path
import psutil
from loguru import logger
from shared.models import NetworkPerception, PerceptionResult, SystemPerception
from shared.types import HealthStatus, NodeID, OpenClawVariant, PerceptionDimension

class PerceptionEngine:
    def __init__(self, node_id: NodeID, variant: OpenClawVariant = OpenClawVariant.UNKNOWN):
        self.node_id = node_id; self.variant = variant
        self._last_perception: dict[PerceptionDimension, PerceptionResult] = {}

    async def perceive_system(self) -> SystemPerception:
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory(); disk = psutil.disk_usage("/")
            procs = []
            for p in psutil.process_iter(["pid", "name", "cpu_percent"]):
                try:
                    pi = p.info
                    if pi.get("cpu_percent", 0) and pi["cpu_percent"] > 1.0:
                        procs.append(dict(pi))
                except Exception: pass
            procs = sorted(procs, key=lambda x: x.get("cpu_percent", 0), reverse=True)[:10]
            return SystemPerception(cpu_percent=cpu, cpu_count=psutil.cpu_count(logical=True),
                memory_total_gb=mem.total/(1024**3), memory_used_gb=mem.used/(1024**3),
                memory_percent=mem.percent, disk_total_gb=disk.total/(1024**3),
                disk_used_gb=disk.used/(1024**3), disk_percent=disk.percent, processes=procs)
        except Exception: logger.exception("System perception error"); return SystemPerception()

    async def perceive_network(self) -> NetworkPerception:
        try:
            hostname = socket.gethostname(); ip = socket.gethostbyname(hostname)
            ports = []
            for p in [80, 443, 3000, 5000, 8080, 8443, 9000, 9090]:
                try:
                    s = socket.socket(); s.settimeout(0.5)
                    if s.connect_ex(("127.0.0.1", p)) == 0: ports.append(p)
                    s.close()
                except Exception: pass
            return NetworkPerception(hostname=hostname, ip_address=ip, open_ports=ports, internet_access=await self._check_internet())
        except Exception: logger.exception("Network perception error"); return NetworkPerception()

    async def _check_internet(self) -> bool:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as c:
                r = await c.get("https://www.google.com")
                return r.status_code < 500
        except Exception: return False

    async def full_perception(self) -> dict[PerceptionDimension, PerceptionResult]:
        results = {}
        sd = await self.perceive_system()
        results[PerceptionDimension.SYSTEM] = PerceptionResult(
            dimension=PerceptionDimension.SYSTEM, data=sd.model_dump(),
            health=HealthStatus.HEALTHY if sd.memory_percent < 90 else HealthStatus.WARNING)
        nd = await self.perceive_network()
        results[PerceptionDimension.NETWORK] = PerceptionResult(
            dimension=PerceptionDimension.NETWORK, data=nd.model_dump(),
            health=HealthStatus.HEALTHY if nd.internet_access else HealthStatus.WARNING)
        self._last_perception = results
        return results

    async def perception_loop(self, interval: int = 60):
        while True:
            await asyncio.sleep(interval)
            try: await self.full_perception()
            except Exception: logger.exception("Perception loop error")

    async def detect_openclaw_variant(self) -> OpenClawVariant:
        sigs = {OpenClawVariant.OPENCLAW: ["~/.openclaw"],
            OpenClawVariant.HERMES: ["~/.hermes"],
            OpenClawVariant.WORK_BUDDY: ["~/.workbuddy"],
            OpenClawVariant.EASYCLAW: ["~/.easyclaw"]}
        home = Path.home()
        for v, paths in sigs.items():
            for p in paths:
                if (home / p.replace("~/", "")).exists():
                    logger.info(f"Detected: {v.value}"); return v
        return OpenClawVariant.UNKNOWN

    @property
    def last_perception(self) -> dict: return self._last_perception

    @property
    def system_health(self) -> HealthStatus:
        sr = self._last_perception.get(PerceptionDimension.SYSTEM)
        if sr:
            mp = sr.data.get("memory_percent", 0); cp = sr.data.get("cpu_percent", 0)
            if mp > 95 or cp > 95: return HealthStatus.CRITICAL
            if mp > 80 or cp > 80: return HealthStatus.WARNING
            return HealthStatus.HEALTHY
        return HealthStatus.UNKNOWN
