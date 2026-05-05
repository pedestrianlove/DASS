from __future__ import annotations

import json
import logging
import sys
import time

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.queue.factory import get_queue_client
from app.services.scheduler_service import SchedulerService
from app.services.worker_service import WorkerService

logger = logging.getLogger(__name__)


def run_scheduler() -> None:
    """啟動 Scheduler 主迴圈。

    # TODO:
    #   1. 取得 settings，設定 logging
    #   2. 取得 queue_client
    #   3. 無限迴圈：
    #      a. 開一個 DB session（with SessionLocal() as db）
    #      b. 建立 SchedulerService(db, queue, settings.worker_visibility_timeout_seconds)
    #      c. 執行 recover_orphans()
    #      d. 執行 dispatch_due_jobs()
    #      e. sleep(settings.scheduler_interval_seconds)
    """
    raise NotImplementedError


def run_worker() -> None:
    """啟動 Worker 主迴圈。

    # TODO:
    #   1. 取得 settings，設定 logging
    #   2. 取得 queue_client
    #   3. 無限迴圈：
    #      a. queue.receive_tasks(max_messages=1, wait_time_seconds=10)
    #      b. 若無訊息 → continue
    #      c. 對每個 message：
    #         - 解析 payload = json.loads(message.body)
    #         - 取出 task_id
    #         - 開 DB session，建立 WorkerService
    #         - 呼叫 service.process_task_id(task_id)
    #         - 成功後 queue.delete_message(message.receipt_handle)
    #         - 捕獲 Exception 並 log
    """
    raise NotImplementedError


def main() -> None:
    """CLI 入口：根據 sys.argv[1] 分派到 scheduler 或 worker。

    # TODO:
    #   - 'scheduler' → run_scheduler()
    #   - 'worker'    → run_worker()
    #   - 其他        → raise SystemExit
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
