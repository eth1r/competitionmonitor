from __future__ import annotations

import logging
import sys

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment / .env."""

    OPENAI_API_KEY: str = Field(..., min_length=1)
    OPENAI_PROXY: str | None = None
    OPENAI_MODEL: str = "gpt-4o"
    history_file: str = "history.json"
    max_history_items: int = 50

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Setup logger
logger = logging.getLogger("competitor_monitor")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s")
    )
    logger.addHandler(handler)