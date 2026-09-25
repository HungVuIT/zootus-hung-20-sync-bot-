"""Runtime configuration loaded from environment variables (see .env.sample)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """All tunables for one run. Secrets never have defaults."""

    gemini_api_key: str
    zendesk_base_url: str = "https://support.optisigns.com"
    zendesk_locale: str = "en-us"
    store_display_name: str = "optibot-kb"
    gemini_model: str = "gemini-3.5-flash"
    chunk_max_tokens: int = 400
    chunk_overlap_tokens: int = 60
    upload_workers: int = 4
    articles_dir: Path = Path("articles")
    data_dir: Path = Path("data")

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from the process environment (after loading .env if present)."""
        load_dotenv()
        key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not key or key == "your_key_here":
            raise RuntimeError("GEMINI_API_KEY is missing. Copy .env.sample to .env and fill it in.")
        return cls(
            gemini_api_key=key,
            zendesk_base_url=os.environ.get("ZENDESK_BASE_URL", cls.zendesk_base_url).rstrip("/"),
            zendesk_locale=os.environ.get("ZENDESK_LOCALE", cls.zendesk_locale),
            store_display_name=os.environ.get("FILE_SEARCH_STORE_NAME", cls.store_display_name),
            gemini_model=os.environ.get("GEMINI_MODEL", cls.gemini_model),
            chunk_max_tokens=int(os.environ.get("CHUNK_MAX_TOKENS", cls.chunk_max_tokens)),
            chunk_overlap_tokens=int(os.environ.get("CHUNK_OVERLAP_TOKENS", cls.chunk_overlap_tokens)),
            upload_workers=int(os.environ.get("UPLOAD_WORKERS", cls.upload_workers)),
            articles_dir=Path(os.environ.get("ARTICLES_DIR", str(cls.articles_dir))),
            data_dir=Path(os.environ.get("DATA_DIR", str(cls.data_dir))),
        )
