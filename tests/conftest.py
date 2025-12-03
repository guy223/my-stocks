"""
pytest 공통 픽스처 및 설정
"""

import pytest
import pandas as pd
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# src 디렉토리를 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Base
from database.connection import Database


# ============================================================================
# 데이터베이스 픽스처
# ============================================================================

@pytest.fixture(scope="function")
def db_engine():
    """SQLite 인메모리 DB 엔진 생성"""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """테스트용 DB 세션"""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="function")
def test_database():
    """Database 인스턴스 (인메모리)"""
    db = Database(db_url='sqlite:///:memory:')
    db.create_tables()
    yield db
    db.drop_tables()


# ============================================================================
# 샘플 데이터 픽스처
# ============================================================================

@pytest.fixture
def sample_stock_data():
    """샘플 종목 데이터"""
    return {
        'ticker': '005930',
        'name': '삼성전자',
        'market': 'KOSPI'
    }


@pytest.fixture
def sample_ohlcv_df():
    """샘플 OHLCV DataFrame"""
    dates = pd.date_range('2024-01-01', periods=5, freq='D')
    return pd.DataFrame({
        '시가': [70000, 71000, 70500, 72000, 71500],
        '고가': [71000, 72000, 71500, 73000, 72500],
        '저가': [69500, 70500, 70000, 71500, 71000],
        '종가': [70500, 71500, 71000, 72500, 72000],
        '거래량': [10000000, 12000000, 11000000, 13000000, 12500000]
    }, index=dates)


@pytest.fixture
def sample_market_cap_df():
    """샘플 시가총액 DataFrame"""
    dates = pd.date_range('2024-01-01', periods=5, freq='D')
    return pd.DataFrame({
        '시가총액': [400000000000000, 410000000000000, 405000000000000,
                    415000000000000, 410000000000000],
        '거래량': [10000000, 12000000, 11000000, 13000000, 12500000],
        '거래대금': [705000000000, 858000000000, 781000000000,
                    942500000000, 900000000000],
        '상장주식수': [5969782550, 5969782550, 5969782550,
                      5969782550, 5969782550]
    }, index=dates)


@pytest.fixture
def sample_fundamental_df():
    """샘플 펀더멘탈 DataFrame (NULL 값 포함)"""
    dates = pd.date_range('2024-01-01', periods=5, freq='D')
    return pd.DataFrame({
        'BPS': [45000, 45100, 45050, 45200, 45150],
        'PER': [15.5, 15.8, 15.6, 16.0, 15.9],
        'PBR': [1.56, 1.58, 1.57, 1.60, 1.59],
        'EPS': [4500, 4510, 4505, 4520, 4515],
        'DIV': [2.5, 2.5, 2.5, 2.5, 2.5],
        'DPS': [1500, 1500, 1500, 1500, 1500]
    }, index=dates)


@pytest.fixture
def sample_trading_df():
    """샘플 투자자별 매매 DataFrame"""
    dates = pd.date_range('2024-01-01', periods=5, freq='D')
    return pd.DataFrame({
        '기관합계': [100000000, -50000000, 75000000, -25000000, 50000000],
        '외국인합계': [200000000, 150000000, -100000000, 250000000, 175000000],
        '개인': [-300000000, -100000000, 25000000, -225000000, -225000000],
        '금융투자': [50000000, -25000000, 40000000, -10000000, 30000000],
        '보험': [20000000, 10000000, 15000000, 5000000, 12000000],
        '투신': [15000000, -5000000, 10000000, -3000000, 8000000],
        '사모': [10000000, -15000000, 5000000, -8000000, 3000000],
        '연기금': [5000000, -15000000, 5000000, 1000000, -3000000]
    }, index=dates)


@pytest.fixture
def sample_short_selling_df():
    """샘플 공매도 거래량 DataFrame"""
    dates = pd.date_range('2024-01-01', periods=5, freq='D')
    return pd.DataFrame({
        '거래량': [500000, 450000, 480000, 520000, 490000],
        '거래대금': [35250000000, 32175000000, 34080000000,
                    37700000000, 35280000000]
    }, index=dates)


@pytest.fixture
def sample_short_balance_df():
    """샘플 공매도 잔고 DataFrame"""
    dates = pd.date_range('2024-01-01', periods=5, freq='D')
    return pd.DataFrame({
        '잔고수량': [2000000, 2050000, 2025000, 2100000, 2075000],
        '잔고금액': [141000000000, 146525000000, 143775000000,
                    152250000000, 149400000000],
        '잔고비율': [0.34, 0.34, 0.34, 0.35, 0.35]
    }, index=dates)


@pytest.fixture
def empty_dataframe():
    """빈 DataFrame"""
    return pd.DataFrame()


# ============================================================================
# 날짜 픽스처
# ============================================================================

@pytest.fixture
def weekday_date():
    """평일 날짜 문자열 (수요일)"""
    return '20240103'


@pytest.fixture
def weekend_date():
    """주말 날짜 문자열 (토요일)"""
    return '20240106'


# ============================================================================
# Mock 픽스처
# ============================================================================

@pytest.fixture(autouse=True)
def mock_time_sleep(mocker):
    """time.sleep mock (자동 적용 - 테스트 속도 향상)"""
    return mocker.patch('time.sleep', return_value=None)
