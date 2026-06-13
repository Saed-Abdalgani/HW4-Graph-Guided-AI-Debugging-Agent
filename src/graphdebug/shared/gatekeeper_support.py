"""Redaction, factory helpers, and message preview for the gatekeeper."""

from __future__ import annotations

import re
from collections.abc import Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from graphdebug.shared.config import AppConfig

_SK_RE = re.compile(r"sk-[A-Za-z0-9]{8,}")
_BEARER_RE = re.compile(r"(Bearer\s+)([A-Za-z0-9\-._~+/]+=*)", re.I)


def redact_secrets(text: str) -> str:
    """Strip API-key shaped substrings for logs and ledgers (G.10)."""
    out = _SK_RE.sub("sk-***REDACTED***", text)
    return _BEARER_RE.sub(r"\1***REDACTED***", out)


class TransientLLMError(RuntimeError):
    """Retryable provider / transport failure."""


def build_chat_model(cfg: AppConfig) -> ChatOpenAI:
    if not cfg.openai_api_key:
        raise RuntimeError("OpenAI API key required for live Gatekeeper.")
    return ChatOpenAI(
        api_key=cfg.openai_api_key,
        model=str(cfg.llm["model"]),
        temperature=float(cfg.llm.get("temperature", 0.0)),
        max_tokens=int(cfg.llm.get("max_output_tokens", 1024)),
    )


def gatekeeper_user_content(messages: Sequence[BaseMessage]) -> str:
    parts: list[str] = []
    for m in messages:
        if isinstance(m, SystemMessage):
            parts.append("system: " + redact_secrets(str(m.content)))
        elif isinstance(m, HumanMessage):
            parts.append("human: " + redact_secrets(str(m.content)))
        elif isinstance(m, AIMessage):
            parts.append("ai: " + redact_secrets(str(m.content)))
    return "\n".join(parts)


def is_transient_llm_error(exc: BaseException) -> bool:
    name = type(exc).__name__
    if "RateLimit" in name or "APIConnection" in name or "Timeout" in name:
        return True
    return isinstance(exc, TransientLLMError)


def usage_from_ai_message(msg: AIMessage) -> dict[str, int]:
    meta = getattr(msg, "response_metadata", None) or {}
    tok = meta.get("token_usage") or meta.get("usage") or {}
    pt = int(tok.get("prompt_tokens", 0) or 0)
    ct = int(tok.get("completion_tokens", 0) or 0)
    if pt + ct == 0 and isinstance(msg.content, str):
        ct = max(1, len(msg.content) // 4)
        pt = max(1, 1)
    total = int(tok.get("total_tokens", pt + ct) or (pt + ct))
    return {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": max(1, total)}


__all__ = [
    "TransientLLMError",
    "build_chat_model",
    "gatekeeper_user_content",
    "is_transient_llm_error",
    "redact_secrets",
    "usage_from_ai_message",
]
