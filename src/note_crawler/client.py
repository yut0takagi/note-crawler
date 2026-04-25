from __future__ import annotations

import logging
from typing import Any, Iterator

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://note.com"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class NoteAPIError(RuntimeError):
    """Raised when note.com API returns a non-success response."""


class NoteClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        user_agent: str = DEFAULT_USER_AGENT,
        cookies: dict[str, str] | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={"User-Agent": user_agent, "Accept": "application/json"},
            cookies=cookies or {},
            follow_redirects=True,
        )

    def __enter__(self) -> "NoteClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    @retry(
        reraise=True,
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)),
    )
    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self._client.get(path, params=params)
        if resp.status_code == 429:
            logger.warning("rate limited at %s", path)
            resp.raise_for_status()
        if resp.status_code >= 500:
            resp.raise_for_status()
        if resp.status_code >= 400:
            raise NoteAPIError(f"GET {path} -> {resp.status_code}: {resp.text[:200]}")
        return resp.json()

    def get_creator(self, urlname: str) -> dict[str, Any]:
        return self._get(f"/api/v2/creators/{urlname}")

    def list_creator_contents(
        self,
        urlname: str,
        kind: str = "note",
        page: int = 1,
    ) -> dict[str, Any]:
        return self._get(
            f"/api/v2/creators/{urlname}/contents",
            params={"kind": kind, "page": page},
        )

    def iter_creator_contents(
        self, urlname: str, kind: str = "note"
    ) -> Iterator[dict[str, Any]]:
        page = 1
        while True:
            payload = self.list_creator_contents(urlname, kind=kind, page=page)
            data = payload.get("data", {})
            for item in data.get("contents", []):
                yield item
            if data.get("isLastPage", True):
                break
            page += 1

    def get_note(self, key: str) -> dict[str, Any]:
        return self._get(f"/api/v3/notes/{key}")
