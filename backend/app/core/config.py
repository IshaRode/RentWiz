"""
RentWiz – Application Configuration
Reads environment variables via Pydantic BaseSettings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "RentWiz API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Supabase
    supabase_url: str = "https://your-project.supabase.co"
    supabase_service_key: str = "your-service-role-key"
    supabase_anon_key: str = "your-anon-key"

    # ML Model paths (relative to backend/)
    model_path: str = "app/models/rent_model.joblib"
    preprocessor_path: str = "app/models/preprocessor.joblib"

    # AI Explanations
    gemini_api_key: str = ""
    use_ai_explanations: bool = True

    # CORS — can be overridden via ALLOWED_ORIGINS env var (comma-separated)
    @property
    def allowed_origins(self) -> list[str]:
        env_origins = os.getenv("ALLOWED_ORIGINS", "")
        base = [
            "http://localhost:3000",
            "http://localhost:3001",
        ]
        if env_origins:
            base += [o.strip() for o in env_origins.split(",") if o.strip()]
        return base

    # Deal scoring thresholds
    good_deal_threshold: int = 2000      # deal_score > 2000 → good deal
    overpriced_threshold: int = -2000    # deal_score < -2000 → overpriced

    # Scraper
    scraper_headless: bool = True
    scraper_max_listings: int = 50


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
