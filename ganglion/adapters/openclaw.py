"""ClawShell 2.0 — OpenClaw architecture adapter"""
from pathlib import Path
from typing import Any, Optional
from loguru import logger
from shared.types import OpenClawVariant

ARCHITECTURE_PROFILES: dict[OpenClawVariant, dict[str, Any]] = {
    OpenClawVariant.OPENCLAW: {"name": "OpenClaw", "config_dir": "~/.openclaw",
        "agents_file": "AGENTS.md", "soul_file": "SOUL.md", "skills_dir": "skills", "tools_dir": "tools"},
    OpenClawVariant.HERMES: {"name": "Hermes", "config_dir": "~/.hermes",
        "agents_file": "agents.md", "soul_file": "soul.md", "skills_dir": "skills", "tools_dir": "tools"},
    OpenClawVariant.WORK_BUDDY: {"name": "Work Buddy", "config_dir": "~/.workbuddy",
        "agents_file": "WORK_BUDDY.md", "soul_file": None, "skills_dir": "skills", "tools_dir": None},
    OpenClawVariant.EASYCLAW: {"name": "EasyClaw", "config_dir": "~/.easyclaw",
        "agents_file": "EASYCLAW.md", "soul_file": None, "skills_dir": "skills", "tools_dir": None},
}

class OpenClawAdapter:
    def __init__(self, variant: OpenClawVariant, install_path: str = ""):
        self.variant = variant
        self.profile = ARCHITECTURE_PROFILES.get(variant, {})
        self.install_path = Path(install_path) if install_path else Path.home() / ".openclaw"
        config_dir = self.profile.get("config_dir", "~/.openclaw")
        self.config_dir = Path(config_dir).expanduser()

    async def read_agents_file(self) -> Optional[str]:
        af = self.profile.get("agents_file", "AGENTS.md")
        path = self.config_dir / af
        return path.read_text(encoding="utf-8") if path.exists() else None

    async def read_config(self) -> dict[str, Any]:
        return {}

    async def discover_skills(self) -> list[str]:
        sd = self.profile.get("skills_dir", "skills")
        sp = self.config_dir / sd
        return [e.name for e in sp.iterdir() if e.is_dir()] if sp.exists() else []

    async def discover_tools(self) -> list[str]:
        td = self.profile.get("tools_dir")
        if td:
            tp = self.config_dir / td
            return [e.name for e in tp.iterdir()] if tp.exists() else []
        return []

    async def install_bridge_script(self, target_dir: Optional[Path] = None) -> bool:
        td = target_dir or self.config_dir / "clawshell_bridge"
        td.mkdir(parents=True, exist_ok=True)
        (td / "clawshell_hook.py").write_text('"""ClawShell bridge hook"""\nimport json\nfrom pathlib import Path\n')
        logger.info(f"Bridge installed: {td}")
        return True

    async def get_architecture_info(self) -> dict[str, Any]:
        return {"variant": self.variant.value, "name": self.profile.get("name", "Unknown"),
            "config_dir": str(self.config_dir), "skills": await self.discover_skills(),
            "tools": await self.discover_tools()}
