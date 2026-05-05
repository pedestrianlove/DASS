from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.models.job import Job
from app.models.task import Task
from app.services.scheduler_service import SchedulerService
from app.services.worker_service import WorkerService
from app.queue.memory import MemoryQueueClient
from app.services.execution_service import ExecutionService


def _job(db_session, **overrides):
    job = Job(
        id=str(uuid4()),
        name=overrides.get("name", f"job-{uuid4()}"),
        cron_expression="* * * * *",
        action_type=overrides.get("action_type", "http"),
        action_config=overrides.get("action_config", {"method": "GET", "url": "https://example.com", "timeout_seconds": 1}),
        enabled=overrides.get("enabled", True),
        concurrency_policy=overrides.get("concurrency_policy", "allow"),
        max_retries=overrides.get("max_retries", 0),
        next_fire_at=datetime.now(UTC) - timedelta(seconds=1),
    )
    db_session.add(job)
    db_session.commit()
    return job


def test_scheduler_dispatch_due_job(db_session):
    queue = MemoryQueueClient()
    job = _job(db_session)
    service = SchedulerService(db_session, queue)
    created = service.dispatch_due_jobs()
    assert created == 1
    tasks = db_session.query(Task).filter(Task.job_id == job.id).all()
    assert len(tasks) == 1


def test_concurrency_policy_forbid_skips_running_task(db_session):
    queue = MemoryQueueClient()
    job = _job(db_session, concurrency_policy="forbid")
    running = Task(job_id=job.id, status="running", trigger_type="scheduled", retry_count=0)
    db_session.add(running)
    db_session.commit()
    service = SchedulerService(db_session, queue)
    service.dispatch_due_jobs()
    tasks = db_session.query(Task).filter(Task.job_id == job.id).all()
    assert len(tasks) == 1


def test_worker_claims_pending_task_atomically(db_session):
    queue = MemoryQueueClient()
    job = _job(db_session)
    task = Task(job_id=job.id, status="pending", trigger_type="manual", retry_count=0)
    db_session.add(task)
    db_session.commit()
    service = WorkerService(db_session, queue, "worker-1")
    claimed = service.claim_task(str(task.id))
    assert claimed is not None
    assert claimed.status == "running"


def test_worker_executes_http_action(monkeypatch, db_session):
    queue = MemoryQueueClient()
    job = _job(db_session)
    task = Task(job_id=job.id, status="pending", trigger_type="manual", retry_count=0)
    db_session.add(task)
    db_session.commit()

    class DummyResponse:
        is_success = True
        status_code = 200
        text = "ok"

    class DummyClient:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def request(self, *args, **kwargs):
            return DummyResponse()

    monkeypatch.setattr("app.services.execution_service.httpx.Client", lambda timeout: DummyClient())
    service = WorkerService(db_session, queue, "worker-1")
    assert service.process_task_id(str(task.id))
    updated = db_session.get(Task, task.id)
    assert updated.status == "success"


def test_retry_flow(db_session):
    queue = MemoryQueueClient()
    job = _job(db_session, max_retries=1)
    task = Task(job_id=job.id, status="pending", trigger_type="manual", retry_count=0)
    db_session.add(task)
    db_session.commit()
    service = WorkerService(db_session, queue, "worker-1")

    class FailingExecutor:
        def run(self, *args, **kwargs):
            from app.services.execution_service import ExecutionResult

            return ExecutionResult(success=False, stdout="", stderr="boom")

    service.executor = FailingExecutor()
    service.process_task_id(str(task.id))
    tasks = db_session.query(Task).filter(Task.job_id == job.id).all()
    assert len(tasks) == 2


def test_orphan_recovery(db_session):
    queue = MemoryQueueClient()
    job = _job(db_session)
    task = Task(
        job_id=job.id,
        status="running",
        trigger_type="scheduled",
        retry_count=0,
        locked_by="worker-1",
        locked_until=datetime.now(UTC) - timedelta(seconds=1),
    )
    db_session.add(task)
    db_session.commit()
    service = SchedulerService(db_session, queue)
    recovered = service.recover_orphans()
    assert recovered == 1
    updated = db_session.get(Task, task.id)
    assert updated.status == "pending"

