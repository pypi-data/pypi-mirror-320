"""의존성 관리 모듈."""
from typing import Type, TypeVar, Dict, Any, Optional, Callable, List, AsyncGenerator
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
import logging

from .exceptions import CustomException, ErrorCode
from .config import get_settings
from .base_service import BaseService
from .base_repository import BaseRepository
from .database import db_manager

T = TypeVar("T", bound=BaseService)
R = TypeVar("R", bound=BaseRepository)

_service_registry: Dict[str, Dict[str, Any]] = {}

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """데이터베이스 세션을 반환합니다.
    
    Yields:
        AsyncSession: 데이터베이스 세션
        
    Raises:
        CustomException: 세션 생성 실패 시
    """
    try:
        async with db_manager.get_session() as session:
            yield session
    except Exception as e:
        raise CustomException(
            ErrorCode.DATABASE_ERROR,
            detail=str(e),
            source_function="dependencies.get_db",
            original_error=e
        )

def register_service(
    service_class: Type[T],
    repository_class: Optional[Type[R]] = None,
    **kwargs
) -> None:
    """서비스를 등록합니다.
    
    Args:
        service_class: 서비스 클래스
        repository_class: 저장소 클래스 (선택)
        **kwargs: 추가 의존성
    """
    service_name = service_class.__name__
    _service_registry[service_name] = {
        "service_class": service_class,
        "repository_class": repository_class,
        "dependencies": kwargs
    }

async def _get_service(
    service_name: str,
    session: AsyncSession,
    request: Request
) -> BaseService:
    """서비스 인스턴스를 생성합니다.
    
    Args:
        service_name: 서비스 이름
        session: 데이터베이스 세션
        request: FastAPI 요청 객체
        
    Returns:
        BaseService: 서비스 인스턴스
        
    Raises:
        CustomException: 서비스 생성 실패 시
    """
    try:
        service_info = _service_registry.get(service_name)
        if not service_info:
            raise CustomException(
                ErrorCode.SERVICE_NOT_FOUND,
                detail=service_name,
                source_function="dependencies._get_service"
            )
            
        service_class = service_info["service_class"]
        repository_class = service_info["repository_class"]
        dependencies = service_info["dependencies"]
        
        # 저장소 인스턴스 생성
        repository = None
        if repository_class:
            repository = repository_class(session=session)
            
        # 서비스 인스턴스 생성
        service = service_class(
            repository=repository,
            session=session,
            request=request,
            **dependencies
        )
        
        return service
        
    except CustomException as e:
        raise e
    except Exception as e:
        raise CustomException(
            ErrorCode.INTERNAL_ERROR,
            detail=str(e),
            source_function="dependencies._get_service",
            original_error=e
        )

def get_service(service_name: str) -> Callable:
    """서비스 의존성을 반환합니다.
    
    Args:
        service_name: 서비스 이름
        
    Returns:
        Callable: 서비스 의존성 함수
    """
    async def _get_service_dependency(
        request: Request,
        session: AsyncSession = Depends(get_db)
    ) -> BaseService:
        return await _get_service(service_name, session, request)
    return _get_service_dependency

async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db),
    auth_service: BaseService = Depends(get_service("AuthService"))
) -> Dict[str, Any]:
    """현재 사용자 정보를 반환합니다.
    
    Args:
        request: FastAPI 요청 객체
        session: 데이터베이스 세션
        auth_service: 인증 서비스
        
    Returns:
        Dict[str, Any]: 사용자 정보
        
    Raises:
        HTTPException: 인증 실패 시
    """
    settings = get_settings()
    
    # Authorization 헤더 검증
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    token = authorization.split(" ")[1]
    
    try:
        # JWT 토큰 디코딩
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.token_issuer,
            audience=settings.token_audience
        )
        
        # 토큰 타입 검증
        token_type = payload.get("token_type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # 사용자 조회
        user_ulid = payload.get("user_ulid")
        if not user_ulid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        user = await auth_service.get_by_ulid(user_ulid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        return user
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )