from __future__ import annotations

import json

import boto3

from app.core.config import Settings
from app.queue.base import QueueMessage


class SQSQueueClient:
    """AWS SQS Queue 實作（本地用 LocalStack）。"""

    def __init__(self, settings: Settings):
        """初始化 SQS client 並取得 queue URL。

        # TODO:
        #   1. 儲存 settings
        #   2. 建立 boto3.client('sqs', region_name=..., endpoint_url=...,
        #      aws_access_key_id=..., aws_secret_access_key=..., aws_session_token=...)
        #   3. 呼叫 self._resolve_queue_url() 取得 queue_url
        """
        raise NotImplementedError

    def _resolve_queue_url(self) -> str:
        """取得 SQS queue URL，若 queue 不存在則自動建立。

        # TODO:
        #   1. 嘗試 self.client.get_queue_url(QueueName=self.settings.queue_name)
        #   2. 若 QueueDoesNotExist → self.client.create_queue(...)
        #   3. 回傳 queue URL
        """
        raise NotImplementedError

    def send_task(self, task_id: str) -> None:
        """發送 task_id 到 SQS queue。

        # TODO:
        #   MessageBody = json.dumps({"task_id": task_id})
        #   self.client.send_message(QueueUrl=..., MessageBody=...)
        """
        raise NotImplementedError

    def receive_tasks(self, max_messages: int = 1, wait_time_seconds: int = 10) -> list[QueueMessage]:
        """從 SQS 接收訊息（支援 long polling）。

        # TODO:
        #   1. self.client.receive_message(
        #        QueueUrl=..., MaxNumberOfMessages=max_messages,
        #        WaitTimeSeconds=wait_time_seconds,
        #        VisibilityTimeout=self.settings.worker_visibility_timeout_seconds)
        #   2. 將 response['Messages'] 轉成 QueueMessage list
        #      - body = message['Body'], receipt_handle = message['ReceiptHandle']
        """
        raise NotImplementedError

    def delete_message(self, receipt_handle: str) -> None:
        """確認消費，從 SQS 刪除已處理的訊息。

        # TODO:
        #   self.client.delete_message(QueueUrl=..., ReceiptHandle=receipt_handle)
        """
        raise NotImplementedError
