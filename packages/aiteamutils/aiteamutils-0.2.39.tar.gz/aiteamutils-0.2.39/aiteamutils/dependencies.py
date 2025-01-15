from typing import Type, Dict, Tuple, Any, Callable
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from .database import DatabaseService, get_database_service, get_db
from .exceptions import CustomException, ErrorCode
from .config import get_settings

class ServiceRegistry:
    """서비스 레지스트리를 관리하는 클래스"""
    def __init__(self):
        self._services: Dict[str, Tuple[Type, Type]] = {}
        self._initialized = False

    def clear(self):
        """등록된 모든 서비스를 초기화합니다."""
        self._services.clear()
        self._initialized = False

    def register(self, name: str, repository_class: Type, service_class: Type):
        """서비스를 레지스트리에 등록

        Args:
            name (str): 서비스 이름
            repository_class (Type): Repository 클래스
            service_class (Type): Service 클래스

        Raises:
            CustomException: 이미 등록된 서비스인 경우
        """
        try:
            if name in self._services:
                logging.warning(f"Service '{name}' is already registered. Skipping...")
                return
                
            if not repository_class or not service_class:
                raise CustomException(
                    ErrorCode.INTERNAL_ERROR,
                    detail=f"Invalid service classes for '{name}'",
                    source_function="ServiceRegistry.register"
                )
                
            self._services[name] = (repository_class, service_class)
            logging.info(f"Service '{name}' registered successfully")
            
        except Exception as e:
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                detail=f"Failed to register service '{name}': {str(e)}",
                source_function="ServiceRegistry.register",
                original_error=e
            )

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
                ErrorCode.SERVICE_NOT_REGISTERED,
                detail=f"Service '{name}' is not registered",
                source_function="ServiceRegistry.get"
            )
        return self._services[name]
        
    def is_initialized(self) -> bool:
        """서비스 레지스트리 초기화 여부를 반환합니다."""
        return self._initialized
        
    def set_initialized(self):
        """서비스 레지스트리를 초기화 상태로 설정합니다."""
        self._initialized = True

# ServiceRegistry 초기화
service_registry = ServiceRegistry()

def get_service(name: str):
    """등록된 서비스를 가져오는 의존성 함수

    Args:
        name (str): 서비스 이름

    Returns:
        Callable: 서비스 인스턴스를 반환하는 의존성 함수
        
    Raises:
        CustomException: 서비스 생성 실패 시
    """
    def _get_service(db_service: DatabaseService = Depends(get_database_service)):
        try:
            # 서비스 레지스트리에서 클래스 조회
            try:
                repository_class, service_class = service_registry.get(name)
            except CustomException as e:
                raise CustomException(
                    ErrorCode.SERVICE_NOT_REGISTERED,
                    detail=f"Service '{name}' is not registered",
                    source_function="dependencies.get_service",
                    original_error=e
                )
            
            # 서비스 인스턴스 생성
            try:
                repository = repository_class(db_service)
                return service_class(repository)
            except Exception as e:
                raise CustomException(
                    ErrorCode.INTERNAL_ERROR,
                    detail=f"Failed to create service instance for '{name}': {str(e)}",
                    source_function="dependencies.get_service",
                    original_error=e
                )
                
        except CustomException as e:
            raise e
        except Exception as e:
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                detail=f"Unexpected error while creating service '{name}': {str(e)}",
                source_function="dependencies.get_service",
                original_error=e
            )
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