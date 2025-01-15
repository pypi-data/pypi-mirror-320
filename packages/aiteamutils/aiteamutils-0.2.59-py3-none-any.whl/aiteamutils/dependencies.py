"""의존성 관리 모듈."""
from typing import Type, TypeVar, Dict, Any, Optional, Callable, List, AsyncGenerator
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import CustomException, ErrorCode
from .base_service import BaseService
from .base_repository import BaseRepository
from .database import DatabaseService

T = TypeVar("T", bound=BaseService)
R = TypeVar("R", bound=BaseRepository)

_service_registry: Dict[str, Dict[str, Any]] = {}
_session_provider = None

__all__ = [
    "setup_dependencies",
    "register_service",
    "get_service"
]

def setup_dependencies(session_provider: Callable[[], AsyncGenerator[AsyncSession, None]]) -> None:
    """의존성 설정을 초기화합니다.
    
    Args:
        session_provider: 데이터베이스 세션을 제공하는 함수
    """
    global _session_provider
    _session_provider = session_provider

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
    if _session_provider is None:
        raise CustomException(
            ErrorCode.INTERNAL_ERROR,
            detail="Dependencies not initialized",
            source_function="dependencies.register_service"
        )
        
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
        
        # 데이터베이스 서비스 생성
        db_service = DatabaseService(session=session)
        
        # 저장소 인스턴스 생성
        repository = None
        if repository_class:
            repository = repository_class(session=session)
            
        # 서비스 인스턴스 생성
        service = service_class(
            db=db_service,
            repository=repository,
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
    if _session_provider is None:
        raise CustomException(
            ErrorCode.INTERNAL_ERROR,
            detail="Dependencies not initialized",
            source_function="dependencies.get_service"
        )
    
    async def _get_service_dependency(
        request: Request,
        session: AsyncSession = Depends(_session_provider)
    ) -> BaseService:
        return await _get_service(service_name, session, request)
    return _get_service_dependency