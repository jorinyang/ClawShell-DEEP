"""Alibaba Cloud adapter"""
import hmac, hashlib, base64
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone
import httpx
from loguru import logger

class AliyunAdapter:
    def __init__(self, access_key_id: str = "", access_key_secret: str = "",
                 region: str = "cn-hangzhou", oss_bucket: str = "clawshell-deep"):
        self.access_key_id = access_key_id; self.access_key_secret = access_key_secret
        self.region = region; self.oss_bucket = oss_bucket
        self.oss_endpoint = f"https://{oss_bucket}.oss-{region}.aliyuncs.com"
        self._http = httpx.AsyncClient(timeout=30.0)

    async def close(self): await self._http.aclose()

    async def oss_upload(self, key: str, content: str | bytes) -> bool:
        try:
            url = f"{self.oss_endpoint}/{key}"
            headers = self._oss_headers("PUT", key)
            if isinstance(content, str): content = content.encode("utf-8")
            resp = await self._http.put(url, content=content, headers=headers)
            ok = resp.status_code == 200
            if ok: logger.info(f"OSS upload: {key}")
            return ok
        except Exception: logger.exception(f"OSS upload error: {key}"); return False

    async def oss_download(self, key: str) -> Optional[str]:
        try:
            url = f"{self.oss_endpoint}/{key}"
            resp = await self._http.get(url, headers=self._oss_headers("GET", key))
            if resp.status_code == 200: return resp.text
            return None
        except Exception: logger.exception(f"OSS download error"); return None

    def _oss_headers(self, method: str, key: str) -> dict[str, str]:
        now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        sig_str = f"{method}\n\n\n{now}\n/{self.oss_bucket}/{key}"
        sig = hmac.new(self.access_key_secret.encode(), sig_str.encode(), hashlib.sha1).digest()
        return {"Authorization": f"OSS {self.access_key_id}:{base64.b64encode(sig).decode()}", "Date": now}
