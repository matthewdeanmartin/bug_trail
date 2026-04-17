"""SSE /events endpoint — pushes 'refresh' when DB changes."""

from __future__ import annotations

import asyncio
import logging

from fastapi import Request
from fastapi.responses import StreamingResponse

from bug_trail.app import STATE, app

logger = logging.getLogger(__name__)


@app.get("/events")
async def events(request: Request) -> StreamingResponse:
    watcher = STATE.watcher

    async def stream():
        if watcher is None:
            # No watcher configured — send a heartbeat and close.
            yield ": no watcher\n\n"
            return
        queue = watcher.subscribe()
        try:
            yield ": connected\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {msg}\n\n"
                except TimeoutError:
                    # keep-alive
                    yield ": keep-alive\n\n"
        finally:
            watcher.unsubscribe(queue)

    return StreamingResponse(stream(), media_type="text/event-stream")
