"""MemOS Cloud adapter"""
from typing import Any, Optional
import httpx
from loguru import logger
from shared.models import Memory, Knowledge

class MemOSAdapter:
    BASE_URL = "https://api.memos.cloud/v1"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self._http = httpx.AsyncClient(timeout=30.0, headers={
            "Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})

    async def close(self): await self._http.aclose()

    async def store_memory(self, memory: Memory) -> bool:
        try:
            resp = await self._http.post(f"{self.BASE_URL}/memories", json={
                "content": memory.content, "category": memory.category,
                "importance": memory.importance, "tags": memory.tags,
                "source": memory.source_node or "cortex"})
            return resp.status_code in (200, 201)
        except Exception: logger.exception("MemOS store error"); return False

    async def search_memories(self, query: str, category: Optional[str] = None,
                              limit: int = 10) -> list[dict[str, Any]]:
        try:
            params = {"q": query, "limit": limit}
            if category: params["category"] = category
            resp = await self._http.get(f"{self.BASE_URL}/memories/search", params=params)
            if resp.status_code == 200:
                return resp.json().get("memories", [])
            return []
        except Exception: logger.exception("MemOS search error"); return []

    async def recall_for_context(self, query: str, max_tokens: int = 2000) -> str:
        memories = await self.search_memories(query, limit=5)
        lines = ["## Related memories"]
        for m in memories:
            lines.append(f"- [{m.get('category', '')}] {m.get('content', '')[:200]}")
        return "\n".join(lines)

    @property
    def connected(self) -> bool: return bool(self.api_key)
