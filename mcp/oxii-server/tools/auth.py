"""Authentication helper tool for OXII MCP server."""
from __future__ import annotations

import os
from typing import Annotated, Optional

from dotenv import load_dotenv
from pydantic import Field

from .common import _request


load_dotenv()


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(
            f"Missing environment variable {var_name}. Please set it before using get_oxii_token."
        )
    return value


def get_oxii_token(
    phone: Annotated[Optional[str], Field(description="Phone number for the OXII account", default=None)] = None,
    password: Annotated[Optional[str], Field(description="Password for the OXII account", default=None)] = None,
    country: Annotated[Optional[str], Field(description="Country code (default: VI)", default=None)] = None,
) -> str:
    """Return an authentication token from the OXII API."""

    phone = phone or _require_env("USER_PHONE")
    password = password or _require_env("USER_PASSWORD")
    country = country or os.getenv("USER_COUNTRY", "VI")

    try:
        response = _request(
            "POST",
            "/api/app/user/signin",
            json={"phone": phone, "password": password, "country": country},
        ).json()

        if response.get("code") == 200:
            return response.get("data", {}).get("token", "")
        message = response.get("message") or "Authentication failed"
        return f"Authentication failed: {message}"

    except Exception as exc:  # pragma: no cover - surfaced to agent
        return f"Authentication error: {exc}"