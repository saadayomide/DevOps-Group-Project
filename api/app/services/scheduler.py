"""Lightweight in-process scheduler for periodic shopping list refreshes.

This scheduler is intentionally simple: it runs an asyncio task that wakes up every
`REFRESH_INTERVAL_SECONDS` and refreshes shopping lists that haven't been refreshed
within `REFRESH_THRESHOLD_SECONDS` (both configurable via environment variables).

For production, consider using an external scheduler or worker (Celery/RQ/K8s CronJob).
"""
import asyncio
import os
import logging
import datetime
from typing import Optional
from app.db import SessionLocal
from app.models import ShoppingList
from app.services.refresh_service import async_refresh_shopping_list

logger = logging.getLogger(__name__)

# Configurable via env vars
REFRESH_INTERVAL_SECONDS = int(os.getenv("REFRESH_INTERVAL_SECONDS", "300"))
REFRESH_THRESHOLD_SECONDS = int(os.getenv("REFRESH_THRESHOLD_SECONDS", "3600"))

_scheduler_task: Optional[asyncio.Task] = None
_stop_event: Optional[asyncio.Event] = None


async def _scheduler_loop():
    logger.info("Scheduler loop started (interval=%s s, threshold=%s s)", REFRESH_INTERVAL_SECONDS, REFRESH_THRESHOLD_SECONDS)
    while not _stop_event.is_set():
        try:
            db = SessionLocal()
            try:
                cutoff = datetime.datetime.utcnow() - datetime.timedelta(seconds=REFRESH_THRESHOLD_SECONDS)
                lists = db.query(ShoppingList).filter(
                    (ShoppingList.last_refreshed == None) | (ShoppingList.last_refreshed < cutoff)
                ).all()
                if lists:
                    logger.info("Scheduler found %s shopping lists to refresh", len(lists))
                for sl in lists:
                    try:
                        await async_refresh_shopping_list(sl.id, db)
                    except Exception as e:
                        logger.exception("Error refreshing list %s: %s", sl.id, e)
            finally:
                db.close()
        except Exception as e:
            logger.exception("Unexpected scheduler error: %s", e)

        # Wait with early exit support
        try:
            await asyncio.wait_for(_stop_event.wait(), timeout=REFRESH_INTERVAL_SECONDS)
        except asyncio.TimeoutError:
            continue

    logger.info("Scheduler loop stopping")


def start_scheduler(loop: asyncio.AbstractEventLoop):
    global _scheduler_task, _stop_event
    if _scheduler_task and not _scheduler_task.done():
        logger.info("Scheduler already running")
        return

    _stop_event = asyncio.Event()
    _scheduler_task = loop.create_task(_scheduler_loop())
    logger.info("Scheduler task created")


async def stop_scheduler():
    global _scheduler_task, _stop_event
    if not _scheduler_task:
        return
    _stop_event.set()
    try:
        await _scheduler_task
    except Exception:
        pass
    _scheduler_task = None
    logger.info("Scheduler stopped")


def is_running() -> bool:
    return _scheduler_task is not None and not _scheduler_task.done()
