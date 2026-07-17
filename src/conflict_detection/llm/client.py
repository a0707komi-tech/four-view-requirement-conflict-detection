import time

from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from conflict_detection.llm.providers import ProviderClient
from conflict_detection.llm.request_factory import build_chat_body as build_provider_chat_body
from conflict_detection.llm.model_config import (
    NO_SYSTEM_ROLE_MODELS,
    ROLE_CONFIG,
    ROLE_DEFAULTS,
    build_role_settings,
    resolve_role_settings,
)

OPENAI_CHAT_CREATE_KEYS = {
    "model",
    "messages",
    "max_tokens",
    "temperature",
    "top_p",
    "n",
    "stream",
    "stop",
    "presence_penalty",
    "frequency_penalty",
    "logit_bias",
    "user",
    "response_format",
    "seed",
    "tools",
    "tool_choice",
    "parallel_tool_calls",
    "stream_options",
    "timeout",
    "extra_headers",
    "extra_query",
    "extra_body",
}


class LLMClient:
    """Role-based model router."""

    ROLE_CONFIG = ROLE_CONFIG

    def __init__(self):
        self._clients: dict[str, OpenAI] = {}
        self._models: dict[str, str] = {}
        self._batch_clients: dict[str, OpenAI] = {}
        self._batch_models: dict[str, str] = {}
        self._batch_support: dict[str, bool] = {}
        self._provider_clients: dict[str, ProviderClient] = {}
        resolved_settings = build_role_settings()

        for role, settings in resolved_settings.items():
            client = OpenAI(
                api_key=settings.api_key,
                base_url=settings.base_url,
            )
            self._clients[role] = client
            self._models[role] = settings.model
            batch_client = OpenAI(
                api_key=settings.batch_api_key,
                base_url=settings.batch_base_url,
            )
            self._batch_clients[role] = batch_client
            self._batch_models[role] = settings.batch_model
            self._batch_support[role] = settings.supports_batch_submission
            self._provider_clients[role] = ProviderClient(name=role, client=batch_client, model=settings.batch_model)

    @property
    def semantic(self) -> "RoleClient":
        return RoleClient(self, "semantic")

    @property
    def logic(self) -> "RoleClient":
        return RoleClient(self, "logic")

    @property
    def feasibility(self) -> "RoleClient":
        return RoleClient(self, "feasibility")

    @property
    def goal(self) -> "RoleClient":
        return RoleClient(self, "goal")

    @property
    def da(self) -> "RoleClient":
        return RoleClient(self, "da")

    @property
    def arbiter(self) -> "RoleClient":
        return RoleClient(self, "arbiter")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIConnectionError, APITimeoutError, RateLimitError)),
        reraise=True,
    )
    def _call_api(self, client, request_kwargs: dict[str, object]) -> str:
        for attempt in range(3):
            effective_kwargs = dict(request_kwargs)
            provider_specific = {
                key: effective_kwargs.pop(key)
                for key in list(effective_kwargs.keys())
                if key not in OPENAI_CHAT_CREATE_KEYS
            }
            if provider_specific:
                extra_body = dict(effective_kwargs.get("extra_body", {}))
                extra_body.update(provider_specific)
                effective_kwargs["extra_body"] = extra_body
            response = client.chat.completions.create(**effective_kwargs)
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()
            if attempt < 2:
                time.sleep(2**attempt)
        return ""

    def chat(
        self,
        role: str,
        prompt: str,
        user_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        *,
        system_prompt: str | None = None,
    ) -> str:
        body = self.build_chat_body(
            role,
            prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )
        client = self._clients[role]
        return self._call_api(client, dict(body))

    def get_model_name(self, role: str) -> str:
        return self._models[role]

    def get_batch_model_name(self, role: str) -> str:
        return self._batch_models[role]

    def get_provider_client(self, role: str) -> ProviderClient:
        if not self.supports_batch_submission(role):
            raise NotImplementedError(f"Batch submission is not supported for role: {role}")
        return self._provider_clients[role]

    def supports_batch_submission(self, role: str) -> bool:
        return self._batch_support.get(role, False)

    def build_chat_body(
        self,
        role: str,
        prompt: str,
        user_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        *,
        system_prompt: str | None = None,
    ) -> dict[str, object]:
        model = self._models[role]
        role_defaults = ROLE_DEFAULTS[role]

        if system_prompt is None and user_prompt is not None:
            system_prompt = prompt
            actual_user_prompt = user_prompt
        else:
            actual_user_prompt = prompt

        requested_temperature = role_defaults["temperature"] if temperature is None else temperature
        if role_defaults["force_reasoning"]:
            actual_temp = role_defaults["temperature"]
        else:
            actual_temp = requested_temperature

        requested_max_tokens = role_defaults["min_max_tokens"] if max_tokens is None else max_tokens
        actual_max_tokens = max(requested_max_tokens, role_defaults["min_max_tokens"])

        return build_provider_chat_body(
            role=role,
            model=model,
            system_prompt=system_prompt if model not in NO_SYSTEM_ROLE_MODELS else None,
            user_prompt=actual_user_prompt,
            temperature=actual_temp,
            max_tokens=actual_max_tokens,
            supports_system_role=model not in NO_SYSTEM_ROLE_MODELS,
            batch_mode=False,
        )


class RoleClient:
    """Convenience wrapper around one logical role."""

    def __init__(self, llm: LLMClient, role: str):
        self._llm = llm
        self._role = role

    def chat(
        self,
        prompt: str,
        user_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        *,
        system_prompt: str | None = None,
    ) -> str:
        return self._llm.chat(
            self._role,
            prompt,
            user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )

    @property
    def model_name(self) -> str:
        return self._llm.get_model_name(self._role)
