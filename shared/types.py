"""ClawShell 2.0 — Type definitions"""
from enum import Enum
from typing import TypeAlias

class NodeType(str, Enum):
    CORTEX = "cortex"
    GANGLION = "ganglion"

class NodeStatus(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"

class Strategy(str, Enum):
    DEFAULT = "default"
    EMERGENCY = "emergency"
    ECONOMY = "economy"
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"

class EventCategory(str, Enum):
    TASK = "task"
    NODE = "node"
    INSIGHT = "insight"
    STRATEGY = "strategy"
    ERROR = "error"
    SYSTEM = "system"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"

class EventPriority(int, Enum):
    LOW = 0
    NORMAL = 50
    HIGH = 80
    CRITICAL = 100

class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class PerceptionDimension(str, Enum):
    DIGITAL = "digital"
    PHYSICAL = "physical"
    NETWORK = "network"
    SYSTEM = "system"
    CLOUD = "cloud"
    INTERNET = "internet"

class CapabilityDomain(str, Enum):
    SKILL = "skill"
    TOOL = "tool"
    API = "api"
    MODEL = "model"
    SERVICE = "service"

class TrustLevel(str, Enum):
    UNTRUSTED = "untrusted"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    FULL = "full"

class RepairLayer(str, Enum):
    SELF_HEALING = "self_healing"
    AUTO_REPAIR = "auto_repair"
    MANUAL = "manual"

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class OpenClawVariant(str, Enum):
    OPENCLAW = "openclaw"
    WORK_BUDDY = "work_buddy"
    QCLAW = "qclaw"
    COPAW = "copaw"
    HICLAW = "hiclaw"
    WUKONG = "wukong"
    HERMES = "hermes"
    EASYCLAW = "easyclaw"
    UNKNOWN = "unknown"

NodeID: TypeAlias = str
TaskID: TypeAlias = str
PluginID: TypeAlias = str
EventID: TypeAlias = str
