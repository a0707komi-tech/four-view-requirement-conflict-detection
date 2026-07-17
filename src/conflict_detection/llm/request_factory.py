from __future__ import annotations

import json
from dataclasses import dataclass

from conflict_detection.io.prompt_rendering import render_prompt_template
from conflict_detection.llm.model_config import ROLE_DEFAULTS
from conflict_detection.orchestration.session_types import DetectionPair, PromptBundle


@dataclass(frozen=True)
class ChatRequest:
    system_prompt: str | None
    user_prompt: str
    temperature: float
    max_tokens: int


def render_pair_prompt(bundle: PromptBundle, pair: DetectionPair) -> ChatRequest:
    user_prompt = render_prompt_template(
        bundle.user_prompt,
        {
            "r1_text": pair.r1_text,
            "r2_text": pair.r2_text,
            "pair_id": pair.pair_id,
            "r1_id": pair.r1_id,
            "r2_id": pair.r2_id,
            "requirement_a": pair.r1_text,
            "requirement_b": pair.r2_text,
        },
    )
    return ChatRequest(
        system_prompt=bundle.system_prompt if bundle.metadata.supports_system_role else None,
        user_prompt=user_prompt,
        temperature=float(bundle.metadata.temperature_policy.get("value", 0.0)),
        max_tokens=int(bundle.metadata.max_tokens_policy.get("value", 1024)),
    )


def build_chat_body(
    *,
    role: str,
    model: str,
    system_prompt: str | None,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    supports_system_role: bool,
    batch_mode: bool = False,
) -> dict[str, object]:
    messages = [{"role": "user", "content": user_prompt}]
    if system_prompt and supports_system_role:
        messages.insert(0, {"role": "system", "content": system_prompt})

    body: dict[str, object] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if not _omit_temperature(role=role, model=model, batch_mode=batch_mode):
        body["temperature"] = temperature
    thinking = _resolve_thinking_config(role=role, model=model)
    if thinking is not None:
        body["thinking"] = thinking
    if _is_qwen_hybrid_model(model):
        body["enable_thinking"] = _resolve_qwen_thinking(role)
    return body


def extract_batch_chat_text(result_payload: dict[str, object]) -> str:
    response = result_payload.get("response", {})
    if not isinstance(response, dict):
        return ""
    body = response.get("body", {})
    if not isinstance(body, dict):
        return ""
    choices = body.get("choices", [])
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message", {})
    if not isinstance(message, dict):
        return ""
    content = message.get("content", "")
    if isinstance(content, str):
        return content.strip()
    return json.dumps(content, ensure_ascii=False)


def _omit_temperature(*, role: str, model: str, batch_mode: bool) -> bool:
    return model.startswith("kimi-k2.6")


def _is_qwen_hybrid_model(model: str) -> bool:
    return model.startswith(("qwen3.5-", "qwen3.6-", "qwen3.7-"))


def _resolve_qwen_thinking(role: str) -> bool:
    defaults = ROLE_DEFAULTS.get(role, {})
    return bool(defaults.get("force_reasoning", False))


def _resolve_thinking_config(*, role: str, model: str) -> dict[str, str] | None:
    if model.startswith("kimi-k2.6") and role == "feasibility":
        return {"type": "disabled"}
    if model.startswith("deepseek-v4-") and role == "da":
        return {"type": "disabled"}
    return None
