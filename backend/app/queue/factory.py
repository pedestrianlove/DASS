from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.queue.memory import MemoryQueueClient
from app.queue.sqs import SQSQueueClient


@lru_cache
def get_queue_client():
    """根據 settings.queue_backend 回傳對應的 QueueClient 實例。

    # TODO:
    #   1. 取得 settings = get_settings()
    #   2. 若 settings.queue_backend == 'memory' → 回傳 MemoryQueueClient()
    #   3. 否則 → 回傳 SQSQueueClient(settings)
    """
    raise NotImplementedError
