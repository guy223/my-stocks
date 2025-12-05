# my-stocks 프로젝트 가이드

## 프로젝트 개요

효과적인 주식 투자를 위한 시장 동향 분석 및 리포트 생성 프로젝트입니다.

## 주요 기능

- 주식 시장 동향 모니터링
- 가격 변동사항 추적 및 분석
- 투자 분석 리포트 자동 생성
- 알림 및 리포트 전송

## 개발 가이드라인

### 코드 스타일
- 명확하고 읽기 쉬운 코드 작성
- 함수와 변수명은 명확한 의미 전달
- 필요한 경우에만 주석 추가

### 커밋 메시지
- 한글로 작성
- 명확하고 간결하게 변경 내용 설명

### 데이터 처리
- 주식 데이터는 실시간성이 중요하므로 효율적인 처리 필요
- API 호출 시 rate limit 고려
- 에러 처리 및 재시도 로직 구현

## 프로젝트 구조

```
my-stocks/
├── src/           # 소스 코드
├── data/          # 데이터 저장소
├── reports/       # 생성된 리포트
├── config/        # 설정 파일
└── tests/         # 테스트 코드
```

## 환경 설정

### 필수 환경 변수
- API 키 및 인증 정보는 `.env` 파일에 저장
- `.env` 파일은 git에 커밋하지 않음

### 주식 데이터 소스
- 사용할 API 선택 (예: Yahoo Finance, Alpha Vantage, KRX 등)
- API 키 발급 및 설정

## 리포트 생성

- 일일/주간/월간 리포트 자동 생성
- 주요 지표: 가격 변동률, 거래량, 기술적 지표 등
- 이메일 또는 메시징 서비스를 통한 전송

## 보안 주의사항

- API 키, 계정 정보 등 민감한 정보는 절대 코드에 직접 포함하지 않음
- 환경 변수 또는 안전한 저장소 사용
- `.gitignore`에 민감한 파일 패턴 추가

## CLI 명령어 레퍼런스

### 일일 리포트 생성
```bash
# 오늘 날짜 리포트 + 자동 데이터 수집 (가장 많이 사용)
uv run report

# 특정 날짜 리포트
uv run report 20251204

# 강제 재수집 후 리포트
uv run report --fetch

# 데이터 수집 없이 리포트만 생성
uv run report --no-fetch

# 수집 범위 지정
uv run report --mode today       # 당일만
uv run report --mode recent      # 최근 5일 (기본값)
uv run report --mode month       # 최근 30일

# 조합 예제
uv run report 20251204 --fetch --mode month
```

### 테스트 실행
```bash
# 전체 테스트
uv run test-stocks

# 특정 파일만 테스트
uv run test-stocks tests/unit/test_krx_client.py

# 특정 테스트 함수만
uv run test-stocks tests/unit/test_krx_client.py::TestKRXClient::test_get_ohlcv

# 키워드로 필터링
uv run test-stocks -k "client"

# 커버리지 리포트
uv run test-stocks --cov=src --cov-report=html

# 상세 출력
uv run test-stocks -v
```

### 데이터 수집
```bash
# 관심 종목 데이터 수집 (최근 5일, 기본)
uv run collect

# 당일만 수집
uv run collect --today

# 최근 30일 수집
uv run collect --month

# 강제 재수집 (기존 데이터 덮어쓰기)
uv run collect --force

# 특정 날짜 기준으로 수집
uv run collect 20251203
```

### 데이터 조회
```bash
# DB에 저장된 데이터 조회 예제 실행
uv run query
```

### Make 명령어 (Linux/Mac)
```bash
make report      # 일일 리포트 생성
make test        # 단위 테스트 실행
make test-cov    # 테스트 + 커버리지 리포트
make collect     # 데이터 수집
make query       # 데이터 조회
make clean       # 캐시 정리 (__pycache__, .pytest_cache 등)
make help        # 도움말
```

### pyproject.toml 엔트리포인트
CLI 명령어는 다음 엔트리포인트로 정의되어 있습니다:
- `report` → `cli:report_command`
- `test-stocks` → `cli:test_command`
- `collect` → `cli:collect_command`
- `query` → `cli:query_command`

## PyKrx API 제약사항 및 주의사항

### Rate Limiting (매우 중요!)
- **요청 간 1초 딜레이 필수** (`time.sleep(1)`)
- KRX 서버가 과도한 요청을 차단함
- 딜레이 없이 연속 실행 시 IP 차단 가능성 있음
- 현재 구현: 모든 API 호출 후 자동으로 1초 대기

### 재시도 로직
```python
# 현재 구현된 재시도 메커니즘
- 최대 3회 재시도
- 재시도 간격: 5초
- 공매도 데이터는 실패해도 계속 진행 (선택적 데이터)
```

### 데이터 제공 시점
- **당일 데이터**: 장 마감 후 약 **18:00 이후** 제공
- **주말/공휴일**: 데이터 없음 (거래일만 데이터 존재)
- **거래 정지 종목**: 데이터 누락 가능
- 권장 실행 시간: 평일 18:30 이후

### PyKrx API 함수 예시
```python
from pykrx import stock

# OHLCV 데이터
stock.get_market_ohlcv(start_date, end_date, ticker)

# 시가총액 및 거래 정보
stock.get_market_cap(start_date, end_date, ticker)

# 펀더멘탈 지표 (PER, PBR, EPS 등)
stock.get_market_fundamental(start_date, end_date, ticker)

# 투자자별 매매 동향
stock.get_market_trading_by_date(start_date, end_date, ticker)

# 공매도 거래
stock.get_shorting_volume_by_date(start_date, end_date, ticker)

# 공매도 잔고
stock.get_shorting_balance_by_date(start_date, end_date, ticker)
```

### 데이터 수집 범위 권장사항
- **1일**: 즉시 실행 (딜레이 최소)
- **5일**: 약 30초 소요 (권장)
- **30일**: 약 3분 소요
- **1년**: 약 20분 소요 (타임아웃 가능성)

## 개발 워크플로우

### 새로운 기능 추가
1. **테스트 먼저 작성 (TDD 권장)**
   ```bash
   # tests/unit/test_new_feature.py 작성
   uv run test-stocks tests/unit/test_new_feature.py
   ```

2. **기능 구현**
   - `src/` 하위에 모듈 추가
   - 기존 아키텍처 패턴 따르기 (Layered Architecture)
   - Context manager 사용 (Database 세션)

3. **테스트 실행 및 커버리지 확인**
   ```bash
   uv run test-stocks --cov=src --cov-report=html
   open htmlcov/index.html  # 브라우저에서 확인
   ```

4. **통합 테스트**
   ```bash
   uv run report --fetch    # 실제 데이터로 동작 확인
   ```

5. **커밋**
   ```bash
   git add .
   git commit -m "새로운 기능 추가: XXX"
   git push
   ```

### 관심 종목 추가
1. **watchlist 설정 파일 수정**
   ```python
   # src/config/watchlist.py
   WATCHLIST = [
       ("267260", "HD현대일렉트릭", "KOSPI"),
       ("064350", "현대로템", "KOSPI"),
       ("005930", "삼성전자", "KOSPI"),  # 새로운 종목 추가
   ]
   ```

2. **데이터 수집**
   ```bash
   # 최근 30일 데이터 수집 (초기 수집)
   uv run collect --month
   ```

3. **리포트 확인**
   ```bash
   uv run report
   ```

### 버그 수정
1. **재현 테스트 작성**
   ```bash
   # 버그를 재현하는 테스트 작성
   uv run test-stocks tests/unit/test_bug_fix.py
   ```

2. **버그 수정 및 테스트 통과 확인**
   ```bash
   # 수정 후 테스트 재실행
   uv run test-stocks
   ```

3. **회귀 테스트**
   ```bash
   # 전체 테스트 실행하여 기존 기능 정상 작동 확인
   uv run test-stocks --cov=src
   ```

### 리팩토링
1. **테스트 커버리지 확인** (리팩토링 전)
   ```bash
   uv run test-stocks --cov=src --cov-report=html
   ```

2. **리팩토링 수행**
   - 테스트가 통과하는 상태 유지
   - 작은 단위로 커밋

3. **테스트 재실행** (리팩토링 후)
   ```bash
   uv run test-stocks
   # 모든 테스트가 여전히 통과해야 함
   ```

## Python 코딩 컨벤션

### Python 스타일 가이드
- **PEP 8** 준수
- **타입 힌트** 사용 권장 (Optional, List, Dict, Tuple 등)
- **Docstring**: 복잡한 함수에만 추가 (간단한 함수는 생략 가능)
- **Line length**: 최대 100자 (PEP 8은 79자이지만 현대적 기준)

### 네이밍 규칙
```python
# 클래스: PascalCase
class DailyReport:
    pass

class KRXClient:
    pass

# 함수/변수: snake_case
def get_latest_price(session, ticker):
    daily_price = ...
    return daily_price

# 상수: UPPER_SNAKE_CASE
WATCHLIST = [...]
MAX_RETRIES = 3
DEFAULT_DELAY = 1

# Private 메서드/변수: _leading_underscore
def _format_number(self, value):
    pass

_internal_cache = {}
```

### Import 순서
```python
# 1. 표준 라이브러리
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict

# 2. 서드파티 라이브러리
import pandas as pd
from sqlalchemy import create_engine
from pykrx import stock

# 3. 로컬 모듈
from models import Stock, DailyPrice
from database.connection import Database
from krx.client import KRXClient
```

### 타입 힌트 사용 예시
```python
from typing import Optional, List, Dict, Tuple
from datetime import date

def get_daily_prices(
    session,
    ticker: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[DailyPrice]:
    """타입 힌트로 명확한 인터페이스 제공"""
    pass

def fetch_stock_data(
    ticker: str,
    name: str,
    market: str,
    date_str: str,
    fetch_mode: str = 'today'
) -> Dict[str, int]:
    """반환값: {'success': 6, 'failed': 1}"""
    pass
```

### Context Manager 패턴
```python
# 권장: Context manager 사용
with Database().get_session() as session:
    stocks = StockQueries.get_all_stocks(session)
    # 세션 자동 종료

# 비권장: 수동 세션 관리
session = db.get_session()
try:
    stocks = StockQueries.get_all_stocks(session)
finally:
    session.close()
```

### 예외 처리 패턴
```python
# 명확한 예외 처리
try:
    data = stock.get_market_ohlcv(...)
except Exception as e:
    print(f"❌ 데이터 수집 실패: {e}")
    return None

# 특정 예외만 catch
from sqlalchemy.exc import IntegrityError

try:
    session.add(price)
    session.commit()
except IntegrityError:
    session.rollback()  # 중복 데이터 스킵
```

## 프로젝트 디렉토리 구조 규칙

### src/ 하위 구조
```
src/
├── models/              # SQLAlchemy 모델 (테이블 정의)
│   ├── __init__.py     # 통합 export
│   ├── stock.py        # Stock 모델
│   ├── daily_price.py  # DailyPrice 모델
│   └── ...
│
├── database/           # DB 연결 및 쿼리
│   ├── connection.py   # Database 클래스
│   └── queries.py      # StockQueries 클래스
│
├── krx/                # KRX API 클라이언트
│   ├── client.py       # KRXClient (PyKrx 래퍼)
│   └── saver.py        # DataSaver (데이터 저장)
│
├── analysis/           # 분석 로직
│   └── market_summary.py  # 시장 동향 분석
│
├── report/             # 리포트 생성
│   └── daily_report.py    # DailyReport 클래스
│
├── config/             # 설정 파일
│   └── watchlist.py    # 관심 종목 리스트
│
├── cli.py              # CLI 엔트리포인트
├── data_fetcher.py     # 데이터 수집 통합 모듈
└── main.py             # 메인 실행 스크립트
```

### 파일명 규칙
- **모듈 파일**: `snake_case.py` (예: `daily_report.py`, `market_summary.py`)
- **클래스와 파일명 일치 권장**:
  - `DailyReport` 클래스 → `daily_report.py`
  - `KRXClient` 클래스 → `client.py` (krx/ 하위)
- **테스트 파일**: `test_` prefix (예: `test_daily_report.py`)
- **설정 파일**: 명확한 이름 (예: `watchlist.py`, `config.py`)

### __init__.py 용도
```python
# models/__init__.py - 외부에서 import할 항목만 명시
from .stock import Stock
from .daily_price import DailyPrice
from .market_cap import MarketCap
from .fundamental import Fundamental
from .trading_by_investor import TradingByInvestor
from .short_selling import ShortSelling
from .short_balance import ShortBalance

__all__ = [
    'Stock',
    'DailyPrice',
    'MarketCap',
    'Fundamental',
    'TradingByInvestor',
    'ShortSelling',
    'ShortBalance',
]
```

### 계층 구조 원칙
```
외부 API (PyKrx)
    ↓
krx/ (API 호출 및 데이터 저장)
    ↓
database/ (데이터 조회)
    ↓
analysis/ (데이터 분석)
    ↓
report/ (리포트 생성)
    ↓
CLI / main.py (사용자 인터페이스)
```

### 모듈 의존성 규칙
- **models**: 의존성 없음 (순수 데이터 모델)
- **database**: models에만 의존
- **krx**: models, database에 의존
- **analysis**: models, database에 의존
- **report**: analysis, database에 의존
- **CLI**: 모든 모듈 사용 가능

### 테스트 파일 구조
```
tests/
├── conftest.py                    # 공통 픽스처
├── unit/                          # 단위 테스트
│   ├── test_database_connection.py
│   ├── test_krx_client.py
│   ├── test_krx_saver.py
│   ├── test_database_queries.py
│   ├── test_data_fetcher.py
│   └── test_daily_report.py
│
└── integration/                   # 통합 테스트 (향후 추가)
    └── test_end_to_end.py
```

### 데이터 디렉토리
```
data/
└── stocks.db          # SQLite 데이터베이스 (gitignore)

reports/
└── daily_report_*.txt # 생성된 리포트 (gitignore)
```
