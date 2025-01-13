"""보안 관련 유틸리티."""
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, Optional, Literal, Callable, TYPE_CHECKING
from fastapi import Request, HTTPException, status
from functools import wraps
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.utils.exceptions import CustomException, ErrorCode
from app.utils.database import DatabaseService
from app.utils.enums import ActivityType
from app.config import settings

if TYPE_CHECKING:
    from app.user.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RateLimitExceeded(CustomException):
    """Rate limit 초과 예외."""
    def __init__(self, detail: str, source_function: str):
        super().__init__(
            ErrorCode.RATE_LIMIT_EXCEEDED,
            detail=detail,
            source_function=source_function
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호를 검증합니다.
    
    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호
        
    Returns:
        bool: 비밀번호 일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """비밀번호를 해시화합니다.
    
    Args:
        password: 평문 비밀번호
        
    Returns:
        str: 해시된 비밀번호
    """
    return pwd_context.hash(password)

def rate_limit(
    max_requests: int,
    window_seconds: int,
    key_func: Optional[Callable] = None
):
    """Rate limiting 데코레이터."""
    rate_limits: Dict[str, Dict[str, Any]] = {}
    
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
                rate_info = rate_limits.get(rate_limit_key)
                
                if rate_info is None or (now - rate_info["start_time"]).total_seconds() >= window_seconds:
                    # 새로운 rate limit 설정
                    rate_limits[rate_limit_key] = {
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
                    # CustomException은 그대로 전파
                    raise e
                except Exception as e:
                    # 다른 예외는 INTERNAL_ERROR로 래핑
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
    user: Any,
    token_type: Literal["access", "refresh"],
    db_service: DatabaseService,
    request: Optional[Request] = None
) -> str:
    """JWT 토큰을 생성하고 로그를 기록합니다.
    
    Args:
        user: 사용자 정보
        token_type: 토큰 타입 ("access" 또는 "refresh")
        db_service: 데이터베이스 서비스
        request: FastAPI 요청 객체
        
    Returns:
        str: 생성된 JWT 토큰
        
    Raises:
        CustomException: 토큰 생성 실패 시
    """
    try:
        if token_type == "access":
            expires_at = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            token_data = {
                # 등록 클레임 (Registered Claims)
                "iss": settings.TOKEN_ISSUER,  # 토큰 발급자
                "sub": user.username,   # 토큰 주체
                "aud": settings.TOKEN_AUDIENCE, # 토큰 대상자
                "exp": expires_at,  # 토큰 만료 시간
                
                # 공개 클레임 (Public Claims)
                "username": user.username,
                "name": user.name,
                
                # 비공개 클레임 (Private Claims)
                "user_ulid": user.ulid,
                "role_ulid": user.role_ulid,
                "status": user.status,
                "last_login": datetime.now(UTC).isoformat(),
                "token_type": token_type,
                
                # 조직 관련 클레임
                "organization_ulid": user.role.organization.ulid if user.role and user.role.organization else None,
                "organization_id": user.role.organization.id if user.role and user.role.organization else None,
                "organization_name": user.role.organization.name if user.role and user.role.organization else None,
                "company_name": user.role.organization.company.name if user.role and user.role.organization and user.role.organization.company else None
            }
            
            # 액세스 토큰 발급 로그 생성
            token = jwt.encode(
                token_data,
                settings.JWT_SECRET,
                algorithm=settings.JWT_ALGORITHM
            )
            
            await db_service.create_log(
                {
                    "type": ActivityType.ACCESS_TOKEN_ISSUED,
                    "user_ulid": user.ulid,
                    "token": token
                },
                request
            )
            
            return token
            
        else:  # refresh token
            expires_at = datetime.now(UTC) + timedelta(days=14)
            token_data = {
                "iss": settings.TOKEN_ISSUER,
                "sub": user.username,
                "exp": expires_at,  # 리프레시 토큰은 14일간 유효
                "user_ulid": user.ulid,
                "token_type": token_type
            }
            
            # 리프레시 토큰 발급 로그 생성
            token = jwt.encode(
                token_data,
                settings.JWT_SECRET,
                algorithm=settings.JWT_ALGORITHM
            )
            
            await db_service.create_log(
                {
                    "type": ActivityType.REFRESH_TOKEN_ISSUED,
                    "user_ulid": user.ulid,
                    "token": token
                },
                request
            )
            
            return token
        
    except Exception as e:
        raise CustomException(
            ErrorCode.INTERNAL_ERROR,
            detail=str(e),
            source_function="security.create_jwt_token",
            original_error=e
        )

async def verify_jwt_token(token: str, expected_type: Literal["access", "refresh"]) -> Dict[str, Any]:
    """JWT 토큰을 검증합니다.
    
    Args:
        token: JWT 토큰
        expected_type: 예상되는 토큰 타입 ("access" 또는 "refresh")
        
    Returns:
        Dict[str, Any]: 디코딩된 토큰 페이로드
        
    Raises:
        CustomException: 토큰 검증 실패 시
    """
    try:
        # 토큰 디코딩
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.TOKEN_AUDIENCE,
            issuer=settings.TOKEN_ISSUER
        )
        
        # 토큰 타입 검증
        if payload.get("token_type") != expected_type:
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
    """JWT 토큰을 검증하고 페이로드를 반환합니다.
    
    Args:
        token: JWT 토큰
        
    Returns:
        Dict[str, Any]: 토큰의 페이로드
        
    Raises:
        CustomException: 토큰이 유효하지 않은 경우
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise CustomException(
            ErrorCode.INVALID_TOKEN,
            detail=str(e),
            source_function="security.validate_token",
            original_error=e
        ) 