from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.task import Task
from app.queue.factory import get_queue_client
from app.repositories.task_repository import TaskRepository
from app.schemas.task import RetryResponse

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/{task_id}/retry", response_model=RetryResponse)
def retry_task(task_id: str, db: Session = Depends(get_db)):
    """重試一筆失敗的 Task。

    # TODO:
    #   1. 用 TaskRepository 取得 task，不存在 → 404
    #   2. 檢查 status 是否為 'failed' 或 'final_failed'，否則 → 409
    #   3. 建立新 Task：
    #      - job_id = 原 task 的 job_id
    #      - status = 'pending'
    #      - trigger_type = 原 task 的 trigger_type
    #      - retry_count = 原 task 的 retry_count + 1
    #   4. repo.create(retry_task)
    #   5. queue.send_task(str(retry_task.id))
    #   6. 回傳 RetryResponse(task_id=task.id, retry_task_id=retry_task.id, status=retry_task.status)
    """
    raise NotImplementedError
