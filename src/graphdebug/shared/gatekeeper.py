"""Central LLM chokepoint: rate limits, retries, ledger (FR-S2, T5.2)."""

from __future__ import annotations

import random
import threading
import time
from collections.abc import Callable, Sequence
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI

from graphdebug.services.agents import budget as budget_mod
from graphdebug.services.ledger.schema import LedgerRecord
from graphdebug.services.ledger.writer import LedgerWriter
from graphdebug.shared._rate_limit import RefillBucket
from graphdebug.shared.config import AppConfig
from graphdebug.shared.gatekeeper_support import (
    TransientLLMError,
    build_chat_model,
    gatekeeper_user_content,
    is_transient_llm_error,
    redact_secrets,
    usage_from_ai_message,
)


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class Gatekeeper:
    """All worker LLM calls must go through this class (G.4)."""

    def __init__(
        self,
        *,
        app_config: AppConfig,
        budget: dict[str, Any],
        ledger: LedgerWriter,
        chat_model: ChatOpenAI | None = None,
        invoker: Callable[[str, Sequence[BaseMessage]], AIMessage] | None = None,
    ) -> None:
        gk = app_config.gatekeeper
        rpm = float(gk["requests_per_minute"])
        tpm = float(gk["tokens_per_minute"])
        self._req_bucket = RefillBucket(capacity=max(1.0, rpm), refill_per_second=rpm / 60.0)
        self._tok_bucket = RefillBucket(capacity=max(1.0, tpm), refill_per_second=tpm / 60.0)
        self._max_retries = int(gk["max_retries"])
        self._backoff_base = float(gk["backoff_base_seconds"])
        self._backoff_max = float(gk["max_backoff_seconds"])
        self._queue_sem = threading.BoundedSemaphore(int(gk["queue_size"]))
        self._cfg = app_config
        self._budget = budget
        self._ledger = ledger
        self._invoker = invoker
        self._chat = chat_model

    def complete_chat(
        self,
        *,
        role: str,
        messages: Sequence[BaseMessage],
        max_out: int | None = None,
    ) -> AIMessage:
        joined = "\n".join(
            str(getattr(m, "content", m)) for m in messages if hasattr(m, "content")
        )
        est = _estimate_tokens(joined) + int(max_out or self._cfg.llm.get("max_output_tokens", 512))
        budget_mod.assert_can_tool_call(self._budget, 1)
        budget_mod.assert_can_use_tokens(self._budget, est)

        if not self._queue_sem.acquire(blocking=True, timeout=120):
            raise RuntimeError("gatekeeper queue timeout (backpressure)")

        try:
            self._req_bucket.consume(1.0)
            self._tok_bucket.consume(float(est))
            return self._invoke_with_retries(role, messages, max_out)
        finally:
            self._queue_sem.release()

    def _invoke_with_retries(
        self,
        role: str,
        messages: Sequence[BaseMessage],
        max_out: int | None,
    ) -> AIMessage:
        attempt = 0
        while True:
            t0 = time.perf_counter()
            try:
                msg = self._raw_invoke(messages, max_out)
            except Exception as exc:  # noqa: BLE001 — boundary for retries
                attempt += 1
                if attempt > self._max_retries or not is_transient_llm_error(exc):
                    raise
                delay = min(
                    self._backoff_max,
                    self._backoff_base * (2 ** (attempt - 1)) + random.random() * 0.1,
                )
                time.sleep(delay)
                continue

            dt = (time.perf_counter() - t0) * 1000.0
            usage = usage_from_ai_message(msg)
            budget_mod.record_tool_call(self._budget, 1)
            budget_mod.record_tokens(self._budget, usage["total_tokens"])
            self._ledger.append(
                LedgerRecord(
                    role=role,
                    event="llm_completion",
                    prompt_tokens=usage["prompt_tokens"],
                    completion_tokens=usage["completion_tokens"],
                    total_tokens=usage["total_tokens"],
                    latency_ms=dt,
                    tool_calls=1,
                    meta={"model": str(self._cfg.llm.get("model", ""))},
                )
            )
            return msg

    def _raw_invoke(self, messages: Sequence[BaseMessage], max_out: int | None) -> AIMessage:
        if self._invoker is not None:
            return self._invoker("gatekeeper", messages)
        if self._chat is None:
            raise RuntimeError("Gatekeeper has no chat model or invoker.")
        return self._chat.invoke(list(messages))


__all__ = [
    "Gatekeeper",
    "TransientLLMError",
    "build_chat_model",
    "gatekeeper_user_content",
    "redact_secrets",
]
