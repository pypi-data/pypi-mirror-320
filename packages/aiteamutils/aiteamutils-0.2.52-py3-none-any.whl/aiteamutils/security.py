"""보안 관련 유틸리티."""
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, Optional, Literal, Callable, Type
from sqlalchemy.orm import DeclarativeBase as Base
from fastapi import Request, HTTPException, status
from functools import wraps
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from .exceptions import CustomException, ErrorCode
from .enums import ActivityType
from .config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 전역 rate limit 상태 저장
_rate_limits: Dict[str, Dict[str, Any]] = {}

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
        """Rate limit 초과 예외를 초기화합니다."""
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

async def create_jwt_token(
    user_data: Dict[str, Any],
    token_type: Literal["access", "refresh"],
    session: AsyncSession,
    log_model: Type[Base],
    request: Optional[Request] = None
) -> str:
    """JWT 토큰을 생성합니다.
    
    Args:
        user_data (Dict[str, Any]): 사용자 데이터
        token_type (Literal["access", "refresh"]): 토큰 타입
        session (AsyncSession): 데이터베이스 세션
        log_model (Type[Base]): 로그 모델
        request (Optional[Request], optional): FastAPI 요청 객체. Defaults to None.
        
    Returns:
        str: 생성된 JWT 토큰
        
    Raises:
        CustomException: 토큰 생성 실패 시
    """
    try:
        settings = get_settings()
        
        if token_type == "access":
            expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
            token_data = {
                # 등록 클레임
                "iss": settings.token_issuer,
                "sub": user_data["ulid"],
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
                "sub": user_data["ulid"],
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
            log_entry = log_model(
                type=activity_type,
                user_ulid=user_data["ulid"],
                token=token
            )
            session.add(log_entry)
            await session.flush()
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
                detail="Token type is missing",
                source_function="security.verify_jwt_token"
            )
            
        if expected_type and token_type != expected_type:
            raise CustomException(
                ErrorCode.INVALID_TOKEN,
                detail=f"Expected {expected_type} token but got {token_type}",
                source_function="security.verify_jwt_token"
            )
            
        # 사용자 식별자 검증
        user_ulid = payload.get("user_ulid")
        if not user_ulid:
            raise CustomException(
                ErrorCode.INVALID_TOKEN,
                detail="User identifier is missing",
                source_function="security.verify_jwt_token"
            )
            
        return payload
        
    except JWTError as e:
        raise CustomException(
            ErrorCode.INVALID_TOKEN,
            detail=str(e),
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