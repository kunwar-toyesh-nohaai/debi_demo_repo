from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Noha Interview Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENV: str = "production"
    
    # Database Configuration (Override these in .env file)
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "claude_test_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "Toyesh@2907"  # Fallback default
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from individual components."""
        from urllib.parse import quote_plus
        encoded_user = quote_plus(self.DB_USER)
        encoded_password = quote_plus(self.DB_PASSWORD)
        
        url = f"postgresql+asyncpg://{encoded_user}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        # Debug print to see what's being loaded (masking password)
        safe_url = f"postgresql+asyncpg://{encoded_user}:****@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        print(f"--> LOADING CONFIG: Connecting to {safe_url}")
        return url
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # GCS
    GCS_BUCKET_NAME: str = "noha-storage"
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = "sk-placeholder"
    
    # Calendly
    CALENDLY_API_TOKEN: str = ""
    CALENDLY_WEBHOOK_SECRET: str = ""
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@noha.com"
    SMTP_FROM_NAME: str = "Noha"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        # Use absolute path to ensure .env is found
        import os
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
        case_sensitive = True


settings = Settings()
