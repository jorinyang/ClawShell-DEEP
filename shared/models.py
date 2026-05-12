"""ClawShell 2.0 — Pydantic core data models"""
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field
from .types import (NodeType, NodeStatus, Strategy, EventCategory, EventPriority,
    TaskStatus, HealthStatus, RepairLayer, OpenClawVariant,
    PerceptionDimension, CapabilityDomain, NodeID, TaskID, PluginID)

class NodeInfo(BaseModel):
    node_id: NodeID; node_type: NodeType = NodeType.GANGLION
    variant: OpenClawVariant = OpenClawVariant.UNKNOWN
    hostname: str = ""; os: str = ""; arch: str = ""; ip_address: str = ""
    status: NodeStatus = NodeStatus.OFFLINE
    capabilities: list[str] = Field(default_factory=list)
    plugins: list[str] = Field(default_factory=list)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)

class NodeHeartbeat(BaseModel):
    node_id: NodeID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: NodeStatus = NodeStatus.ONLINE
    cpu_percent: float = 0.0; memory_percent: float = 0.0; disk_percent: float = 0.0
    active_tasks: int = 0

class CortexInfo(BaseModel):
    node_id: NodeID = "cortex-01"; node_type: NodeType = NodeType.CORTEX
    version: str = "2.0.0"; status: NodeStatus = NodeStatus.ONLINE
    connected_ganglions: int = 0; uptime_seconds: float = 0.0

class Task(BaseModel):
    task_id: TaskID; title: str; description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: EventPriority = EventPriority.NORMAL
    assigned_to: Optional[NodeID] = None; created_by: Optional[NodeID] = None
    tags: list[str] = Field(default_factory=list)
    dependencies: list[TaskID] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)
    result: Optional[dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None; completed_at: Optional[datetime] = None
    max_retries: int = 3; retry_count: int = 0; timeout_seconds: int = 300

class TaskResult(BaseModel):
    task_id: TaskID; success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    error_message: str = ""; duration_ms: float = 0.0
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EventMessage(BaseModel):
    event_id: str = ""; category: EventCategory; event_type: str
    source: NodeID; target: Optional[NodeID] = None
    priority: EventPriority = EventPriority.NORMAL
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None; ttl_seconds: int = 60

class Insight(BaseModel):
    insight_id: str; title: str; content: str; category: str = "general"
    severity: EventPriority = EventPriority.NORMAL
    source_node: Optional[NodeID] = None
    tags: list[str] = Field(default_factory=list)
    actionable: bool = False; action: Optional[dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

class Plugin(BaseModel):
    plugin_id: PluginID; name: str; version: str = "0.1.0"; description: str = ""
    domain: CapabilityDomain = CapabilityDomain.TOOL
    provider: str = ""; endpoint: Optional[str] = None
    config: dict[str, Any] = Field(default_factory=dict)
    health_status: HealthStatus = HealthStatus.UNKNOWN
    enabled: bool = True; last_checked: Optional[datetime] = None

class CloudConfig(BaseModel):
    aliyun_ecs: dict[str, str] = Field(default_factory=dict)
    aliyun_oss: dict[str, str] = Field(default_factory=dict)
    github_token: str = ""; github_repo: str = ""
    memos_cloud: dict[str, str] = Field(default_factory=dict)

class CortexConfig(BaseModel):
    node_id: NodeID = "cortex-01"; host: str = "0.0.0.0"; port: int = 9000
    strategy: Strategy = Strategy.DEFAULT
    heartbeat_interval: int = 30; max_ganglions: int = 100
    insight_broadcast_interval: int = 300; knowledge_sync_interval: int = 600
    cloud: CloudConfig = Field(default_factory=CloudConfig)

class GanglionConfig(BaseModel):
    node_id: NodeID = ""; cortex_host: str = "localhost"; cortex_port: int = 9000
    variant: OpenClawVariant = OpenClawVariant.UNKNOWN; variant_path: str = ""
    strategy: Strategy = Strategy.DEFAULT
    heartbeat_interval: int = 30; perception_interval: int = 60
    auto_register: bool = True; offline_mode: bool = False
    plugins_dir: str = "plugins"
    cloud: CloudConfig = Field(default_factory=CloudConfig)

class PerceptionResult(BaseModel):
    dimension: PerceptionDimension
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict[str, Any] = Field(default_factory=dict)
    health: HealthStatus = HealthStatus.UNKNOWN

class SystemPerception(BaseModel):
    cpu_percent: float = 0.0; cpu_count: int = 1
    memory_total_gb: float = 0.0; memory_used_gb: float = 0.0; memory_percent: float = 0.0
    disk_total_gb: float = 0.0; disk_used_gb: float = 0.0; disk_percent: float = 0.0
    processes: list[dict[str, Any]] = Field(default_factory=list)

class NetworkPerception(BaseModel):
    hostname: str = ""; ip_address: str = ""; mac_address: str = ""
    open_ports: list[int] = Field(default_factory=list)
    services: list[dict[str, Any]] = Field(default_factory=list)
    internet_access: bool = False

class Knowledge(BaseModel):
    knowledge_id: str; title: str; content: str; category: str = ""
    tags: list[str] = Field(default_factory=list); source: str = ""
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)

class Memory(BaseModel):
    memory_id: str; content: str
    embedding: Optional[list[float]] = None; category: str = "session"
    importance: float = 0.5; tags: list[str] = Field(default_factory=list)
    source_node: Optional[NodeID] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    accessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0; ttl_seconds: int = 0

class HealthReport(BaseModel):
    node_id: NodeID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    overall: HealthStatus = HealthStatus.UNKNOWN
    components: dict[str, HealthStatus] = Field(default_factory=dict)
    issues: list[dict[str, Any]] = Field(default_factory=list)

class RepairAction(BaseModel):
    action_id: str; component: str; layer: RepairLayer = RepairLayer.SELF_HEALING
    action: str; params: dict[str, Any] = Field(default_factory=dict)
    triggered_by: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    result: Optional[dict[str, Any]] = None

class PluginRegistry(BaseModel):
    node_id: NodeID
    plugins: list[Plugin] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
