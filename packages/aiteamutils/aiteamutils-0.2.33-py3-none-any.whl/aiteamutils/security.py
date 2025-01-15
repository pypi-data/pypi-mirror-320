"""보안 관련 유틸리티."""
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, Optional, Literal, Callable, Type
from sqlalchemy.orm import DeclarativeBase as Base
from fastapi import Request, HTTPException, status
from functools import wraps
from jose import jwt, JWTError
from passlib.context import CryptContext

from .exceptions import CustomException, ErrorCode
from .database import DatabaseService
from .enums import ActivityType
from .config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RateLimitExceeded(CustomException):
    """Rate limit 초과 예외."""
    
    def __init__(
        self,
        detail: str,
        source_function: str,
        remaining_seconds: float,
        max_requests: int,
        window_seconds: int
    ):
        """Rate limit 초과 예외를 초기화합니다.
        
        Args:
            detail: 상세 메시지
            source_function: 예외가 발생한 함수명
            remaining_seconds: 다음 요청까지 남은 시간 (초)
            max_requests: 허용된 최대 요청 수
            window_seconds: 시간 윈도우 (초)
        """
        super().__init__(
            ErrorCode.RATE_LIMIT_EXCEEDED,
            detail=detail,
            source_function=source_function,
            metadata={
                "remaining_seconds": remaining_seconds,
                "max_requests": max_requests,
                "window_seconds": window_seconds
            }
        )
        self.remaining_seconds = remaining_seconds
        self.max_requests = max_requests
        self.window_seconds = window_seconds

class SecurityError(CustomException):
    """보안 관련 기본 예외."""
    
    def __init__(
        self,
        error_code: ErrorCode,
        detail: str,
        source_function: str,
        original_error: Optional[Exception] = None
    ):
        """보안 관련 예외를 초기화합니다.
        
        Args:
            error_code: 에러 코드
            detail: 상세 메시지
            source_function: 예외가 발생한 함수명
            original_error: 원본 예외
        """
        super().__init__(
            error_code,
            detail=detail,
            source_function=f"security.{source_function}",
            original_error=original_error
        )

class TokenError(SecurityError):
    """토큰 관련 예외."""
    
    def __init__(
        self,
        detail: str,
        source_function: str,
        original_error: Optional[Exception] = None
    ):
        """토큰 관련 예외를 초기화합니다."""
        super().__init__(
            ErrorCode.INVALID_TOKEN,
            detail=detail,
            source_function=source_function,
            original_error=original_error
        )

class RateLimiter:
    """Rate limit 관리 클래스."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        """Rate limiter를 초기화합니다.
        
        Args:
            max_requests: 허용된 최대 요청 수
            window_seconds: 시간 윈도우 (초)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        
    def is_allowed(self, key: str) -> bool:
        """현재 요청이 허용되는지 확인합니다.
        
        Args:
            key: Rate limit 키
            
        Returns:
            bool: 요청 허용 여부
        """
        now = datetime.now(UTC)
        rate_info = self._cache.get(key)
        
        if rate_info is None or (now - rate_info["start_time"]).total_seconds() >= self.window_seconds:
            self._cache[key] = {
                "count": 1,
                "start_time": now
            }
            return True
            
        if rate_info["count"] >= self.max_requests:
            return False
            
        rate_info["count"] += 1
        return True
        
    def get_remaining_time(self, key: str) -> float:
        """남은 시간을 반환합니다.
        
        Args:
            key: Rate limit 키
            
        Returns:
            float: 남은 시간 (초)
        """
        rate_info = self._cache.get(key)
        if not rate_info:
            return 0
            
        now = datetime.now(UTC)
        return max(
            0,
            self.window_seconds - (now - rate_info["start_time"]).total_seconds()
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호를 검증합니다.
    
    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호
        
    Returns:
        bool: 비밀번호 일치 여부
        
    Raises:
        CustomException: 비밀번호 검증 실패 시
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        raise CustomException(
            ErrorCode.INVALID_PASSWORD,
            detail=plain_password,
            source_function="security.verify_password",
            original_error=e
        )

def hash_password(password: str) -> str:
    """비밀번호를 해시화합니다.
    
    Args:
        password: 평문 비밀번호
        
    Returns:
        str: 해시된 비밀번호
        
    Raises:
        CustomException: 비밀번호 해시화 실패 시
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise CustomException(
            ErrorCode.INTERNAL_ERROR,
            detail=password,
            source_function="security.hash_password",
            original_error=e
        )

def rate_limit(
    max_requests: int,
    window_seconds: int,
    key_func: Optional[Callable] = None
):
    """Rate limiting 데코레이터."""
    limiter = RateLimiter(max_requests, window_seconds)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Request 객체 찾기
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                for arg in kwargs.values():
                    if isinstance(arg, Request):
                        request = arg
                        break
            if not request:
                raise SecurityError(
                    ErrorCode.INTERNAL_ERROR,
                    detail="Request object not found",
                    source_function="rate_limit"
                )
            
            # Rate limit 키 생성
            if key_func:
                rate_limit_key = f"rate_limit:{key_func(request)}"
            else:
                client_ip = request.client.host
                rate_limit_key = f"rate_limit:{client_ip}:{func.__name__}"
            
            try:
                if not limiter.is_allowed(rate_limit_key):
                    remaining_time = limiter.get_remaining_time(rate_limit_key)
                    raise RateLimitExceeded(
                        detail=f"Rate limit exceeded. Try again in {int(remaining_time)} seconds",
                        source_function=func.__name__,
                        remaining_seconds=remaining_time,
                        max_requests=max_requests,
                        window_seconds=window_seconds
                    )
                
                return await func(*args, **kwargs)
                    
            except (RateLimitExceeded, SecurityError) as e:
                raise e
            except Exception as e:
                raise SecurityError(
                    ErrorCode.INTERNAL_ERROR,
                    detail=str(e),
                    source_function="rate_limit",
                    original_error=e
                )
                
        return wrapper
    return decorator

class TokenCreationError(SecurityError):
    """토큰 생성 관련 예외."""
    
    def __init__(
        self,
        detail: str,
        source_function: str,
        token_type: str,
        original_error: Optional[Exception] = None
    ):
        """토큰 생성 예외를 초기화합니다.
        
        Args:
            detail: 상세 메시지
            source_function: 예외가 발생한 함수명
            token_type: 토큰 타입
            original_error: 원본 예외
        """
        super().__init__(
            ErrorCode.INTERNAL_ERROR,
            detail=detail,
            source_function=source_function,
            original_error=original_error
        )
        self.token_type = token_type

async def create_jwt_token(
    user_data: Dict[str, Any],
    token_type: Literal["access", "refresh"],
    db_service: DatabaseService,
    log_model: Type[Base],
    request: Optional[Request] = None
) -> str:
    """JWT 토큰을 생성하고 로그를 기록합니다.
    
    Args:
        user_data: 사용자 데이터 딕셔너리 (username, ulid, name, role_ulid, status, organization 정보 등)
        token_type: 토큰 타입 ("access" 또는 "refresh")
        db_service: 데이터베이스 서비스
        log_model: 로그 모델 클래스
        request: FastAPI 요청 객체
        
    Returns:
        str: 생성된 JWT 토큰
        
    Raises:
        CustomException: 토큰 생성 실패 시
    """
    try:
        settings = get_settings()
        
        # 필수 필드 검증
        required_fields = {"username", "ulid"}
        missing_fields = required_fields - set(user_data.keys())
        if missing_fields:
            raise CustomException(
                ErrorCode.REQUIRED_FIELD_MISSING,
                detail="|".join(missing_fields),
                source_function="security.create_jwt_token"
            )
        
        if token_type == "access":
            expires_at = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            token_data = {
                # 등록 클레임
                "iss": settings.TOKEN_ISSUER,
                "sub": user_data["username"],
                "aud": settings.TOKEN_AUDIENCE,
                "exp": expires_at,
                
                # 공개 클레임
                "username": user_data["username"],
                "name": user_data.get("name"),
                
                # 비공개 클레임
                "user_ulid": user_data["ulid"],
                "role_ulid": user_data.get("role_ulid"),
                "status": user_data.get("status"),
                "last_login": datetime.now(UTC).isoformat(),
                "token_type": token_type,
                
                # 조직 관련 클레임
                "organization_ulid": user_data.get("organization_ulid"),
                "organization_id": user_data.get("organization_id"),
                "organization_name": user_data.get("organization_name"),
                "company_name": user_data.get("company_name")
            }
        else:  # refresh token
            expires_at = datetime.now(UTC) + timedelta(days=14)
            token_data = {
                "iss": settings.TOKEN_ISSUER,
                "sub": user_data["username"],
                "exp": expires_at,
                "token_type": token_type,
                "user_ulid": user_data["ulid"]
            }
        
        try:
            token = jwt.encode(
                token_data,
                settings.JWT_SECRET,
                algorithm=settings.JWT_ALGORITHM
            )
        except Exception as e:
            raise CustomException(
                ErrorCode.INTERNAL_ERROR,
                detail=f"token|{token_type}",
                source_function="security.create_jwt_token",
                original_error=e
            )
        
        # 로그 생성
        try:
            activity_type = ActivityType.ACCESS_TOKEN_ISSUED if token_type == "access" else ActivityType.REFRESH_TOKEN_ISSUED
            await db_service.create_log(
                model=log_model,
                log_data={
                    "type": activity_type,
                    "user_ulid": user_data["ulid"],
                    "token": token
                },
                request=request
            )
        except Exception as e:
            # 로그 생성 실패는 토큰 생성에 영향을 주지 않음
            pass
        
        return token
        
    except CustomException as e:
        raise e
    except Exception as e:
        raise CustomException(
            ErrorCode.INTERNAL_ERROR,
            detail=str(e),
            source_function="security.create_jwt_token",
            original_error=e
        )

async def verify_jwt_token(
    token: str,
    expected_type: Optional[Literal["access", "refresh"]] = None
) -> Dict[str, Any]:
    """JWT 토큰을 검증합니다.
    
    Args:
        token: 검증할 JWT 토큰
        expected_type: 예상되는 토큰 타입
        
    Returns:
        Dict[str, Any]: 토큰 페이로드
        
    Raises:
        CustomException: 토큰 검증 실패 시
    """
    try:
        settings = get_settings()
        # 토큰 디코딩
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.TOKEN_AUDIENCE,
            issuer=settings.TOKEN_ISSUER
        )
        
        # 토큰 타입 검증 (expected_type이 주어진 경우에만)
        if expected_type and payload.get("token_type") != expected_type:
            raise CustomException(
                ErrorCode.INVALID_TOKEN,
                detail=f"token|{expected_type}|{payload.get('token_type')}",
                source_function="security.verify_jwt_token"
            )
        
        return payload
        
    except JWTError as e:
        raise CustomException(
            ErrorCode.INVALID_TOKEN,
            detail=token[:10] + "...",
            source_function="security.verify_jwt_token",
            original_error=e
        )
    except CustomException as e:
        raise e
    except Exception as e:
        raise CustomException(
            ErrorCode.INTERNAL_ERROR,
            detail=str(e),
            source_function="security.verify_jwt_token",
            original_error=e
        ) 