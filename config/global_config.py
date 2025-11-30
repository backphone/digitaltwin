"""Global configuration utilities for centralized secrets handling."""

import os
from pathlib import Path
from typing import Optional


def _load_env_file(env_path: Optional[Path] = None) -> None:
    """Load environment variables from a .env file if present.

    Values already present in ``os.environ`` are not overridden. This keeps the
    execution environment in control while still allowing local development to
    supply secrets via a ``.env`` file at the repository root.
    """

    path = env_path
    if path is None:
        path = Path(__file__).resolve().parent.parent / ".env"

    if not path.exists():
        return

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        os.environ.setdefault(key, value)


def _require_env(name: str) -> str:
    """Fetch a required environment variable or raise a clear error."""

    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"{name} not set. Define it in the environment or in a .env file at the repository root."
        )
    return value


def get_openai_api_key() -> str:
    """Return the OpenAI API key from environment or .env."""

    _load_env_file()
    return _require_env("OPENAI_API_KEY")


__all__ = ["get_openai_api_key"]
