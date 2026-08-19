from __future__ import annotations

import os, re
from pathlib import Path
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl, model_validator


class Credentials(BaseModel):
    username: str
    app_password: str


class Site(BaseModel):
    id: str
    base_url: str
    seo_plugin: str = "none"
    default_category: str = "Uncategorized"
    default_status: str = "draft"
    template: str = "default"
    timezone: str = "UTC"
    credentials: Credentials | None = None

    @model_validator(mode="after")
    def valid_seo(self):
        if self.seo_plugin not in {"yoast", "rankmath", "none"}:
            raise ValueError("seo_plugin must be yoast, rankmath, or none")
        return self


class OpenCodeSettings(BaseModel):
    model: str = "anthropic/claude-sonnet-4-5"
    use_server: bool = True
    server_url: str = "http://localhost:4096"
    timeout_seconds: int = 300


class RunSettings(BaseModel):
    max_retries: int = 3
    retry_backoff_seconds: int = 5
    requests_per_minute_per_site: int = 20
    concurrency: int = 4


class Settings(BaseModel):
    opencode: OpenCodeSettings = Field(default_factory=OpenCodeSettings)
    run: RunSettings = Field(default_factory=RunSettings)
    logging: dict = Field(default_factory=dict)


class AppConfig(BaseModel):
    sites: list[Site]
    settings: Settings

    def site(self, site_id: str) -> Site:
        for site in self.sites:
            if site.id == site_id: return site
        raise ValueError(f"Unknown site_id: {site_id}")

    def missing_credentials(self, site_id: str | None = None) -> list[str]:
        return [s.id for s in self.sites if (not site_id or s.id == site_id) and not s.credentials]


def _env_key(site_id: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", site_id.upper()).strip("_")


def load_config(config_dir: Path = Path("config"), require_credentials: bool = False) -> AppConfig:
    load_dotenv()
    sites_data = yaml.safe_load((config_dir / "sites.yaml").read_text()) or {"sites": []}
    local_path = config_dir / "sites.local.yaml"
    local = yaml.safe_load(local_path.read_text()) if local_path.exists() else {}
    credentials = (local or {}).get("credentials", {})
    for site in sites_data["sites"]:
        sid = site["id"]; key = _env_key(sid)
        merged = credentials.get(sid, {}).copy()
        if os.getenv(f"WP_{key}_USERNAME"): merged["username"] = os.environ[f"WP_{key}_USERNAME"]
        if os.getenv(f"WP_{key}_APP_PASSWORD"): merged["app_password"] = os.environ[f"WP_{key}_APP_PASSWORD"]
        if merged: site["credentials"] = merged
    settings_path = config_dir / "settings.yaml"
    settings = yaml.safe_load(settings_path.read_text()) if settings_path.exists() else {}
    config = AppConfig(sites=sites_data["sites"], settings=settings or {})
    missing = config.missing_credentials()
    if require_credentials and missing:
        raise ValueError("Missing WordPress credentials for: " + ", ".join(missing))
    return config
