from __future__ import annotations

from datetime import datetime
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, job: Job) -> Job:
        """將 Job 實體寫入資料庫並回傳（含 commit + refresh）。

        # TODO:
        #   1. 用 self.db.add() 加入 session
        #   2. commit
        #   3. refresh 以取得 DB 產生的欄位（id, created_at）
        #   4. 回傳 job
        """
        raise NotImplementedError

    def list(self) -> list[Job]:
        """回傳所有 Job，按 created_at 降冪排序。

        # TODO:
        #   使用 select(Job).order_by(Job.created_at.desc())
        """
        raise NotImplementedError

    def get(self, job_id: str) -> Job | None:
        """依 primary key 取得單一 Job，找不到回傳 None。

        # TODO:
        #   使用 self.db.get(Job, job_id)
        """
        raise NotImplementedError

    def delete(self, job: Job) -> None:
        """刪除指定 Job 並 commit。

        # TODO:
        #   1. self.db.delete(job)
        #   2. commit
        """
        raise NotImplementedError

    def update(self, job: Job) -> Job:
        """更新已修改的 Job 欄位並回傳（含 commit + refresh）。

        # TODO:
        #   1. self.db.add(job)（merge 進 session）
        #   2. commit
        #   3. refresh
        #   4. 回傳 job
        """
        raise NotImplementedError

    def due_jobs(self, now: datetime) -> list[Job]:
        """回傳所有已啟用且 next_fire_at <= now 的 Job，按 next_fire_at 升冪排序。

        # TODO:
        #   篩選條件：Job.enabled == True AND Job.next_fire_at <= now
        #   排序：Job.next_fire_at.asc()
        """
        raise NotImplementedError
