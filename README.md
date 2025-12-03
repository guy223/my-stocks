# My Stocks - 주식 투자 분석 프로젝트

효과적인 주식 투자를 위한 KRX 시장 동향 분석 및 자동 리포트 생성 시스템

## 📊 프로젝트 소개

한국거래소(KRX)의 주식 시장 데이터를 자동 수집하고, 시장 동향을 분석하여 일일 투자 리포트를 생성하는 시스템입니다. PyKrx 라이브러리를 활용하여 KOSPI/KOSDAQ 시장의 실시간 데이터를 수집하고, SQLite 데이터베이스에 체계적으로 저장합니다.

## ✨ 핵심 기능

### 1. 종합 데이터 수집 시스템
- **PyKrx 기반 KRX 데이터 수집**
  - 일별 주가 데이터 (OHLCV: 시가, 고가, 저가, 종가, 거래량)
  - 시가총액 및 거래 정보 (거래량, 거래대금, 상장주식수)
  - 펀더멘탈 지표 (BPS, PER, PBR, EPS, DIV, DPS)
  - 투자자별 매매 동향 (기관, 외국인, 개인, 금융투자, 보험, 투신, 사모, 연기금)
  - 공매도 데이터 (거래량, 거래대금)
  - 공매도 잔고 (잔고수량, 잔고금액, 잔고비율)

- **안정적인 데이터 수집 메커니즘**
  - API 요청 간 1초 딜레이 (KRX 서버 차단 방지)
  - 최대 3회 재시도 로직 (5초 간격)
  - 중복 데이터 자동 스킵 (UNIQUE 제약조건)

### 2. 시장 동향 분석
- **KOSPI/KOSDAQ 지수 분석**
  - 당일 종가 및 전일 대비 변동폭
  - 등락률 계산
  - 거래량 정보

- **주요 종목 동향**
  - 급등 상위 5종목 (등락률 기준)
  - 급락 상위 5종목 (등락률 기준)
  - 거래대금 상위 5종목
  - 외국인 순매수 상위 종목

### 3. 일일 투자 리포트 자동 생성
종합적인 시장 분석 리포트를 자동으로 생성합니다.

#### 리포트 구성 내용

**📊 시장 개황**
```
▶ KOSPI: 4,044 (+49.25, +1.23%)
  거래량: 227,130,503

▶ KOSDAQ: 930 (+1.16, +0.12%)
  거래량: 664,646,402
```

**📈 KOSPI/KOSDAQ 주요 동향**
- 급등 상위 5종목 (종목명, 종가, 등락률, 거래량)
- 급락 상위 5종목 (종목명, 종가, 등락률, 거래량)
- 거래대금 상위 5종목 (종목명, 종가, 등락률, 거래대금)

**⭐ 관심 종목 분석**
```
▶ HD현대일렉트릭 (267260)
  종가: 503,000원  등락률: +1.21%  거래량: 148,943
  외국인 순매수 (최근 5일):
    2025-12-03: 15.2억
    2025-12-02: -8.5억
    ...
  펀더멘탈: PER 15.32  PBR 2.45  EPS 32,850원
```

### 4. 데이터 관리 시스템
- **SQLite 데이터베이스**
  - 7개 정규화된 테이블 구조
  - stocks, daily_price, market_cap, fundamental, trading_by_investor, short_selling, short_balance
  - ticker + date 복합 인덱스로 조회 성능 최적화

- **SQLAlchemy ORM**
  - 타입 안전성 보장
  - Context manager로 세션 안전 관리
  - 자동 테이블 생성 및 마이그레이션

## 🚀 시작하기

### 필수 요구사항

- Python 3.10 이상
- uv (Python 패키지 관리자)

### 설치

```bash
# 저장소 클론
git clone <repository-url>
cd my-stocks

# uv로 의존성 설치
uv sync
```

### 환경 설정

환경 변수 파일 설정 (필요시):

```bash
cp .env.example .env
```

## 📖 사용 방법

### 1. 데이터 수집

특정 종목의 과거 데이터를 수집합니다.

```bash
# 메인 스크립트 실행 (HD현대일렉트릭, 현대로템 1년치 데이터 수집)
uv run src/main.py
```

**수집되는 데이터**:
- 최근 1년간의 일별 주가 (OHLCV)
- 시가총액 및 거래 정보
- 펀더멘탈 지표
- 투자자별 매매 동향
- 공매도 데이터 및 잔고

### 2. 일일 리포트 생성

시장 동향 및 관심 종목 분석 리포트를 생성합니다.

```bash
# 오늘 날짜로 리포트 생성
uv run examples/generate_daily_report.py

# 특정 날짜로 리포트 생성 (YYYYMMDD)
uv run examples/generate_daily_report.py 20251203
```

**생성되는 리포트**:
- 콘솔에 실시간 출력
- `reports/` 디렉토리에 텍스트 파일로 자동 저장
- 파일명 형식: `daily_report_YYYYMMDD_HHMMSS.txt`

### 3. 데이터 조회 예제

저장된 데이터를 조회하는 예제를 실행합니다.

```bash
# 데이터 조회 예제 실행
uv run examples/query_example.py
```

## 📁 프로젝트 구조

```
my-stocks/
├── src/                           # 소스 코드
│   ├── models/                   # SQLAlchemy 데이터 모델
│   │   ├── __init__.py          # 모델 통합 export
│   │   ├── stock.py             # Stock 모델 (종목 기본 정보)
│   │   ├── daily_price.py       # DailyPrice 모델 (일별 주가 OHLCV)
│   │   ├── market_cap.py        # MarketCap 모델 (시가총액)
│   │   ├── fundamental.py       # Fundamental 모델 (펀더멘탈 지표)
│   │   ├── trading_by_investor.py  # TradingByInvestor 모델 (투자자 매매)
│   │   ├── short_selling.py     # ShortSelling 모델 (공매도)
│   │   └── short_balance.py     # ShortBalance 모델 (공매도 잔고)
│   │
│   ├── database/                # 데이터베이스 관리
│   │   ├── connection.py        # Database 클래스 (SQLite 연결 및 세션)
│   │   └── queries.py           # StockQueries 클래스 (데이터 조회)
│   │
│   ├── krx/                     # KRX 데이터 수집
│   │   ├── client.py            # KRXClient 클래스 (PyKrx API 래퍼)
│   │   └── saver.py             # DataSaver 클래스 (데이터 저장)
│   │
│   ├── analysis/                # 시장 분석
│   │   └── market_summary.py    # MarketSummary 클래스 (시장 동향 분석)
│   │
│   ├── report/                  # 리포트 생성
│   │   └── daily_report.py      # DailyReport 클래스 (일일 리포트)
│   │
│   └── main.py                  # 메인 실행 스크립트 (데이터 수집)
│
├── examples/                    # 실행 예제
│   ├── query_example.py         # 데이터 조회 예제
│   └── generate_daily_report.py # 일일 리포트 생성 스크립트
│
├── data/                        # 데이터 저장소
│   └── stocks.db               # SQLite 데이터베이스 파일
│
├── reports/                     # 생성된 리포트 저장 디렉토리
│   └── daily_report_*.txt      # 일일 리포트 파일들
│
├── tests/                       # 테스트 코드
│   └── test_krx_client.py      # KRX 클라이언트 테스트
│
├── .env.example                # 환경 변수 예시
├── .gitignore                  # Git 제외 파일
├── pyproject.toml              # uv 프로젝트 설정 및 의존성
├── CLAUDE.md                   # Claude Code 개발 가이드
└── README.md                   # 프로젝트 문서
```

## 🔧 기술 스택

### 주요 라이브러리

- **PyKrx** (v1.0.46+): 한국거래소 데이터 수집
- **SQLAlchemy** (v2.0.0+): ORM 및 데이터베이스 관리
- **Pandas** (v2.0.0+): 데이터 처리 및 분석
- **uv**: Python 패키지 관리자

### 데이터베이스 스키마

**7개 테이블 구조**:

1. **stocks** - 종목 기본 정보
   - PK: ticker
   - 컬럼: name, market, created_at, updated_at

2. **daily_price** - 일별 주가 (OHLCV)
   - UNIQUE: ticker + date
   - 컬럼: open, high, low, close, volume

3. **market_cap** - 시가총액 및 거래 정보
   - UNIQUE: ticker + date
   - 컬럼: market_cap, trading_volume, trading_value, outstanding_shares

4. **fundamental** - 펀더멘탈 지표
   - UNIQUE: ticker + date
   - 컬럼: bps, per, pbr, eps, div, dps

5. **trading_by_investor** - 투자자별 매매 동향
   - UNIQUE: ticker + date
   - 컬럼: institution_net, foreigner_net, individual_net, financial_net, insurance_net, trust_net, private_equity_net, pension_net

6. **short_selling** - 공매도 거래
   - UNIQUE: ticker + date
   - 컬럼: short_volume, short_value

7. **short_balance** - 공매도 잔고
   - UNIQUE: ticker + date
   - 컬럼: balance_quantity, balance_value, balance_ratio

## 📈 데이터 소스

- **KRX (한국거래소)**: PyKrx 라이브러리를 통한 데이터 수집
  - KOSPI 시장 데이터
  - KOSDAQ 시장 데이터
  - 주가, 시가총액, 펀더멘탈, 투자자 매매, 공매도 정보

## 🔍 주요 구현 특징

### 1. 안정적인 API 호출 메커니즘
```python
# KRX 서버 차단 방지를 위한 딜레이
time.sleep(1)

# 재시도 로직
for attempt in range(max_retries):
    try:
        data = stock.get_market_ohlcv(...)
        break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
```

### 2. 중복 데이터 자동 처리
```python
# UNIQUE 제약조건으로 중복 방지
try:
    session.add(price)
    session.commit()
except IntegrityError:
    session.rollback()  # 중복 데이터 스킵
```

### 3. Context Manager 기반 세션 관리
```python
with db.get_session() as session:
    stocks = StockQueries.get_all_stocks(session)
    # 세션 자동 종료
```

## 📊 실행 결과 예시

### 데이터 수집 결과
```
HD현대일렉트릭(267260) 데이터 수집 완료
- 일별 주가: 243건
- 시가총액: 243건
- 펀더멘탈: 243건
- 투자자별 매매: 242건
- 공매도: 243건
- 공매도 잔고: 240건
```

### 일일 리포트 샘플
리포트는 다음 섹션들로 구성됩니다:

1. **시장 개황**: KOSPI/KOSDAQ 지수 및 전일대비 변동
2. **KOSPI 주요 동향**: 급등/급락/거래대금 상위 5종목
3. **KOSDAQ 주요 동향**: 급등/급락/거래대금 상위 5종목
4. **관심 종목 분석**: 등록된 종목의 주가, 외국인 매매, 펀더멘탈

생성된 리포트는 `reports/` 디렉토리에 자동 저장됩니다.

## ⚙️ 개발 가이드

### 새로운 종목 추가

[src/main.py](src/main.py)에서 종목 정보를 추가합니다:

```python
stocks = [
    ("267260", "HD현대일렉트릭", "KOSPI"),
    ("064350", "현대로템", "KOSPI"),
    # 새로운 종목 추가
    ("005930", "삼성전자", "KOSPI"),
]
```

### 데이터 조회 쿼리 작성

```python
from database.connection import Database
from database.queries import StockQueries

with Database().get_session() as session:
    # 최근 주가 조회
    latest = StockQueries.get_latest_price(session, "267260")

    # 날짜 범위 조회
    prices = StockQueries.get_daily_prices(
        session, "267260",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31)
    )
```

## 📝 주의사항

### API 사용 제한
- KRX 서버 차단 방지를 위해 **요청 간 1초 이상 딜레이 필수**
- 장기간 데이터 조회 시 타임아웃 가능 (1년 단위 권장)
- **당일 데이터는 장 마감 후 약 18:00 이후 제공**

### 데이터 품질
- 펀더멘탈 지표는 상장 초기 종목의 경우 NULL 가능
- 주말 및 공휴일 데이터는 제공되지 않음
- 거래 정지 종목은 데이터 누락 가능

## ⚠️ 면책 조항

본 프로젝트는 투자 분석을 위한 도구이며, 제공되는 정보는 투자 권유가 아닙니다.
모든 투자 결정은 본인의 책임 하에 이루어져야 합니다.
