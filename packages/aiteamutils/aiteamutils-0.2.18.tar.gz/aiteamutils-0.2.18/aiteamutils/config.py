"""설정 모듈."""
from typing import Union
from .database import init_database_service

class Settings:
    """기본 설정 클래스"""
    def __init__(self, jwt_secret: str, jwt_algorithm: str = "HS256"):
        self.JWT_SECRET = jwt_secret
        self.JWT_ALGORITHM = jwt_algorithm

_settings: Union[Settings, None] = None

def init_settings(
    jwt_secret: str,
    jwt_algorithm: str = "HS256",
    db_url: str = None,
    db_echo: bool = False,
    db_pool_size: int = 5,
    db_max_overflow: int = 10,
    db_pool_timeout: int = 30,
    db_pool_recycle: int = 1800
):
    """설정 초기화 함수
    
    Args:
        jwt_secret (str): JWT 시크릿 키
        jwt_algorithm (str, optional): JWT 알고리즘. Defaults to "HS256".
        db_url (str, optional): 데이터베이스 URL
        db_echo (bool, optional): SQL 로깅 여부
        db_pool_size (int, optional): DB 커넥션 풀 크기
        db_max_overflow (int, optional): 최대 초과 커넥션 수
        db_pool_timeout (int, optional): 커넥션 풀 타임아웃
        db_pool_recycle (int, optional): 커넥션 재활용 시간
    """
    global _settings
    _settings = Settings(jwt_secret, jwt_algorithm)
    
    if db_url:
        init_database_service(
            db_url=db_url,
            db_echo=db_echo,
            db_pool_size=db_pool_size,
            db_max_overflow=db_max_overflow,
            db_pool_timeout=db_pool_timeout,
            db_pool_recycle=db_pool_recycle
        )

def get_settings() -> Settings:
    """현재 설정을 반환하는 함수
    
    Returns:
        Settings: 설정 객체
        
    Raises:
        RuntimeError: 설정이 초기화되지 않은 경우
    """
    if _settings is None:
        raise RuntimeError("Settings not initialized. Call init_settings first.")
    return _settings 