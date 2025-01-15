from typing import Type, Dict, Tuple, Any, Callable
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from .database import DatabaseService, get_database_service, get_db
from .exceptions import CustomException, ErrorCode
from .config import get_settings

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
            CustomException: 이미 등록된 서비스인 경우
        """
        if name in self._services:
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                detail=f"service|{name}",
                source_function="ServiceRegistry.register"
            )
        self._services[name] = (repository_class, service_class)

    def get(self, name: str) -> Tuple[Type, Type]:
        """등록된 서비스를 조회

        Args:
            name (str): 서비스 이름

        Returns:
            Tuple[Type, Type]: (Repository 클래스, Service 클래스) 튜플

        Raises:
            CustomException: 등록되지 않은 서비스인 경우
        """
        if name not in self._services:
            raise CustomException(
                ErrorCode.NOT_FOUND,
                detail=f"service|{name}",
                source_function="ServiceRegistry.get"
            )
        return self._services[name]

# ServiceRegistry 초기화
service_registry = ServiceRegistry()

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

    try:
        repository_class, _ = service_registry.get("user")
        user_repo = repository_class(db_service)
        user = await user_repo.get_user(user_ulid, by="ulid")
    except ValueError:
        raise CustomException(
            ErrorCode.SERVICE_NOT_REGISTERED,
            detail="User service is not registered",
            source_function="dependencies.py / get_current_user"
        )

    if not user:
        raise CustomException(
            ErrorCode.USER_NOT_FOUND,
            source_function="dependencies.py / get_current_user"
        )

    return user