"""Authentication helper tool for OXII MCP server."""
from __future__ import annotations

import os
from typing import Annotated, Optional

from dotenv import load_dotenv
from pydantic import Field
from .mockup_data import MOCK_TOKEN
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
    country: Annotated[Optional[str], Field(description="Country code (default: VI)", default="VI")] = None,
) -> str:
    """[MOCK] Return an authentication token from the OXII API."""
    
    # Simulate authentication
    if phone and password:
        print(f"[MOCK] Authenticating with phone: {phone}")
        return MOCK_TOKEN
    
    # Default credentials
    return MOCK_TOKEN