"""ClawShell 2.0 — Adaptation engine"""
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Optional
import psutil
from loguru import logger
from shared.models import HealthReport, RepairAction
from shared.types import (
    HealthStatus,
    NodeID,
    OpenClawVariant,
    RepairLayer,
    Strategy,
)


class AdaptationEngine:
    MAX_HEALING_ATTEMPTS = 3
    MAX_REPAIR_ATTEMPTS = 2

    def __init__(
        self,
        node_id: NodeID,
        variant: OpenClawVariant = OpenClawVariant.UNKNOWN,
    ):
        self.node_id = node_id
        self.variant = variant
        self._health: dict[str, HealthStatus] = {}
        self._healing_history: dict[str, int] = {}
        self._repair_history: dict[str, int] = {}
        self._strategy: Strategy = Strategy.DEFAULT

    async def discover_capabilities(
        self, base_path: Optional[Path] = None
    ) -> list[dict[str, Any]]:
        caps = []
        try:
            r = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if r.returncode == 0:
                import json
                pkgs = json.loads(r.stdout)
                caps.append({
                    "domain": "python_packages",
                    "count": len(pkgs),
                    "items": [p["name"] for p in pkgs[:20]],
                })
        except Exception:
            pass
        tools = []
        for t in ["git", "docker", "node", "npm", "curl", "gh"]:
            try:
                cmd = ["where", t] if os.name == "nt" else ["which", t]
                r = subprocess.run(cmd, capture_output=True, timeout=5)
                if r.returncode == 0:
                    tools.append(t)
            except Exception:
                pass
        if tools:
            caps.append({"domain": "cli_tools", "items": tools})
        return caps

    async def analyze_health(self) -> HealthReport:
        issues = []
        comps = {}
        cpu = psutil.cpu_percent(interval=1)
        if cpu > 90:
            issues.append({
                "component": "cpu",
                "severity": "critical",
                "message": f"CPU: {cpu}%",
            })
            comps["cpu"] = HealthStatus.CRITICAL
        elif cpu > 70:
            comps["cpu"] = HealthStatus.WARNING
        else:
            comps["cpu"] = HealthStatus.HEALTHY
        mem = psutil.virtual_memory()
        if mem.percent > 95:
            issues.append({
                "component": "memory",
                "severity": "critical",
                "message": f"MEM: {mem.percent}%",
            })
            comps["memory"] = HealthStatus.CRITICAL
        elif mem.percent > 80:
            comps["memory"] = HealthStatus.WARNING
        else:
            comps["memory"] = HealthStatus.HEALTHY
        disk = psutil.disk_usage("/")
        if disk.percent > 95:
            issues.append({
                "component": "disk",
                "severity": "critical",
                "message": f"Disk: {disk.percent}%",
            })
            comps["disk"] = HealthStatus.CRITICAL
        elif disk.percent > 85:
            comps["disk"] = HealthStatus.WARNING
        else:
            comps["disk"] = HealthStatus.HEALTHY
        overall = HealthStatus.HEALTHY
        if HealthStatus.CRITICAL in comps.values():
            overall = HealthStatus.CRITICAL
        elif HealthStatus.WARNING in comps.values():
            overall = HealthStatus.WARNING
        return HealthReport(
            node_id=self.node_id,
            overall=overall,
            components=comps,
            issues=issues,
        )

    async def self_heal(self, issue: dict[str, Any]) -> RepairAction:
        comp = issue.get("component", "")
        acts = {
            "memory": {"action": "clear_cache", "params": {}},
            "cpu": {"action": "reduce_load", "params": {"max_processes": 5}},
            "disk": {"action": "clean_temp", "params": {"paths": ["/tmp"]}},
        }
        ai = acts.get(comp, {"action": "unknown", "params": {}})
        action = RepairAction(
            action_id=f"heal-{comp}-{int(time.time())}",
            component=comp,
            layer=RepairLayer.SELF_HEALING,
            action=ai["action"],
            params=ai["params"],
            triggered_by="adaptation",
        )
        success = await self._execute_healing(ai)
        action.result = {"success": success}
        return action

    async def _execute_healing(self, ai: dict) -> bool:
        if ai.get("action") == "clear_cache":
            try:
                import gc
                gc.collect()
                return True
            except Exception:
                return False
        return False

    async def should_escalate(self, issue: dict) -> tuple:
        comp = issue.get("component", "")
        ca = self._healing_history.get(comp, 0)
        if ca >= self.MAX_HEALING_ATTEMPTS:
            ra = self._repair_history.get(comp, 0)
            if ra >= self.MAX_REPAIR_ATTEMPTS:
                return True, RepairLayer.MANUAL
            return True, RepairLayer.AUTO_REPAIR
        return False, RepairLayer.SELF_HEALING

    async def degrade(self, strategy: Strategy):
        self._strategy = strategy
        logger.info(f"Degrade to {strategy.value}")

    def record_healing(self, component: str):
        prev = self._healing_history.get(component, 0)
        self._healing_history[component] = prev + 1

    def record_repair(self, component: str):
        prev = self._repair_history.get(component, 0)
        self._repair_history[component] = prev + 1
