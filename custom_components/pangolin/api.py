"""Small async client for the Pangolin Integration API."""
import asyncio
from urllib.parse import quote, urlsplit
from aiohttp import ClientError

class PangolinError(Exception):
    """API or transport failure."""

class PangolinAuthError(PangolinError):
    """Invalid key or insufficient permissions."""

def normalize_url(value):
    value = value.strip().rstrip("/")
    parts = urlsplit(value)
    if parts.scheme not in ("http", "https") or not parts.hostname or parts.query or parts.fragment or parts.username:
        raise ValueError("Invalid API URL")
    return value if value.endswith("/v1") else value + "/v1"

class PangolinClient:
    def __init__(self, session, url, token, org):
        self.session, self.url, self.token, self.org = session, normalize_url(url), token, org

    async def request(self, method, path, **kwargs):
        try:
            async with self.session.request(method, self.url + path,
                headers={"Authorization": "Bearer " + self.token},
                timeout=__import__("aiohttp").ClientTimeout(total=20),
                allow_redirects=False, **kwargs) as response:
                if response.status in (401, 403):
                    raise PangolinAuthError("API key invalid or missing resource permissions")
                if response.status != 200:
                    raise PangolinError(f"Pangolin HTTP {response.status}")
                body = await response.json()
                if not isinstance(body, dict) or body.get("success") is not True or body.get("error"):
                    raise PangolinError("Pangolin returned an unsuccessful response")
                return body.get("data")
        except (ClientError, asyncio.TimeoutError, ValueError) as err:
            raise PangolinError("Unable to read Pangolin API response") from err

    async def resources(self):
        result = {}
        for kind, key in (("public", "resources"), ("private", "siteResources")):
            page = 1
            while True:
                data = await self.request("GET", f"/org/{quote(self.org, safe='')}/{kind}-resources",
                    params={"page": page, "pageSize": 100})
                rows = data.get(key, data.get("resources")) if isinstance(data, dict) else None
                if not isinstance(rows, list):
                    raise PangolinError("Unexpected resource list format")
                added = 0
                for row in rows:
                    rid = row.get("resourceId") if kind == "public" else row.get("siteResourceId")
                    if rid is None or not isinstance(row.get("enabled"), bool):
                        raise PangolinError("Resource ID or enabled state missing")
                    uid = f"{kind}:{rid}"
                    if uid not in result:
                        added += 1
                    result[uid] = {**row, "kind": kind, "id": str(rid)}
                if not rows or len(rows) < 100:
                    break
                if not added:
                    raise PangolinError("Pagination did not advance")
                page += 1
        return result

    async def set_enabled(self, resource, enabled):
        await self.request("POST", f"/{resource['kind']}-resource/{quote(resource['id'], safe='')}",
            json={"enabled": enabled})
