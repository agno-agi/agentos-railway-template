"""Interface builders for AgentOS."""

from __future__ import annotations

from os import getenv
from typing import Any

from agno.os.interfaces.whatsapp import Whatsapp

_TRUTHY_VALUES = {"1", "true", "yes", "on"}
_PLACEHOLDER_PREFIXES = ("your ",)
_WHATSAPP_REQUIRED_ENV_VARS = (
    "WHATSAPP_ACCESS_TOKEN",
    "WHATSAPP_PHONE_NUMBER_ID",
    "WHATSAPP_VERIFY_TOKEN",
)


def _is_enabled(env_var: str) -> bool:
    value = getenv(env_var, "").strip().lower()
    return value in _TRUTHY_VALUES


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    return not normalized or normalized.startswith(_PLACEHOLDER_PREFIXES)


def _missing_whatsapp_settings() -> list[str]:
    missing: list[str] = []
    for env_var in _WHATSAPP_REQUIRED_ENV_VARS:
        value = getenv(env_var, "")
        if _is_placeholder(value):
            missing.append(env_var)
    if not _is_enabled("WHATSAPP_SKIP_SIGNATURE_VALIDATION") and _is_placeholder(getenv("WHATSAPP_APP_SECRET", "")):
        missing.append("WHATSAPP_APP_SECRET")
    return missing


def build_interfaces(agent: Any) -> list[Whatsapp]:
    """Build external interfaces without enabling networked integrations by accident."""

    if not _is_enabled("WHATSAPP_ENABLED"):
        return []

    missing = _missing_whatsapp_settings()
    if missing:
        missing_vars = ", ".join(missing)
        raise RuntimeError(
            "WHATSAPP_ENABLED=true but these WhatsApp settings are missing or still placeholders: "
            f"{missing_vars}"
        )

    return [
        Whatsapp(
            agent=agent,
            access_token=getenv("WHATSAPP_ACCESS_TOKEN"),
            phone_number_id=getenv("WHATSAPP_PHONE_NUMBER_ID"),
            verify_token=getenv("WHATSAPP_VERIFY_TOKEN"),
        )
    ]
