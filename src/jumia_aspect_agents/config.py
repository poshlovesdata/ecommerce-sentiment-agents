"""Application settings loaded from environment variables."""

from pathlib import Path

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for scraping, NLP processing, and dashboarding."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")
    llm_temperature: float = Field(default=0.0, validation_alias="LLM_TEMPERATURE")

    jumia_base_url: AnyHttpUrl = Field(
        default="https://www.jumia.com.ng",
        validation_alias="JUMIA_BASE_URL",
    )
    jumia_category_url: AnyHttpUrl = Field(
        default="https://www.jumia.com.ng/mobile-accessories/",
        validation_alias="JUMIA_CATEGORY_URL",
    )
    scraper_min_delay_seconds: int = Field(
        default=2,
        validation_alias="SCRAPER_MIN_DELAY_SECONDS",
    )
    scraper_max_delay_seconds: int = Field(
        default=6,
        validation_alias="SCRAPER_MAX_DELAY_SECONDS",
    )
    scraper_timeout_seconds: int = Field(
        default=20,
        validation_alias="SCRAPER_TIMEOUT_SECONDS",
    )
    scraper_max_retries: int = Field(default=3, validation_alias="SCRAPER_MAX_RETRIES")

    raw_data_dir: Path = Field(default=Path("data/raw"), validation_alias="RAW_DATA_DIR")
    processed_data_dir: Path = Field(
        default=Path("data/processed"),
        validation_alias="PROCESSED_DATA_DIR",
    )
    figures_dir: Path = Field(default=Path("reports/figures"), validation_alias="FIGURES_DIR")

    streamlit_server_port: int = Field(
        default=8501,
        validation_alias="STREAMLIT_SERVER_PORT",
    )
    streamlit_server_address: str = Field(
        default="0.0.0.0",
        validation_alias="STREAMLIT_SERVER_ADDRESS",
    )
    dashboard_host: str = Field(
        default="jumia-dashboard.poshlovesdata.dev",
        validation_alias="DASHBOARD_HOST",
    )
    traefik_network: str = Field(default="traefik", validation_alias="TRAEFIK_NETWORK")


settings = Settings()
