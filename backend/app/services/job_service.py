from __future__ import annotations

from datetime import UTC

from croniter import croniter
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.task import Task
from app.repositories.job_repository import JobRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.job import HttpActionConfig, JobCreate, JobUpdate, ShellActionConfig
from app.utils.cron import next_cron_time
from app.utils.time import utcnow


class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.jobs = JobRepository(db)
        self.tasks = TaskRepository(db)

    def create_job(self, payload: JobCreate) -> Job:
        """根據 JobCreate schema 建立新 Job。

        # TODO:
        #   1. 驗證 cron_expression 是否合法（croniter.is_valid），不合法回 422
        #   2. 用 payload 欄位建立 Job model instance
        #      - next_fire_at 用 next_cron_time(cron_expression, utcnow()) 計算
        #   3. 透過 self.jobs.create() 寫入 DB
        #   4. 回傳建立好的 Job
        """
        raise NotImplementedError

    def list_jobs(self) -> list[Job]:
        """列出所有 Job。

        # TODO: 直接呼叫 self.jobs.list()
        """
        raise NotImplementedError

    def get_job(self, job_id: str) -> Job:
        """取得單一 Job，不存在則 raise 404。

        # TODO:
        #   呼叫 self.jobs.get(job_id)
        #   若 None → raise HTTPException(status_code=404, detail="Job not found")
        """
        raise NotImplementedError

    def update_job(self, job_id: str, payload: JobUpdate) -> Job:
        """更新 Job 欄位。需驗證 cron_expression 和 action_config 的合法性。

        # TODO:
        #   1. 先 get_job 確認存在
        #   2. 用 payload.model_dump(exclude_unset=True) 取得要更新的欄位
        #   3. 若有 cron_expression，驗證合法性
        #   4. 若有 action_type/action_config，用對應 schema 驗證
        #   5. setattr 更新 job 欄位
        #   6. 若 cron 改了，重算 next_fire_at
        #   7. self.jobs.update(job)
        """
        raise NotImplementedError

    def delete_job(self, job_id: str) -> None:
        """刪除指定 Job。

        # TODO: get_job → self.jobs.delete()
        """
        raise NotImplementedError

    def trigger_job(self, job_id: str, queue_client) -> Task:
        """手動觸發 Job，建立一筆 pending Task 並送入 Queue。

        # TODO:
        #   1. get_job 確認存在
        #   2. 建立 Task(job_id=..., status='pending', trigger_type='manual', retry_count=0)
        #   3. self.tasks.create(task)
        #   4. queue_client.send_task(str(task.id))
        #   5. 回傳 task
        """
        raise NotImplementedError

    def list_job_tasks(self, job_id: str) -> list[Task]:
        """列出指定 Job 的所有 Task 歷史。

        # TODO: 先 get_job 確認存在，再 self.tasks.list_by_job(job_id)
        """
        raise NotImplementedError
