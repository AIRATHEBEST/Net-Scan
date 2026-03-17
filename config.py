from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://netscan:password@localhost:5432/netscan"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # NVD API
    NVD_API_KEY: Optional[str] = None
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Scanning
    SCAN_TIMEOUT: int = 30
    MAX_CONCURRENT_SCANS: int = 255
    PORT_SCAN_TIMEOUT: int = 2
    
    class Config:
        env_file = ".env"

settings = Settings()
