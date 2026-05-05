from __future__ import annotations

from datetime import UTC, datetime, timedelta
import json

from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.job_repository import JobRepository
from app.repositories.task_repository import TaskRepository
from app.services.execution_service import ExecutionResult, ExecutionService
from app.utils.time import utcnow


class WorkerService:
    def __init__(self, db: Session, queue_client, worker_id: str, claim_seconds: int = 300):
        self.db = db
        self.queue = queue_client
        self.worker_id = worker_id
        self.claim_seconds = claim_seconds
        self.tasks = TaskRepository(db)
        self.jobs = JobRepository(db)
        self.executor = ExecutionService()

    def claim_task(self, task_id: str) -> Task | None:
        """嘗試 claim 一筆 Task，成功回傳 Task，失敗回傳 None。

        # TODO:
        #   1. 計算 locked_until = utcnow() + timedelta(seconds=self.claim_seconds)
        #   2. 呼叫 self.tasks.claim_pending(task_id, self.worker_id, locked_until)
        #   3. 回傳結果
        """
        raise NotImplementedError

    def process_task_id(self, task_id: str) -> bool:
        """處理一筆 Task 的完整流程：claim → 執行 → 記錄結果。

        # TODO:
        #   1. claim_task(task_id) — 若失敗（None）代表別人已 claim，直接 return True
        #   2. 用 self.jobs.get(task.job_id) 取得對應 Job
        #      - Job 不存在 → mark_failed(final=True) → return True
        #   3. 呼叫 self.executor.run(job.action_type, job.action_config) 執行任務
        #      - 捕獲 Exception → 包成 ExecutionResult(success=False)
        #   4. 成功 → self.tasks.mark_success(task, result.stdout, result.stderr)
        #   5. 失敗 → self._handle_failure(task, job, stdout, stderr)
        #   6. return True
        """
        raise NotImplementedError

    def _handle_failure(self, task: Task, job, stdout: str | None, stderr: str | None) -> None:
        """處理 Task 失敗：若還有 retry 次數就建立 retry task，否則 mark final_failed。

        # TODO:
        #   1. 若 task.retry_count < job.max_retries：
        #      a. mark_failed(task, stdout, stderr, final=False)
        #      b. 建立新 Task(retry_count=task.retry_count+1, status='pending')
        #      c. create_without_commit → commit → refresh
        #      d. queue.send_task(retry_task.id)
        #   2. 否則：mark_failed(task, stdout, stderr, final=True)
        """
        raise NotImplementedError
