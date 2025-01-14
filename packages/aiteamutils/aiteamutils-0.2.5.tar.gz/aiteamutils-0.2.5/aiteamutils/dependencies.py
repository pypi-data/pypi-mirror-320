from typing import Type, Dict, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from .database import get_db, DatabaseService
from .exceptions import CustomException, ErrorCode

class Settings:
    """기본 설정 클래스"""
    def __init__(self, jwt_secret: str, jwt_algorithm: str = "HS256"):
        self.JWT_SECRET = jwt_secret
        self.JWT_ALGORITHM = jwt_algorithm

_settings: Settings | None = None

def init_settings(jwt_secret: str, jwt_algorithm: str = "HS256"):
    """설정 초기화 함수
    
    Args:
        jwt_secret (str): JWT 시크릿 키
        jwt_algorithm (str, optional): JWT 알고리즘. Defaults to "HS256".
    """
    global _settings
    _settings = Settings(jwt_secret, jwt_algorithm)

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

class ServiceRegistry:
    """서비스 레지스트리를 관리하는 클래스"""
    def __init__(self):
        self._services: Dict[str, Tuple[Type, Type]] = {}

    def clear(self):
        """등록된 모든 서비스를 초기화합니다."""
        self._services.clear()

    def register(self, name: str, repository_class: Type, service_class: Type):
        """서비스를 레지스트리에 등록

        Args:
            name (str): 서비스 이름
            repository_class (Type): Repository 클래스
            service_class (Type): Service 클래스

        Raises:
            ValueError: 이미 등록된 서비스인 경우
        """
        if name in self._services:
            raise ValueError(f"Service '{name}' is already registered.")
        self._services[name] = (repository_class, service_class)

    def get(self, name: str) -> Tuple[Type, Type]:
        """등록된 서비스를 조회

        Args:
            name (str): 서비스 이름

        Returns:
            Tuple[Type, Type]: (Repository 클래스, Service 클래스) 튜플

        Raises:
            ValueError: 등록되지 않은 서비스인 경우
        """
        if name not in self._services:
            raise ValueError(f"Service '{name}' is not registered.")
        return self._services[name]

# ServiceRegistry 초기화
service_registry = ServiceRegistry()

def get_database_service(db: AsyncSession = Depends(get_db)) -> DatabaseService:
    """DatabaseService 의존성

    Args:
        db (AsyncSession): 데이터베이스 세션

    Returns:
        DatabaseService: DatabaseService 인스턴스
    """
    return DatabaseService(db)

def get_service(name: str):
    """등록된 서비스를 가져오는 의존성 함수

    Args:
        name (str): 서비스 이름

    Returns:
        Callable: 서비스 인스턴스를 반환하는 의존성 함수
    """
    def _get_service(db_service: DatabaseService = Depends(get_database_service)):
        repository_class, service_class = service_registry.get(name)
        repository = repository_class(db_service)
        return service_class(repository, db_service)
    return _get_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_service: DatabaseService = Depends(get_database_service)
):
    """현재 사용자를 가져오는 의존성 함수

    Args:
        token (str): OAuth2 토큰
        db_service (DatabaseService): DatabaseService 객체

    Returns:
        User: 현재 사용자

    Raises:
        CustomException: 인증 실패 시 예외
    """
    try:
        settings = get_settings()
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience="ai-team"
        )
        user_ulid = payload.get("sub")
        if not user_ulid:
            raise CustomException(
                ErrorCode.INVALID_TOKEN,
                source_function="dependencies.py / get_current_user"
            )
    except JWTError:
        raise CustomException(
            ErrorCode.INVALID_TOKEN,
            detail=token[:10] + "...",
            source_function="dependencies.py / get_current_user"
        )

    from app.user.repository import UserRepository
    user_repo = UserRepository(db_service)
    user = await user_repo.get_user(user_ulid, by="ulid")

    if not user:
        raise CustomException(
            ErrorCode.USER_NOT_FOUND,
            source_function="dependencies.py / get_current_user"
        )

    return user