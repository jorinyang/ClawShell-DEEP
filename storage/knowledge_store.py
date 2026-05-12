"""ClawShell 2.0 — Knowledge & memory store"""
import json
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Optional
from shared.models import Knowledge, Memory

class KnowledgeStore:
    MAX_ITEMS = 10000
    STORE_PATH = Path("data/knowledge")

    def __init__(self, store_path: Optional[Path] = None):
        self.store_path = store_path or self.STORE_PATH
        self.store_path.mkdir(parents=True, exist_ok=True)
        self._index: OrderedDict[str, Knowledge] = OrderedDict()

    async def load(self) -> int:
        count = 0
        for f in sorted(self.store_path.glob("*.json")):
            try:
                k = Knowledge.model_validate(json.loads(f.read_text(encoding="utf-8")))
                self._index[k.knowledge_id] = k; count += 1
            except Exception: pass
        return count

    async def store(self, knowledge: Knowledge) -> bool:
        self._index[knowledge.knowledge_id] = knowledge
        while len(self._index) > self.MAX_ITEMS: self._index.popitem(last=False)
        (self.store_path / f"{knowledge.knowledge_id}.json").write_text(
            knowledge.model_dump_json(indent=2), encoding="utf-8")
        return True

    async def search(self, query: str = "", category: str = "",
                     tags: list[str] | None = None, limit: int = 20) -> list[Knowledge]:
        results = []
        for k in self._index.values():
            score = 0
            if query and query.lower() in k.title.lower(): score += 3
            if query and query.lower() in k.content.lower(): score += 1
            if category and k.category == category: score += 2
            if tags: score += len(set(tags) & set(k.tags))
            if score > 0: results.append((score, k))
        results.sort(key=lambda x: x[0], reverse=True)
        return [k for _, k in results[:limit]]

    @property
    def stats(self) -> dict[str, Any]:
        cats = {}
        for k in self._index.values(): cats[k.category] = cats.get(k.category, 0) + 1
        return {"total": len(self._index), "categories": cats}

class MemoryStore:
    MAX_MEMORIES = 5000
    STORE_PATH = Path("data/memory")

    def __init__(self, store_path: Optional[Path] = None):
        self.store_path = store_path or self.STORE_PATH
        self.store_path.mkdir(parents=True, exist_ok=True)
        self._memories: OrderedDict[str, Memory] = OrderedDict()

    async def load(self) -> int:
        count = 0
        for f in sorted(self.store_path.glob("*.json")):
            try:
                m = Memory.model_validate(json.loads(f.read_text(encoding="utf-8")))
                self._memories[m.memory_id] = m; count += 1
                if count >= self.MAX_MEMORIES: break
            except Exception: pass
        return count

    async def store(self, memory: Memory) -> bool:
        self._memories[memory.memory_id] = memory
        while len(self._memories) > self.MAX_MEMORIES: self._memories.popitem(last=False)
        (self.store_path / f"{memory.memory_id}.json").write_text(
            memory.model_dump_json(indent=2), encoding="utf-8")
        return True

    async def recall(self, query: str = "", category: str = "",
                     tags: list[str] | None = None, limit: int = 10) -> list[Memory]:
        now = time.time(); scored = []
        for m in self._memories.values():
            score = m.importance * 10.0
            if query and query.lower() in m.content.lower(): score += 5
            if category and m.category == category: score += 3
            if tags: score += len(set(tags) & set(m.tags)) * 2
            age_h = (now - m.created_at.timestamp()) / 3600
            if age_h > 0: score *= max(0.1, 1.0 - age_h / (24 * 30))
            if score > 0: scored.append((score, m))
        scored.sort(key=lambda x: x[0], reverse=True)
        for _, m in scored[:limit]: m.access_count += 1
        return [m for _, m in scored[:limit]]

    @property
    def stats(self) -> dict[str, Any]:
        return {"total": len(self._memories),
            "avg_importance": sum(m.importance for m in self._memories.values()) / max(len(self._memories), 1)}
