from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from threading import Lock
from typing import Callable, Iterator

from services.openai_backend_api import OpenAIBackendAPI
from utils.log import logger

DEFAULT_MAX_LEASES_PER_BACKEND = 10


@dataclass(frozen=True)
class BackendTokenRef:
    """Lightweight token holder used where callers only need backend.access_token."""

    access_token: str = ""


@dataclass
class _BackendEntry:
    backend: OpenAIBackendAPI
    access_token: str
    leases_used: int = 0
    in_use: bool = False


class OpenAIBackendPool:
    """Small in-process pool for reusable OpenAIBackendAPI sessions.

    A pooled backend is reused only while idle. Concurrent callers for the same
    token get separate backend objects, avoiding shared mutable requests.Session
    and per-request progress_callback state.
    """

    def __init__(self, max_leases_per_backend: int = DEFAULT_MAX_LEASES_PER_BACKEND) -> None:
        self.max_leases_per_backend = max(1, int(max_leases_per_backend or DEFAULT_MAX_LEASES_PER_BACKEND))
        self._lock = Lock()
        self._entries: dict[str, list[_BackendEntry]] = {}
        self._by_backend_id: dict[int, _BackendEntry] = {}

    def acquire(
        self,
        access_token: str = "",
        *,
        progress_callback: Callable[[str], None] | None = None,
    ) -> OpenAIBackendAPI:
        token = str(access_token or "").strip()
        with self._lock:
            entries = self._entries.setdefault(token, [])
            self._retire_expired_idle_locked(token)
            for entry in entries:
                if not entry.in_use and entry.leases_used < self.max_leases_per_backend:
                    entry.in_use = True
                    entry.leases_used += 1
                    backend = entry.backend
                    break
            else:
                backend = OpenAIBackendAPI(access_token=token)
                entry = _BackendEntry(
                    backend=backend,
                    access_token=token,
                    leases_used=1,
                    in_use=True,
                )
                entries.append(entry)
                self._by_backend_id[id(backend)] = entry
                logger.debug({"event": "openai_backend_pool_create", "has_token": bool(token)})
        backend.progress_callback = progress_callback
        return backend

    def release(self, backend: OpenAIBackendAPI | None) -> None:
        if backend is None:
            return
        backend.progress_callback = None
        with self._lock:
            entry = self._by_backend_id.get(id(backend))
            if entry is None:
                return
            entry.in_use = False
            if entry.leases_used >= self.max_leases_per_backend:
                self._remove_entry_locked(entry)

    def discard(self, backend: OpenAIBackendAPI | None) -> None:
        if backend is None:
            return
        backend.progress_callback = None
        with self._lock:
            entry = self._by_backend_id.get(id(backend))
            if entry is not None:
                self._remove_entry_locked(entry)

    def clear(self) -> None:
        with self._lock:
            entries = [entry for items in self._entries.values() for entry in items]
            self._entries.clear()
            self._by_backend_id.clear()
        for entry in entries:
            self._close_backend(entry.backend)

    def stats(self) -> dict[str, int]:
        with self._lock:
            entries = [entry for items in self._entries.values() for entry in items]
            return {
                "entries": len(entries),
                "in_use": sum(1 for entry in entries if entry.in_use),
                "idle": sum(1 for entry in entries if not entry.in_use),
            }

    @contextmanager
    def lease(
        self,
        access_token: str = "",
        *,
        progress_callback: Callable[[str], None] | None = None,
    ) -> Iterator[OpenAIBackendAPI]:
        backend = self.acquire(access_token, progress_callback=progress_callback)
        try:
            yield backend
        finally:
            self.release(backend)

    def _retire_expired_idle_locked(self, token: str) -> None:
        for entry in list(self._entries.get(token, [])):
            if not entry.in_use and entry.leases_used >= self.max_leases_per_backend:
                self._remove_entry_locked(entry)

    def _remove_entry_locked(self, entry: _BackendEntry) -> None:
        entries = self._entries.get(entry.access_token, [])
        if entry in entries:
            entries.remove(entry)
        if not entries:
            self._entries.pop(entry.access_token, None)
        self._by_backend_id.pop(id(entry.backend), None)
        self._close_backend(entry.backend)

    @staticmethod
    def _close_backend(backend: OpenAIBackendAPI) -> None:
        try:
            backend.session.close()
        except Exception as exc:
            logger.debug({"event": "openai_backend_pool_close_failed", "error": str(exc)})


openai_backend_pool = OpenAIBackendPool()


def backend_token_ref(access_token: str = "") -> BackendTokenRef:
    return BackendTokenRef(access_token=str(access_token or "").strip())


@contextmanager
def lease_openai_backend(
    access_token: str = "",
    *,
    progress_callback: Callable[[str], None] | None = None,
) -> Iterator[OpenAIBackendAPI]:
    with openai_backend_pool.lease(access_token, progress_callback=progress_callback) as backend:
        yield backend
