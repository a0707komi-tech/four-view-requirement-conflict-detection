import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)


ROLE_CONFIG = {
    "semantic": {
        "api_key": "SEMANTIC_API_KEY",
        "base_url": "SEMANTIC_BASE_URL",
        "model": "SEMANTIC_MODEL",
        "batch_api_key": "SEMANTIC_BATCH_API_KEY",
        "batch_base_url": "SEMANTIC_BATCH_BASE_URL",
        "batch_model": "SEMANTIC_BATCH_MODEL",
        "default_base": "https://api.deepseek.com/v1",
        "default_model": "deepseek-v4-flash",
        "supports_batch_submission": False,
    },
    "logic": {
        "api_key": "DEEPSEEK_API_KEY",
        "base_url": "DEEPSEEK_BASE_URL",
        "model": "DEEPSEEK_MODEL",
        "batch_api_key": "DEEPSEEK_BATCH_API_KEY",
        "batch_base_url": "DEEPSEEK_BATCH_BASE_URL",
        "batch_model": "DEEPSEEK_BATCH_MODEL",
        "default_base": "https://api.deepseek.com/v1",
        "default_model": "deepseek-v4-pro",
        "supports_batch_submission": False,
    },
    "feasibility": {
        "api_key": "KIMI_API_KEY",
        "base_url": "KIMI_BASE_URL",
        "model": "KIMI_MODEL",
        "batch_api_key": "KIMI_BATCH_API_KEY",
        "batch_base_url": "KIMI_BATCH_BASE_URL",
        "batch_model": "KIMI_BATCH_MODEL",
        "default_base": "https://api.moonshot.cn/v1",
        "default_model": "kimi-k2.6",
        "supports_batch_submission": True,
    },
    "goal": {
        "api_key": "QWEN_MAX_API_KEY",
        "base_url": "QWEN_MAX_BASE_URL",
        "model": "QWEN_MAX_MODEL",
        "batch_api_key": "QWEN_MAX_BATCH_API_KEY",
        "batch_base_url": "QWEN_MAX_BATCH_BASE_URL",
        "batch_model": "QWEN_MAX_BATCH_MODEL",
        "default_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen3.7-plus",
        "supports_batch_submission": True,
    },
    "da": {
        "api_key": "DEEPSEEK_API_KEY",
        "base_url": "DEEPSEEK_BASE_URL",
        "model": "DEEPSEEK_MODEL",
        "batch_api_key": "DEEPSEEK_BATCH_API_KEY",
        "batch_base_url": "DEEPSEEK_BATCH_BASE_URL",
        "batch_model": "DEEPSEEK_BATCH_MODEL",
        "default_base": "https://api.deepseek.com/v1",
        "default_model": "deepseek-v4-pro",
        "supports_batch_submission": False,
    },
    "arbiter": {
        "api_key": "GPT_API_KEY",
        "base_url": "GPT_BASE_URL",
        "model": "GPT_MODEL",
        "batch_api_key": "GPT_BATCH_API_KEY",
        "batch_base_url": "GPT_BATCH_BASE_URL",
        "batch_model": "GPT_BATCH_MODEL",
        "default_base": "",
        "default_model": "gpt-5.4",
        "supports_batch_submission": False,
    },
}

NO_SYSTEM_ROLE_MODELS = {"kimi-k2.6"}

ROLE_DEFAULTS = {
    "semantic": {"force_reasoning": False, "temperature": 0.0, "min_max_tokens": 1024},
    "logic": {"force_reasoning": True, "temperature": 0.0, "min_max_tokens": 1536},
    "feasibility": {"force_reasoning": True, "temperature": 0.6, "min_max_tokens": 1536},
    "goal": {"force_reasoning": False, "temperature": 0.0, "min_max_tokens": 1024},
    "da": {"force_reasoning": False, "temperature": 0.0, "min_max_tokens": 768},
    "arbiter": {"force_reasoning": False, "temperature": 0.0, "min_max_tokens": 1536},
}


@dataclass(frozen=True)
class ResolvedRoleConfig:
    api_key: str
    base_url: str
    model: str
    batch_api_key: str
    batch_base_url: str
    batch_model: str
    supports_batch_submission: bool


def build_role_settings(env: Mapping[str, str] | None = None) -> dict[str, ResolvedRoleConfig]:
    source = os.environ if env is None else env
    settings: dict[str, ResolvedRoleConfig] = {}

    for role, cfg in ROLE_CONFIG.items():
        api_key = source.get(cfg["api_key"], "")
        if not api_key:
            raise EnvironmentError(
                f"Missing environment variable: {cfg['api_key']} (role: {role})"
            )

        base_url = source.get(cfg["base_url"], cfg["default_base"])
        if not base_url:
            raise EnvironmentError(
                f"Missing environment variable: {cfg['base_url']} (role: {role})"
            )

        settings[role] = ResolvedRoleConfig(
            api_key=api_key,
            base_url=base_url,
            model=source.get(cfg["model"], cfg["default_model"]),
            batch_api_key=source.get(cfg["batch_api_key"], api_key),
            batch_base_url=source.get(cfg["batch_base_url"], base_url),
            batch_model=source.get(cfg["batch_model"], source.get(cfg["model"], cfg["default_model"])),
            supports_batch_submission=bool(cfg.get("supports_batch_submission", False)),
        )

    return settings


def resolve_role_settings(role: str) -> dict[str, str]:
    resolved = build_role_settings()[role]
    return {
        "api_key": resolved.api_key,
        "base_url": resolved.base_url,
        "model": resolved.model,
        "batch_api_key": resolved.batch_api_key,
        "batch_base_url": resolved.batch_base_url,
        "batch_model": resolved.batch_model,
        "supports_batch_submission": resolved.supports_batch_submission,
    }
