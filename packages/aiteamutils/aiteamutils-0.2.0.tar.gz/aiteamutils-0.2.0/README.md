# AI Team Core Utils

AI Team Platform의 공통 유틸리티 패키지입니다.

## 설치 방법

```bash
pip install ai-team-core-utils
```

## 사용 예시

```python
from ai_team_core_utils.database import DatabaseManager
from ai_team_core_utils.base_model import Base

# DB 매니저 초기화
db = DatabaseManager("postgresql+asyncpg://user:pass@localhost/db")

# DB 세션 사용
async with db.get_session() as session:
    # DB 작업 수행
    pass

# 예외 처리
from ai_team_core_utils.exceptions import CustomException, ErrorCode

try:
    # 작업 수행
    pass
except CustomException as e:
    # 에러 처리
    print(e.to_dict())
```

## 주요 기능

- 데이터베이스 유틸리티
  - 세션 관리
  - 트랜잭션 관리
  - 기본 CRUD 작업

- 인증/인가 유틸리티
  - JWT 토큰 관리
  - 비밀번호 해싱
  - Rate Limiting

- 예외 처리
  - 표준화된 에러 코드
  - 에러 체인 추적
  - 로깅 통합

- 공통 모델
  - 기본 모델 클래스
  - 타입 검증
  - 유효성 검사 