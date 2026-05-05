from __future__ import annotations

import json
import queue
import uuid

from app.queue.base import QueueMessage


class MemoryQueueClient:
    """In-memory Queue 實作，用於測試環境（不需要 Docker / LocalStack）。"""

    def __init__(self) -> None:
        self._queue: queue.Queue[tuple[str, str]] = queue.Queue()

    def send_task(self, task_id: str) -> None:
        """將 task_id 包成 JSON message 放入 queue。

        # TODO:
        #   message body = json.dumps({"task_id": task_id})
        #   receipt_handle = 隨機 UUID
        #   放入 self._queue
        """
        raise NotImplementedError

    def receive_tasks(self, max_messages: int = 1, wait_time_seconds: int = 10) -> list[QueueMessage]:
        """從 queue 取出最多 max_messages 筆訊息。

        # TODO:
        #   1. 迴圈最多 max_messages 次
        #   2. 用 self._queue.get(timeout=wait_time_seconds) 取訊息
        #      - queue.Empty → break
        #   3. 包成 QueueMessage(body=body, receipt_handle=receipt)
        #   4. 回傳 list
        """
        raise NotImplementedError

    def delete_message(self, receipt_handle: str) -> None:
        """確認消費（Memory 版不需實際做事，直接 return None）。

        # TODO: return None
        """
        raise NotImplementedError
