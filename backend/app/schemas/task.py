from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TaskRead(BaseModel):
    id: UUID
    job_id: UUID
    status: str
    trigger_type: str
    retry_count: int
    locked_by: str | None
    locked_until: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    stdout: str | None
    stderr: str | None
    created_at: datetime


class RetryResponse(BaseModel):
    task_id: UUID
    retry_task_id: UUID
    status: str
