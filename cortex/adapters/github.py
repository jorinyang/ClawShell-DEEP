"""GitHub adapter"""
import base64
from typing import Optional
import httpx
from loguru import logger

class GitHubAdapter:
    API_BASE = "https://api.github.com"

    def __init__(self, token: str = "", repo: str = "jorinyang/ClawShell-DEEP",
                 proxy: Optional[str] = None):
        self.token = token; self.repo = repo
        self._http = httpx.AsyncClient(timeout=30.0, headers={
            "Authorization": f"Bearer {token}" if token else "",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"}, proxy=proxy)

    async def close(self): await self._http.aclose()

    async def read_file(self, path: str, ref: str = "main") -> Optional[str]:
        try:
            url = f"{self.API_BASE}/repos/{self.repo}/contents/{path}"
            resp = await self._http.get(url, params={"ref": ref})
            if resp.status_code == 200:
                return base64.b64decode(resp.json()["content"]).decode("utf-8")
            return None
        except Exception: logger.exception(f"GitHub read error: {path}"); return None

    async def write_file(self, path: str, content: str, message: str = "auto: ClawShell",
                         branch: str = "main") -> bool:
        try:
            url = f"{self.API_BASE}/repos/{self.repo}/contents/{path}"
            sha = None
            r = await self._http.get(url, params={"ref": branch})
            if r.status_code == 200: sha = r.json().get("sha")
            body = {"message": message, "content": base64.b64encode(content.encode()).decode(), "branch": branch}
            if sha: body["sha"] = sha
            resp = await self._http.put(url, json=body)
            return resp.status_code in (200, 201)
        except Exception: logger.exception("GitHub write error"); return False

    async def get_latest_commit(self, branch: str = "main") -> Optional[dict]:
        try:
            url = f"{self.API_BASE}/repos/{self.repo}/commits/{branch}"
            resp = await self._http.get(url)
            return resp.json() if resp.status_code == 200 else None
        except Exception: return None

    async def suggest_optimization(self, content: str) -> bool:
        try:
            url = f"{self.API_BASE}/repos/{self.repo}/issues"
            resp = await self._http.post(url, json={
                "title": "[ClawShell] Optimization suggestion",
                "body": content, "labels": ["clawshell", "optimization"]})
            return resp.status_code == 201
        except Exception: return False
