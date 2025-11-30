"""Global configuration utilities for centralized secrets handling."""

import os
from pathlib import Path
from typing import Optional


def _load_env_file(env_path: Optional[Path] = None) -> None:
    """Load environment variables from a .env file, overriding existing values.

    This version ensures .env always takes priority, which is often preferred
    during development or when running the application manually on servers.
    """

    if env_path is None:
        # Load .env located at project root (parent of /config/)
        env_path = Path(__file__).resolve().parent.parent / ".env"

    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        stripped = line.strip()

        # Skip blank lines & comments
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()

        # OVERRIDE any existing environment variable
        os.environ[key] = value


def _require_env(name: str) -> str:
    """Fetch a required environment variable or raise a clear error."""

    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set. Define it in a .env file at the repository root "
            f"or in the execution environment."
        )
    return value


def get_openai_api_key() -> str:
    """Return the OpenAI API key from .env or environment variables."""

    _load_env_file()
    return _require_env("OPENAI_API_KEY")


__all__ = ["get_openai_api_key"]
