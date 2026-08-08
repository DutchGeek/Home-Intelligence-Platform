from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import threading
from typing import Any

from homeassistant.core import HomeAssistant

STORAGE_RELATIVE_PATH = ".storage/hip_visitor_events.json"


class VisitorStorageError(Exception):
    """Raised when visitor storage operations fail."""


class VisitorEventNotFoundError(VisitorStorageError):
    """Raised when a requested visitor event does not exist."""


class HipVisitorStorage:
    """JSON file-backed storage for Visitor Intelligence events."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._lock = threading.Lock()
        self._events: dict[str, dict[str, Any]] = {}
        self._loaded = False

    @property
    def path(self) -> Path:
        return Path(self._hass.config.path(STORAGE_RELATIVE_PATH))

    async def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        await self._ensure_loaded()
        event_id = str(payload.get("event_id") or self._new_event_id())

        with self._lock:
            if event_id in self._events:
                raise VisitorStorageError(f"event already exists: {event_id}")

            event = self._build_event(event_id, payload)
            self._events[event_id] = event

        await self._persist()
        return deepcopy(event)

    async def update(self, event_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        await self._ensure_loaded()

        with self._lock:
            if event_id not in self._events:
                raise VisitorEventNotFoundError(f"event not found: {event_id}")

            current = self._events[event_id]
            updates = self._normalized_updates(payload)

            if "timeline_append" in updates:
                current.setdefault("timeline", [])
                current["timeline"].append(updates.pop("timeline_append"))

            current.update(updates)
            current["updated_at"] = self._utcnow_iso()

            updated = deepcopy(current)

        await self._persist()
        return updated

    async def get(self, event_id: str) -> dict[str, Any]:
        await self._ensure_loaded()

        with self._lock:
            event = self._events.get(event_id)
            if event is None:
                raise VisitorEventNotFoundError(f"event not found: {event_id}")
            return deepcopy(event)

    async def list(self, *, limit: int | None = None, status: str | None = None, camera: str | None = None) -> list[dict[str, Any]]:
        await self._ensure_loaded()

        with self._lock:
            events = list(self._events.values())

        filtered = []
        for event in events:
            if status and event.get("status") != status:
                continue
            if camera and event.get("camera") != camera:
                continue
            filtered.append(deepcopy(event))

        filtered.sort(key=lambda item: str(item.get("timestamp", "")), reverse=True)
        if limit is not None:
            return filtered[: max(limit, 0)]
        return filtered

    async def delete(self, event_id: str) -> bool:
        await self._ensure_loaded()

        with self._lock:
            if event_id not in self._events:
                return False
            del self._events[event_id]

        await self._persist()
        return True

    async def _ensure_loaded(self) -> None:
        if self._loaded:
            return

        data = await self._hass.async_add_executor_job(self._read_file)
        with self._lock:
            self._events = data
            self._loaded = True

    async def _persist(self) -> None:
        with self._lock:
            payload = {
                "version": 1,
                "events": list(self._events.values()),
            }

        await self._hass.async_add_executor_job(self._write_file, payload)

    def _read_file(self) -> dict[str, dict[str, Any]]:
        path = self.path
        if not path.exists():
            return {}

        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as err:
            raise VisitorStorageError(f"failed to read visitor storage: {err}") from err

        events = parsed.get("events", []) if isinstance(parsed, dict) else []
        result: dict[str, dict[str, Any]] = {}
        if isinstance(events, list):
            for candidate in events:
                if not isinstance(candidate, dict):
                    continue
                event_id = str(candidate.get("event_id", "")).strip()
                if not event_id:
                    continue
                result[event_id] = self._coerce_event_shape(candidate)
        return result

    def _write_file(self, payload: dict[str, Any]) -> None:
        path = self.path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _build_event(self, event_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        timestamp = self._coerce_string(payload.get("timestamp")) or self._utcnow_iso()
        created_at = self._utcnow_iso()
        snapshot = self._coerce_string(payload.get("snapshot"))

        event: dict[str, Any] = {
            "event_id": event_id,
            "type": self._coerce_string(payload.get("type")) or "visitor",
            "status": self._coerce_string(payload.get("status")) or "new",
            "camera": self._coerce_string(payload.get("camera")) or "Front Door",
            "timestamp": timestamp,
            "person": self._coerce_nullable_string(payload.get("person")),
            "snapshot": snapshot,
            "confidence": self._coerce_nullable_float(payload.get("confidence")),
            "notification_sent": bool(payload.get("notification_sent", False)),
            "announcement_sent": bool(payload.get("announcement_sent", False)),
            "timeline": [],
            "created_at": created_at,
            "updated_at": created_at,
        }

        timeline_append = self._coerce_string(payload.get("timeline_append"))
        if timeline_append:
            event["timeline"].append(timeline_append)
        else:
            event["timeline"].append(f"{timestamp} Visitor event created")

        return event

    def _coerce_event_shape(self, event: dict[str, Any]) -> dict[str, Any]:
        payload = self._build_event(str(event.get("event_id")), event)
        timeline = event.get("timeline")
        if isinstance(timeline, list):
            payload["timeline"] = [str(item) for item in timeline if str(item).strip()]
        payload["created_at"] = self._coerce_string(event.get("created_at")) or payload["created_at"]
        payload["updated_at"] = self._coerce_string(event.get("updated_at")) or payload["updated_at"]
        return payload

    def _normalized_updates(self, payload: dict[str, Any]) -> dict[str, Any]:
        updates: dict[str, Any] = {}
        for key in (
            "type",
            "status",
            "camera",
            "timestamp",
            "snapshot",
        ):
            if key in payload:
                updates[key] = self._coerce_string(payload.get(key))

        if "person" in payload:
            updates["person"] = self._coerce_nullable_string(payload.get("person"))

        if "confidence" in payload:
            updates["confidence"] = self._coerce_nullable_float(payload.get("confidence"))

        if "notification_sent" in payload:
            updates["notification_sent"] = bool(payload.get("notification_sent"))

        if "announcement_sent" in payload:
            updates["announcement_sent"] = bool(payload.get("announcement_sent"))

        if "timeline_append" in payload:
            timeline_append = self._coerce_string(payload.get("timeline_append"))
            if timeline_append:
                updates["timeline_append"] = timeline_append

        return updates

    def _new_event_id(self) -> str:
        return f"visitor-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

    def _utcnow_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def _coerce_string(self, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _coerce_nullable_string(self, value: Any) -> str | None:
        text = self._coerce_string(value)
        if text in {"null", "none"}:
            return None
        return text

    def _coerce_nullable_float(self, value: Any) -> float | None:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip().lower()
        if text in {"", "null", "none"}:
            return None
        try:
            return float(text)
        except ValueError:
            return None
