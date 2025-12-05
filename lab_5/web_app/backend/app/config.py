from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Google Cloud
    google_api_key: str
    project_id: str
    location: str = "us-central1"
    model_armor_location: str = "us"
    model_name: str = "gemini-2.5-pro"

    # Model Armor
    model_armor_template_id: str = "lab-five-query-template"
    model_armor_response_template_id: str = "ma-response-filter"

    # RAG
    rag_corpus: str

    # Weather
    noaa_user_agent: str = "WeatherChatbot/1.0"

    # API
    api_timeout: int = 60
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
