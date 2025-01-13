# AI Team Core Utils

AI Team Platform의 공통 유틸리티 패키지입니다.

## 설치 방법

```bash
pip install ai-team-core-utils
```

## 주요 기능

- 데이터베이스 유틸리티
- 인증/인가 유틸리티
- 공통 모델
- 헬퍼 함수

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
``` 