from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.job import Job


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    # ── 基本 CRUD ──────────────────────────────────────

    def create(self, task: Task) -> Task:
        """建立 Task 並 commit，回傳含 DB 生成欄位的 Task。

        # TODO: add → commit → refresh → return
        """
        raise NotImplementedError

    def create_without_commit(self, task: Task) -> Task:
        """將 Task 加入 session 但 **不 commit**（讓呼叫端決定何時 commit）。

        # TODO: 只做 self.db.add(task)，不 commit
        """
        raise NotImplementedError

    def get(self, task_id: str) -> Task | None:
        """依 primary key 取得 Task。

        # TODO: self.db.get(Task, task_id)
        """
        raise NotImplementedError

    # ── 查詢 ───────────────────────────────────────────

    def list_by_job(self, job_id: str) -> list[Task]:
        """列出指定 Job 的所有 Task，按 created_at 降冪。

        # TODO: WHERE Task.job_id == job_id, ORDER BY created_at DESC
        """
        raise NotImplementedError

    def list_recent(self, limit: int = 20) -> list[Task]:
        """列出最近的 Task（不分 Job），按 created_at 降冪，最多 limit 筆。

        # TODO: ORDER BY created_at DESC, LIMIT limit
        """
        raise NotImplementedError

    def count_running_for_job(self, job_id: str) -> int:
        """回傳指定 Job 目前 status='running' 的 Task 數量。

        # TODO: SELECT count(*) WHERE job_id=? AND status='running'
        """
        raise NotImplementedError

    # ── 原子性 Claim（最關鍵！）─────────────────────────

    def claim_pending(self, task_id: str, worker_id: str, locked_until: datetime) -> Task | None:
        """原子性地將一筆 pending Task 轉為 running，回傳成功 claim 的 Task 或 None。

        這是防止多個 Worker 重複執行同一 Task 的核心機制。

        # TODO:
        #   1. 使用 UPDATE ... WHERE id=task_id AND status='pending'
        #      設定 status='running', locked_by=worker_id,
        #      locked_until=locked_until, started_at=func.now()
        #   2. 檢查 result.rowcount：
        #      - 0 → 別人已 claim → commit 後回傳 None
        #      - >0 → claim 成功 → commit → refresh → 回傳 task
        #
        # 關鍵：UPDATE WHERE status='pending' 在 DB 層保證原子性，
        #       兩個 worker 同時 claim 只有一個會成功。
        """
        raise NotImplementedError

    # ── 狀態更新 ────────────────────────────────────────

    def mark_success(self, task: Task, stdout: str | None, stderr: str | None) -> Task:
        """將 Task 標記為成功完成。

        # TODO:
        #   設定 status='success', stdout, stderr,
        #   清除 locked_by/locked_until,
        #   設定 finished_at = datetime.now(UTC)
        #   commit + refresh
        """
        raise NotImplementedError

    def mark_failed(self, task: Task, stdout: str | None, stderr: str | None, final: bool = False) -> Task:
        """將 Task 標記為失敗。final=True 表示已用完所有 retry。

        # TODO:
        #   status = 'final_failed' if final else 'failed'
        #   設定 stdout, stderr, 清除 lock 欄位, 設定 finished_at
        #   commit + refresh
        """
        raise NotImplementedError

    def mark_running_expired_pending(self, task: Task) -> Task:
        """將過期的 running Task 重設為 pending（orphan recovery 用）。

        # TODO:
        #   status='pending', 清除 locked_by / locked_until / started_at
        #   commit + refresh
        """
        raise NotImplementedError

    def list_expired_running(self, now: datetime) -> list[Task]:
        """列出所有 locked_until 已過期的 running Task（需要被回收的 orphan）。

        # TODO:
        #   WHERE status='running' AND locked_until IS NOT NULL AND locked_until < now
        """
        raise NotImplementedError
