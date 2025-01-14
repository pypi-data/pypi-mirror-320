"""설정 모듈."""
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """애플리케이션 설정."""
    
    # 데이터베이스 설정
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    
    # JWT 설정
    JWT_SECRET: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TOKEN_ISSUER: str = "ai-team-platform"
    TOKEN_AUDIENCE: str = "ai-team-users"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 