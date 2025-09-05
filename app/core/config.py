"""
Configuration settings for Hive Backend application.
Handles environment variables, database settings, API keys, and application constants.

ASSIGNED TO: Dhruv Pokhriyal
TASK: Configuration system implementation with Supabase integration
- Database configuration (Supabase connection)
- API keys and external service configurations
- Environment-specific settings
- Application-wide constants
- Security and authentication settings
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SupabaseSettings(BaseSettings):
    """Supabase configuration settings for database and auth."""
    
    url: str = os.getenv("SUPABASE_URL", "")
    anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    class Config:
        env_prefix = "SUPABASE_"

class SecuritySettings(BaseSettings):
    """Security and authentication settings."""
    
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    class Config:
        env_prefix = "SECURITY_"

class GeminiSettings(BaseSettings):
    """Google Gemini API configuration for RAG pipeline."""
    
    api_key: str = os.getenv("GEMINI_API_KEY", "")
    model: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    embed_model: str = os.getenv("GEMINI_EMBED_MODEL", "models/embedding-001")
    max_output_tokens: int = int(os.getenv("GEMINI_MAX_TOKENS", "1000"))
    temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    
    class Config:
        env_prefix = "GEMINI_"


class VectorDBSettings(BaseSettings):
    """Vector database configuration (Chroma)."""
    
    chroma_persist_path: str = os.getenv("CHROMA_PERSIST_PATH", ".chroma")
    collection_name: str = os.getenv("CHROMA_COLLECTION", "verification_docs")
    
    class Config:
        env_prefix = "CHROMA_"

class ScrapingSettings(BaseSettings):
    """Web scraping configuration settings."""
    
    delay: int = int(os.getenv("SCRAPING_DELAY", "1"))
    timeout: int = int(os.getenv("SCRAPING_TIMEOUT", "30"))
    user_agent: str = os.getenv("SCRAPING_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    max_concurrent: int = int(os.getenv("MAX_CONCURRENT_SCRAPES", "5"))
    
    class Config:
        env_prefix = "SCRAPING_"

class APISettings(BaseSettings):
    """External API configuration."""
    
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    fact_check_api_key: str = os.getenv("FACT_CHECK_API_KEY", "")
    
    class Config:
        env_prefix = "API_"
    


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    
    level: str = os.getenv("LOG_LEVEL", "INFO")
    file: str = os.getenv("LOG_FILE", "logs/hive_backend.log")
    
    class Config:
        env_prefix = "LOG_"

class RateLimitSettings(BaseSettings):
    """Rate limiting configuration."""
    
    per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    per_hour: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    class Config:
        env_prefix = "RATE_LIMIT_"

class FileUploadSettings(BaseSettings):
    """File upload configuration."""
    
    max_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads/")
    allowed_extensions: List[str] = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,pdf,txt").split(",")
    
    class Config:
        env_prefix = "FILE_"

class EmailSettings(BaseSettings):
    """Email configuration for notifications."""
    
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    email_from: str = os.getenv("EMAIL_FROM", "noreply@hive.com")
    
    class Config:
        env_prefix = "EMAIL_"

class MonitoringSettings(BaseSettings):
    """Monitoring and analytics configuration."""
    
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN")
    analytics_enabled: bool = os.getenv("ANALYTICS_ENABLED", "True").lower() == "true"
    
    class Config:
        env_prefix = "MONITORING_"

class Settings(BaseSettings):
    """Main application settings."""
    
    # Application settings
    app_name: str = os.getenv("APP_NAME", "Hive Backend")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Server settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    reload: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # Sub-settings
    supabase: SupabaseSettings = SupabaseSettings()
    security: SecuritySettings = SecuritySettings()
    gemini: GeminiSettings = GeminiSettings()
    vectordb: VectorDBSettings = VectorDBSettings()
    scraping: ScrapingSettings = ScrapingSettings()
    api: APISettings = APISettings()
    logging: LoggingSettings = LoggingSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    file_upload: FileUploadSettings = FileUploadSettings()
    email: EmailSettings = EmailSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting."""
        allowed = ["development", "testing", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("debug")
    def validate_debug(cls, v, values):
        """Ensure debug is False in production."""
        if values.get("environment") == "production" and v:
            return False
        return v
    
    # Pydantic v2 configuration: read from .env and ignore unrelated env keys
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

# Create global settings instance
settings = Settings()

# Convenience functions for accessing settings
def get_supabase_url() -> str:
    """Get Supabase URL."""
    return settings.supabase.url

def get_supabase_anon_key() -> str:
    """Get Supabase anonymous key."""
    return settings.supabase.anon_key

def get_supabase_service_key() -> str:
    """Get Supabase service role key."""
    return settings.supabase.service_role_key

def is_development() -> bool:
    """Check if running in development mode."""
    return settings.environment == "development"

def is_production() -> bool:
    """Check if running in production mode."""
    return settings.environment == "production"

def is_testing() -> bool:
    """Check if running in testing mode."""
    return settings.environment == "testing"
