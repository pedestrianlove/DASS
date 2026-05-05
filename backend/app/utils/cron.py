from __future__ import annotations

from datetime import datetime

from croniter import croniter


def next_cron_time(expression: str, base_time: datetime) -> datetime:
    iterator = croniter(expression, base_time)
    next_time = iterator.get_next(datetime)
    if next_time.tzinfo is None and base_time.tzinfo is not None:
        next_time = next_time.replace(tzinfo=base_time.tzinfo)
    return next_time
