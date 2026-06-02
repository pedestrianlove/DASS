from __future__ import annotations

from datetime import datetime
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import force_primary_session
from app.models.job import Job


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, job: Job) -> Job:
        # refresh() must read from primary right after commit to avoid replica lag.
        with force_primary_session(self.db):
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)

        return job

    def list(self) -> list[Job]:
        # 1. 建立查詢語句並加上排序條件
        stmt = select(Job).order_by(Job.created_at.desc())
        
        # 2. 透過 self.db 執行語句，並將結果轉換為 Job 物件列表
        result = self.db.execute(stmt)
        
        # 3. 抽取出物件並轉為清單回傳
        return result.scalars().all()

    def get(self, job_id: str) -> Job | None:
        # 透過主鍵 (Primary Key) 找單一資料，SQLAlchemy 提供了一個專屬的超級捷徑：self.db.get()
        return self.db.get(Job, job_id)
        

    def delete(self, job: Job) -> None:
        
        self.db.delete(job)
        
        self.db.commit()
        

    def update(self, job: Job) -> Job:
        with force_primary_session(self.db):
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
        return job

    def due_jobs(self, now: datetime) -> list[Job]:
        
        # 1. 建立查詢語句：選擇 Job -> 加入過濾條件 -> 加入排序 , 5/24 補上鎖定定時任務，排除非定時任務
        stmt = select(Job).where(Job.job_type == "scheduled", Job.enabled == True, Job.next_fire_at <= now ).order_by(Job.next_fire_at.asc())
        
        result = self.db.execute(stmt)
        return result.scalars().all()

    def list_updated_since(self, since: datetime | None) -> list[Job]:
        # 不預設過濾 enabled，確保能抓到被停用的任務 (Soft Delete)
        stmt = select(Job)
        
        # 若有提供 since，則只抓取該時間點之後異動過的任務 (增量拉取)
        if since is not None:
            stmt = stmt.where(Job.updated_at >= since)
        
        result = self.db.execute(stmt)
        return result.scalars().all()
