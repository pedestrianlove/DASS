from __future__ import annotations

from app.db.session import SessionLocal
from app.models.job import Job
from app.services.job_service import JobService
from app.schemas.job import JobCreate


def main() -> None:
    with SessionLocal() as db:
        existing_names = {job.name for job in db.query(Job).all()}
        service = JobService(db)
        if "dass-http-example" not in existing_names:
            service.create_job(
                JobCreate(
                    name="dass-http-example",
                    cron_expression="*/5 * * * *",
                    action_type="http",
                    action_config={"method": "GET", "url": "https://example.com", "headers": {}, "timeout_seconds": 10},
                    enabled=True,
                    concurrency_policy="allow",
                    max_retries=1,
                )
            )
        if "dass-shell-example" not in existing_names:
            service.create_job(
                JobCreate(
                    name="dass-shell-example",
                    cron_expression="*/10 * * * *",
                    action_type="shell",
                    action_config={"command": "echo hello from dass", "timeout_seconds": 5},
                    enabled=False,
                    concurrency_policy="forbid",
                    max_retries=0,
                )
            )


if __name__ == "__main__":
    main()
