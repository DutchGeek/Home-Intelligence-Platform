from __future__ import annotations

import asyncio
from pathlib import Path

from custom_components.hip.visitor_storage import HipVisitorStorage, VisitorEventNotFoundError


class _DummyConfig:
    def __init__(self, root: Path) -> None:
        self._root = root

    def path(self, relative_path: str) -> str:
        return str(self._root / relative_path)


class _DummyHass:
    def __init__(self, root: Path) -> None:
        self.config = _DummyConfig(root)

    async def async_add_executor_job(self, func, *args):
        return await asyncio.to_thread(func, *args)


def test_create_get_update_delete_round_trip(tmp_path: Path) -> None:
    hass = _DummyHass(tmp_path)
    storage = HipVisitorStorage(hass)  # type: ignore[arg-type]

    created = asyncio.run(
        storage.create(
        {
            "camera": "Front Door",
            "timestamp": "2026-08-08T10:15:00+00:00",
            "timeline_append": "10:15 Doorbell pressed",
        }
        )
    )

    assert created["type"] == "visitor"
    assert created["status"] == "new"
    assert created["camera"] == "Front Door"
    assert created["notification_sent"] is False
    assert created["announcement_sent"] is False
    assert created["timeline"][-1] == "10:15 Doorbell pressed"

    loaded = asyncio.run(storage.get(created["event_id"]))
    assert loaded["event_id"] == created["event_id"]

    updated = asyncio.run(
        storage.update(
            created["event_id"],
            {
                "status": "completed",
                "snapshot": "/local/snapshots/history/example.jpg",
                "notification_sent": True,
                "announcement_sent": True,
                "timeline_append": "10:15 Notification sent",
            },
        )
    )
    assert updated["status"] == "completed"
    assert updated["snapshot"] == "/local/snapshots/history/example.jpg"
    assert updated["notification_sent"] is True
    assert updated["announcement_sent"] is True
    assert updated["timeline"][-1] == "10:15 Notification sent"

    deleted = asyncio.run(storage.delete(created["event_id"]))
    assert deleted is True

    try:
        asyncio.run(storage.get(created["event_id"]))
        assert False, "Expected VisitorEventNotFoundError"
    except VisitorEventNotFoundError:
        pass


def test_list_filters_and_persistence(tmp_path: Path) -> None:
    hass = _DummyHass(tmp_path)
    storage = HipVisitorStorage(hass)  # type: ignore[arg-type]

    first = asyncio.run(
        storage.create(
            {
                "event_id": "visitor-1",
                "camera": "Front Door",
                "timestamp": "2026-08-08T08:14:00+00:00",
                "status": "new",
            }
        )
    )
    second = asyncio.run(
        storage.create(
            {
                "event_id": "visitor-2",
                "camera": "Back Door",
                "timestamp": "2026-08-08T08:15:00+00:00",
                "status": "ignored",
            }
        )
    )

    all_events = asyncio.run(storage.list())
    assert [item["event_id"] for item in all_events] == [second["event_id"], first["event_id"]]

    filtered = asyncio.run(storage.list(status="ignored"))
    assert len(filtered) == 1
    assert filtered[0]["event_id"] == "visitor-2"

    filtered_camera = asyncio.run(storage.list(camera="Front Door"))
    assert len(filtered_camera) == 1
    assert filtered_camera[0]["event_id"] == "visitor-1"

    reloaded = HipVisitorStorage(hass)  # type: ignore[arg-type]
    reloaded_events = asyncio.run(reloaded.list())
    assert len(reloaded_events) == 2
