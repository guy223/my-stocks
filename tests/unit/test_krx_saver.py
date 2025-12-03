"""
DataSaver 클래스 테스트
"""

import pytest
import pandas as pd
from datetime import date
from sqlalchemy.exc import IntegrityError
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from krx.saver import DataSaver
from models import Stock, DailyPrice


class TestDataSaver:
    """DataSaver 클래스 테스트"""

    def test_init(self, db_session):
        """초기화"""
        saver = DataSaver(db_session)
        assert saver.session == db_session

    def test_save_stock_new_stock(self, db_session, sample_stock_data):
        """신규 종목 저장"""
        saver = DataSaver(db_session)
        result = saver.save_stock(**sample_stock_data)

        assert result is not None
        assert result.ticker == sample_stock_data['ticker']
        assert result.name == sample_stock_data['name']
        assert result.market == sample_stock_data['market']

        # DB에 저장 확인
        stock = db_session.query(Stock).filter_by(ticker=sample_stock_data['ticker']).first()
        assert stock is not None

    def test_save_stock_existing_stock(self, db_session, sample_stock_data):
        """기존 종목 조회 (중복 저장 시)"""
        saver = DataSaver(db_session)

        # 첫 저장
        first_save = saver.save_stock(**sample_stock_data)

        # 중복 저장 시도
        second_save = saver.save_stock(**sample_stock_data)

        # 동일한 객체 반환 (새로 생성 안 함)
        assert first_save.ticker == second_save.ticker
        assert first_save.name == second_save.name

        # DB에 1개만 존재
        count = db_session.query(Stock).filter_by(ticker=sample_stock_data['ticker']).count()
        assert count == 1

    def test_save_daily_prices_success(self, db_session, sample_stock_data, sample_ohlcv_df):
        """모든 행 저장 및 카운트 확인"""
        saver = DataSaver(db_session)
        saver.save_stock(**sample_stock_data)

        count = saver.save_daily_prices(sample_stock_data['ticker'], sample_ohlcv_df)

        assert count == 5  # 5개 행 모두 저장
        # DB 확인
        prices = db_session.query(DailyPrice).filter_by(ticker=sample_stock_data['ticker']).all()
        assert len(prices) == 5

    def test_save_daily_prices_empty_dataframe(self, db_session, sample_stock_data, empty_dataframe):
        """빈 DataFrame 처리 (0 반환)"""
        saver = DataSaver(db_session)
        saver.save_stock(**sample_stock_data)

        count = saver.save_daily_prices(sample_stock_data['ticker'], empty_dataframe)

        assert count == 0

    def test_save_daily_prices_duplicate_skip(self, db_session, sample_stock_data, sample_ohlcv_df):
        """IntegrityError 처리, 중복 스킵"""
        saver = DataSaver(db_session)
        saver.save_stock(**sample_stock_data)

        # 첫 저장
        first_count = saver.save_daily_prices(sample_stock_data['ticker'], sample_ohlcv_df)
        assert first_count == 5

        # 중복 저장 시도
        second_count = saver.save_daily_prices(sample_stock_data['ticker'], sample_ohlcv_df)
        assert second_count == 0  # 모두 스킵

        # DB에 여전히 5개만 존재
        prices = db_session.query(DailyPrice).filter_by(ticker=sample_stock_data['ticker']).all()
        assert len(prices) == 5

    def test_save_daily_prices_partial_duplicate(self, db_session, sample_stock_data, sample_ohlcv_df):
        """일부 중복 시 새로운 것만 저장"""
        saver = DataSaver(db_session)
        saver.save_stock(**sample_stock_data)

        # 첫 저장 (5개)
        saver.save_daily_prices(sample_stock_data['ticker'], sample_ohlcv_df)

        # 일부 중복 DataFrame 생성
        dates = pd.date_range('2024-01-01', periods=7, freq='D')  # 처음 5개는 중복, 뒤 2개는 신규
        partial_df = pd.DataFrame({
            '시가': [70000] * 7,
            '고가': [71000] * 7,
            '저가': [69500] * 7,
            '종가': [70500] * 7,
            '거래량': [10000000] * 7
        }, index=dates)

        count = saver.save_daily_prices(sample_stock_data['ticker'], partial_df)
        assert count == 2  # 신규 2개만 저장

        # DB에 총 7개 존재
        prices = db_session.query(DailyPrice).filter_by(ticker=sample_stock_data['ticker']).all()
        assert len(prices) == 7

    def test_save_market_caps_success(self, db_session, sample_stock_data, sample_market_cap_df):
        """시가총액 저장 성공"""
        saver = DataSaver(db_session)
        saver.save_stock(**sample_stock_data)

        count = saver.save_market_caps(sample_stock_data['ticker'], sample_market_cap_df)

        assert count == 5

    def test_save_fundamentals_success(self, db_session, sample_stock_data, sample_fundamental_df):
        """펀더멘탈 저장 성공"""
        saver = DataSaver(db_session)
        saver.save_stock(**sample_stock_data)

        count = saver.save_fundamentals(sample_stock_data['ticker'], sample_fundamental_df)

        assert count == 5

    def test_save_fundamentals_null_handling(self, db_session, sample_stock_data):
        """NULL 값 처리 (pd.notna() 체크)"""
        saver = DataSaver(db_session)
        saver.save_stock(**sample_stock_data)

        # NULL 값 포함 DataFrame
        dates = pd.date_range('2024-01-01', periods=2, freq='D')
        df_with_nulls = pd.DataFrame({
            'BPS': [45000, None],
            'PER': [15.5, None],
            'PBR': [1.56, None],
            'EPS': [4500, None],
            'DIV': [2.5, None],
            'DPS': [1500, None]
        }, index=dates)

        count = saver.save_fundamentals(sample_stock_data['ticker'], df_with_nulls)
        assert count == 2  # NULL 값도 저장됨 (None으로)

    def test_save_trading_by_investor_success(self, db_session, sample_stock_data, sample_trading_df):
        """투자자별 매매 저장 성공"""
        saver = DataSaver(db_session)
        saver.save_stock(**sample_stock_data)

        count = saver.save_trading_by_investor(sample_stock_data['ticker'], sample_trading_df)

        assert count == 5

    def test_save_trading_by_investor_missing_columns(self, db_session, sample_stock_data):
        """누락된 컬럼 처리 ('in row' 체크)"""
        saver = DataSaver(db_session)
        saver.save_stock(**sample_stock_data)

        # 일부 컬럼만 있는 DataFrame
        dates = pd.date_range('2024-01-01', periods=2, freq='D')
        df_partial = pd.DataFrame({
            '외국인합계': [200000000, 150000000],
            '개인': [-300000000, -100000000]
            # 다른 컬럼들은 없음
        }, index=dates)

        count = saver.save_trading_by_investor(sample_stock_data['ticker'], df_partial)
        assert count == 2  # 누락된 컬럼은 None으로 저장

    def test_save_short_selling_success(self, db_session, sample_stock_data, sample_short_selling_df):
        """공매도 저장 성공"""
        saver = DataSaver(db_session)
        saver.save_stock(**sample_stock_data)

        count = saver.save_short_selling(sample_stock_data['ticker'], sample_short_selling_df)

        assert count == 5

    def test_save_short_balance_success(self, db_session, sample_stock_data, sample_short_balance_df):
        """공매도 잔고 저장 성공"""
        saver = DataSaver(db_session)
        saver.save_stock(**sample_stock_data)

        count = saver.save_short_balance(sample_stock_data['ticker'], sample_short_balance_df)

        assert count == 5

    def test_transaction_isolation(self, db_session, sample_stock_data):
        """행별 개별 commit, 트랜잭션 격리"""
        saver = DataSaver(db_session)
        saver.save_stock(**sample_stock_data)

        # 일부 행만 유효한 DataFrame
        dates = pd.date_range('2024-01-01', periods=3, freq='D')
        df = pd.DataFrame({
            '시가': [70000, 71000, 70500],
            '고가': [71000, 72000, 71500],
            '저가': [69500, 70500, 70000],
            '종가': [70500, 71500, 71000],
            '거래량': [10000000, 12000000, 11000000]
        }, index=dates)

        # 첫 저장
        count1 = saver.save_daily_prices(sample_stock_data['ticker'], df)
        assert count1 == 3

        # 중간 행만 중복인 경우
        dates2 = pd.date_range('2024-01-02', periods=3, freq='D')
        df2 = pd.DataFrame({
            '시가': [71000, 70500, 72000],
            '고가': [72000, 71500, 73000],
            '저가': [70500, 70000, 71500],
            '종가': [71500, 71000, 72500],
            '거래량': [12000000, 11000000, 13000000]
        }, index=dates2)

        # 일부 중복 저장 시도
        count2 = saver.save_daily_prices(sample_stock_data['ticker'], df2)
        # 2024-01-02, 01-03은 중복, 01-04만 신규 (1개)
        assert count2 == 1

        # 총 4개 행 존재 (3 + 1)
        total = db_session.query(DailyPrice).filter_by(ticker=sample_stock_data['ticker']).count()
        assert total == 4
