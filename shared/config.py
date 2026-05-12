"""ClawShell 2.0 — Configuration management"""
import os
from pathlib import Path
from typing import Any, Optional
import yaml
from .types import Strategy
from .models import CortexConfig, GanglionConfig


class ConfigLoader:
    DEFAULT_CORTEX_CONFIG_PATH = "config/cortex.yaml"
    DEFAULT_GANGLION_CONFIG_PATH = "config/ganglion.yaml"

    def __init__(self, config_dir: Optional[Path] = None):
        default = os.getenv("CLAWSHELL_CONFIG_DIR", "config")
        self.config_dir = config_dir or Path(default)

    def load_cortex(self, path: Optional[str] = None) -> CortexConfig:
        config = CortexConfig()
        file_path = Path(path or self.DEFAULT_CORTEX_CONFIG_PATH)
        if file_path.exists():
            data = self._read_yaml(file_path)
            config = self._merge_env(config, data, "CLAWSHELL_CORTEX_")
        config.node_id = os.getenv(
            "CLAWSHELL_CORTEX_NODE_ID", config.node_id
        )
        config.host = os.getenv("CLAWSHELL_CORTEX_HOST", config.host)
        port = os.getenv("CLAWSHELL_CORTEX_PORT")
        if port:
            config.port = int(port)
        strategy = os.getenv("CLAWSHELL_CORTEX_STRATEGY")
        if strategy:
            config.strategy = Strategy(strategy)
        ecs_ak = config.cloud.aliyun_ecs.get("access_key_id", "")
        config.cloud.aliyun_ecs["access_key_id"] = os.getenv(
            "ALIBABA_CLOUD_ACCESS_KEY_ID", ecs_ak
        )
        ecs_sk = config.cloud.aliyun_ecs.get("access_key_secret", "")
        config.cloud.aliyun_ecs["access_key_secret"] = os.getenv(
            "ALIBABA_CLOUD_ACCESS_KEY_SECRET", ecs_sk
        )
        config.cloud.github_token = os.getenv(
            "GITHUB_TOKEN", config.cloud.github_token
        )
        mc_ak = config.cloud.memos_cloud.get("api_key", "")
        config.cloud.memos_cloud["api_key"] = os.getenv(
            "MEMOS_CLOUD_API_KEY", mc_ak
        )
        return config

    def load_ganglion(self, path: Optional[str] = None) -> GanglionConfig:
        config = GanglionConfig()
        file_path = Path(path or self.DEFAULT_GANGLION_CONFIG_PATH)
        if file_path.exists():
            data = self._read_yaml(file_path)
            config = self._merge_env(config, data, "CLAWSHELL_GANGLION_")
        config.node_id = os.getenv(
            "CLAWSHELL_GANGLION_NODE_ID", config.node_id
        )
        config.cortex_host = os.getenv(
            "CLAWSHELL_CORTEX_HOST", config.cortex_host
        )
        port = os.getenv("CLAWSHELL_CORTEX_PORT")
        if port:
            config.cortex_port = int(port)
        offline = os.getenv("CLAWSHELL_OFFLINE", "")
        config.offline_mode = offline.lower() == "true"
        config.cloud.github_token = os.getenv(
            "GITHUB_TOKEN", config.cloud.github_token
        )
        mc_ak = config.cloud.memos_cloud.get("api_key", "")
        config.cloud.memos_cloud["api_key"] = os.getenv(
            "MEMOS_CLOUD_API_KEY", mc_ak
        )
        return config

    def _read_yaml(self, path: Path) -> dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _merge_env(
        self, config: Any, data: dict[str, Any], prefix: str
    ) -> Any:
        for key, value in data.items():
            if hasattr(config, key):
                env_val = os.getenv(f"{prefix}{key.upper()}")
                setattr(config, key, env_val if env_val else value)
        return config


_config_loader: Optional[ConfigLoader] = None
_cortex_config: Optional[CortexConfig] = None
_ganglion_config: Optional[GanglionConfig] = None


def get_config_loader() -> ConfigLoader:
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def get_cortex_config() -> CortexConfig:
    global _cortex_config
    if _cortex_config is None:
        _cortex_config = get_config_loader().load_cortex()
    return _cortex_config


def get_ganglion_config() -> GanglionConfig:
    global _ganglion_config
    if _ganglion_config is None:
        _ganglion_config = get_config_loader().load_ganglion()
    return _ganglion_config
