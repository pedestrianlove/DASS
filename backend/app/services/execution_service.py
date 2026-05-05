from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

import httpx
from fastapi import HTTPException

from app.schemas.job import HttpActionConfig, ShellActionConfig


@dataclass
class ExecutionResult:
    success: bool
    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | None = None


class ExecutionService:
    def run(self, action_type: str, action_config: dict) -> ExecutionResult:
        """根據 action_type 分派到對應的執行方法。

        # TODO:
        #   - action_type == 'http'  → self._run_http(HttpActionConfig.model_validate(action_config))
        #   - action_type == 'shell' → self._run_shell(ShellActionConfig.model_validate(action_config))
        #   - 其他 → raise HTTPException(status_code=400, detail="Unsupported action type")
        """
        raise NotImplementedError

    def _run_http(self, config: HttpActionConfig) -> ExecutionResult:
        """執行 HTTP request 並回傳結果。

        # TODO:
        #   1. 建立 httpx.Client (timeout=config.timeout_seconds)
        #   2. 發送 request：method=config.method, url=config.url, headers=config.headers
        #      - body 是 dict → 用 json 參數
        #      - body 是 str → 用 content 參數
        #   3. 回傳 ExecutionResult：
        #      - success = response.is_success
        #      - stdout = f"status={response.status_code}\n{response.text}"
        #      - stderr = "" if success else f"HTTP {response.status_code}"
        """
        raise NotImplementedError

    def _run_shell(self, config: ShellActionConfig) -> ExecutionResult:
        """執行 shell command 並回傳結果。

        # TODO:
        #   1. 使用 subprocess.run(config.command, shell=True, capture_output=True,
        #      text=True, timeout=config.timeout_seconds, check=False)
        #   2. 回傳 ExecutionResult：
        #      - success = returncode == 0
        #      - stdout, stderr, exit_code
        """
        raise NotImplementedError
