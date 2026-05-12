"""ClawShell 2.0 — Plugin manager"""
from pathlib import Path
from typing import Any, Optional
import yaml
from loguru import logger
from shared.models import Plugin, PluginRegistry
from shared.types import CapabilityDomain, HealthStatus, NodeID, PluginID

class PluginManager:
    BUILTIN_PLUGINS = {
        "n8n": {"name": "N8N", "domain": CapabilityDomain.SERVICE, "provider": "n8n", "endpoint": "http://localhost:5678"},
        "memos": {"name": "MemOS", "domain": CapabilityDomain.SERVICE, "provider": "memos", "endpoint": "https://api.memos.cloud/v1"},
        "comfyui": {"name": "ComfyUI", "domain": CapabilityDomain.TOOL, "provider": "comfyui", "endpoint": "http://localhost:8188"},
        "ollama": {"name": "Ollama", "domain": CapabilityDomain.MODEL, "provider": "ollama", "endpoint": "http://localhost:11434"},
        "openclaw_skills": {"name": "OpenClaw Skills", "domain": CapabilityDomain.SKILL, "provider": "openclaw", "endpoint": None},
    }

    def __init__(self, node_id: NodeID, plugins_dir: str = "plugins"):
        self.node_id = node_id; self.plugins_dir = Path(plugins_dir)
        self._plugins: dict[PluginID, Plugin] = {}
        self._registry = PluginRegistry(node_id=node_id)

    async def discover(self) -> list[Plugin]:
        discovered = []
        for pid, info in self.BUILTIN_PLUGINS.items():
            p = Plugin(plugin_id=pid, name=info["name"], domain=info["domain"],
                provider=info["provider"], endpoint=info.get("endpoint"), enabled=True)
            discovered.append(p)
        if self.plugins_dir.exists():
            for entry in self.plugins_dir.iterdir():
                if entry.is_dir() and (entry / "plugin.yaml").exists():
                    try:
                        cfg = yaml.safe_load((entry / "plugin.yaml").read_text(encoding="utf-8"))
                        p = Plugin(plugin_id=entry.name, name=cfg.get("name", entry.name),
                            domain=CapabilityDomain(cfg.get("domain", "tool")),
                            provider=cfg.get("provider", "custom"), endpoint=cfg.get("endpoint"))
                        discovered.append(p)
                    except Exception: logger.exception(f"Plugin load error: {entry}")
        for p in discovered: self._plugins[p.plugin_id] = p
        self._registry.plugins = list(self._plugins.values())
        return discovered

    async def health_check(self) -> dict[PluginID, HealthStatus]:
        results = {}
        for pid, plugin in self._plugins.items():
            results[pid] = await self._check_plugin(plugin)
            plugin.health_status = results[pid]
        return results

    async def _check_plugin(self, plugin: Plugin) -> HealthStatus:
        if not plugin.enabled: return HealthStatus.UNKNOWN
        if plugin.endpoint:
            try:
                import httpx
                async with httpx.AsyncClient(timeout=5.0) as c:
                    r = await c.get(plugin.endpoint)
                    return HealthStatus.HEALTHY if r.status_code < 500 else HealthStatus.WARNING
            except Exception: return HealthStatus.WARNING
        return HealthStatus.UNKNOWN

    async def enable(self, plugin_id: PluginID) -> bool:
        if plugin_id in self._plugins: self._plugins[plugin_id].enabled = True; return True
        return False

    async def disable(self, plugin_id: PluginID) -> bool:
        if plugin_id in self._plugins: self._plugins[plugin_id].enabled = False; return True
        return False

    def get_plugin(self, plugin_id: PluginID) -> Optional[Plugin]:
        return self._plugins.get(plugin_id)

    def list_enabled(self) -> list[Plugin]:
        return [p for p in self._plugins.values() if p.enabled]

    @property
    def registry(self) -> PluginRegistry:
        self._registry.plugins = list(self._plugins.values())
        return self._registry
