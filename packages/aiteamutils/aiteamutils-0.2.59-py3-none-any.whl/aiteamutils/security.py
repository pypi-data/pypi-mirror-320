"""보안 관련 유틸리티."""
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, Optional, Literal, Callable, TYPE_CHECKING
from fastapi import Request, HTTPException, status
from functools import wraps
from jose import jwt, JWTError
from passlib.context import CryptContext
import logging

from .exceptions import CustomException, ErrorCode
from .enums import ActivityType
from .config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 전역 rate limit 상태 저장
_rate_limits: Dict[str, Dict[str, Any]] = {}

class RateLimitExceeded(CustomException):
    """Rate limit 초과 예외."""
    def __init__(self, detail: str, source_function: str):
        super().__init__(
            ErrorCode.RATE_LIMIT_EXCEEDED,
            detail=detail,
            source_function=source_function
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호를 검증합니다."""
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
    """비밀번호를 해시화합니다."""
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
                raise CustomException(
                    ErrorCode.INTERNAL_ERROR,
                    detail="Request object not found",
                    source_function="rate_limit"
                )
            
            # 레이트 리밋 키 생성
            if key_func:
                rate_limit_key = f"rate_limit:{key_func(request)}"
            else:
                client_ip = request.client.host
                rate_limit_key = f"rate_limit:{client_ip}:{func.__name__}"
            
            try:
                now = datetime.now(UTC)
                
                # 현재 rate limit 정보 가져오기
                rate_info = _rate_limits.get(rate_limit_key)
                
                if rate_info is None or (now - rate_info["start_time"]).total_seconds() >= window_seconds:
                    # 새로운 rate limit 설정
                    _rate_limits[rate_limit_key] = {
                        "count": 1,
                        "start_time": now
                    }
                else:
                    # 기존 rate limit 업데이트
                    if rate_info["count"] >= max_requests:
                        # rate limit 초과
                        remaining_seconds = window_seconds - (now - rate_info["start_time"]).total_seconds()
                        raise CustomException(
                            ErrorCode.RATE_LIMIT_EXCEEDED,
                            detail=f"{int(remaining_seconds)}",
                            source_function=func.__name__
                        )
                    rate_info["count"] += 1
                
                try:
                    # 원래 함수 실행
                    return await func(*args, **kwargs)
                except CustomException as e:
                    raise e
                except Exception as e:
                    raise CustomException(
                        ErrorCode.INTERNAL_ERROR,
                        detail=str(e),
                        source_function=func.__name__,
                        original_error=e
                    )
                    
            except CustomException as e:
                raise e
            except Exception as e:
                raise CustomException(
                    ErrorCode.INTERNAL_ERROR,
                    detail=str(e),
                    source_function="rate_limit",
                    original_error=e
                )
                
        return wrapper
    return decorator

async def create_jwt_token(
    user_data: Dict[str, Any],
    token_type: Literal["access", "refresh"],
    db_service: Any,
    request: Optional[Request] = None
) -> str:
    """JWT 토큰을 생성하고 로그를 기록합니다."""
    try:
        settings = get_settings()
        
        if token_type == "access":
            expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
            token_data = {
                # 등록 클레임
                "iss": settings.token_issuer,
                "sub": user_data["username"],
                "aud": settings.token_audience,
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
                "iss": settings.token_issuer,
                "sub": user_data["username"],
                "exp": expires_at,
                "token_type": token_type,
                "user_ulid": user_data["ulid"]
            }

        try:
            token = jwt.encode(
                token_data,
                settings.jwt_secret,
                algorithm=settings.jwt_algorithm
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
                {
                    "type": activity_type,
                    "user_ulid": user_data["ulid"],
                    "token": token
                },
                request
            )
        except Exception as e:
            # 로그 생성 실패는 토큰 생성에 영향을 주지 않음
            logging.error(f"Failed to create token log: {str(e)}")
        
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
    """JWT 토큰을 검증합니다."""
    try:
        settings = get_settings()
        
        # 토큰 디코딩
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.token_audience,
            issuer=settings.token_issuer
        )
        
        # 토큰 타입 검증
        token_type = payload.get("token_type")
        if not token_type:
            raise CustomException(
                ErrorCode.INVALID_TOKEN,
                detail=token,
                source_function="security.verify_jwt_token"
            )
            
        if expected_type and token_type != expected_type:
            raise CustomException(
                ErrorCode.INVALID_TOKEN,
                detail=token,
                source_function="security.verify_jwt_token"
            )
            
        return payload
        
    except JWTError as e:
        raise CustomException(
            ErrorCode.INVALID_TOKEN,
            detail=token,
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

def validate_token(token: str) -> Dict[str, Any]:
    """JWT 토큰을 검증하고 페이로드를 반환합니다."""
    try:
        settings = get_settings()
        payload = jwt.decode(
            token, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        raise CustomException(
            ErrorCode.INVALID_TOKEN,
            detail=token,
            source_function="security.validate_token",
            original_error=e
        ) 