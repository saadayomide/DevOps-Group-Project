"""Routes to trigger shopping list refresh operations.

Provides an endpoint to trigger a refresh run for a shopping list.
The endpoint schedules the refresh as a background task and returns 202 Accepted.
"""

import asyncio
import logging

from fastapi import APIRouter, BackgroundTasks, Query, status
from app.config import settings
import app.db as db_mod
from app.services.refresh_service import async_refresh_shopping_list
from app.services import scheduler

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.api_prefix}/refresh", tags=["Refresh"])


async def _run_refresh_background(list_id: int):
    """Background task that creates its own DB session and runs async refresh."""
    # Resolve SessionLocal at call time so tests can monkeypatch `app.db.SessionLocal`
    db = db_mod.SessionLocal()
    try:
        await async_refresh_shopping_list(list_id, db)
    except Exception as e:
        logger.exception("Background refresh failed for list %s: %s", list_id, e)
    finally:
        db.close()


@router.post("/{list_id}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_refresh(list_id: int, background_tasks: BackgroundTasks):
    """Trigger refresh for a shopping list in a background task.

    Response: 202 Accepted with no body. The actual refresh runs asynchronously.
    """
    background_tasks.add_task(_run_refresh_background, list_id)

    return {"status": "accepted", "list_id": list_id}


@router.get("/scheduler/status")
async def scheduler_status():
    """Get scheduler running status."""
    return {"running": scheduler.is_running()}


@router.post("/scheduler/enable")
async def scheduler_enable(
    background_tasks: BackgroundTasks,
    interval: int = Query(None, description="Optional interval seconds to override env var"),
):
    """Enable the in-process scheduler.

    Optionally override the poll interval for the current run.
    """
    if interval:
        # Set env var for current process only
        import os

        os.environ["REFRESH_INTERVAL_SECONDS"] = str(interval)

    loop = asyncio.get_event_loop()
    scheduler.start_scheduler(loop)
    return {"status": "started"}


@router.post("/scheduler/disable")
async def scheduler_disable():
    """Disable the in-process scheduler (graceful stop)."""
    await scheduler.stop_scheduler()
    return {"status": "stopped"}
