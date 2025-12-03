"""
StockQueries 클래스 테스트
"""

import pytest
from datetime import date, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from database.queries import StockQueries
from models import Stock, DailyPrice, MarketCap, Fundamental, TradingByInvestor


class TestStockQueries:
    """StockQueries 클래스 테스트"""

    def test_get_stock_exists(self, db_session, sample_stock_data):
        """종목 조회 - 존재하는 경우"""
        # 종목 추가
        stock = Stock(**sample_stock_data)
        db_session.add(stock)
        db_session.commit()

        # 조회
        result = StockQueries.get_stock(db_session, sample_stock_data['ticker'])

        assert result is not None
        assert result.ticker == sample_stock_data['ticker']
        assert result.name == sample_stock_data['name']
        assert result.market == sample_stock_data['market']

    def test_get_stock_not_exists(self, db_session):
        """종목 조회 - 존재하지 않는 경우"""
        result = StockQueries.get_stock(db_session, '999999')
        assert result is None

    def test_get_all_stocks(self, db_session):
        """전체 종목 조회"""
        # 여러 종목 추가
        stocks = [
            Stock(ticker='005930', name='삼성전자', market='KOSPI'),
            Stock(ticker='000660', name='SK하이닉스', market='KOSPI'),
            Stock(ticker='035420', name='NAVER', market='KOSPI')
        ]
        for stock in stocks:
            db_session.add(stock)
        db_session.commit()

        # 조회
        result = StockQueries.get_all_stocks(db_session)

        assert len(result) == 3
        tickers = [s.ticker for s in result]
        assert '005930' in tickers
        assert '000660' in tickers
        assert '035420' in tickers

    def test_get_all_stocks_empty(self, db_session):
        """전체 종목 조회 - 빈 결과"""
        result = StockQueries.get_all_stocks(db_session)
        assert len(result) == 0

    def test_get_daily_prices_no_filter(self, db_session, sample_stock_data):
        """일별 주가 조회 - 필터 없음"""
        # 종목 추가
        stock = Stock(**sample_stock_data)
        db_session.add(stock)
        db_session.commit()

        # 주가 데이터 추가
        dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
        for d in dates:
            price = DailyPrice(
                ticker=sample_stock_data['ticker'],
                date=d,
                open=70000, high=71000, low=69000, close=70500, volume=1000000
            )
            db_session.add(price)
        db_session.commit()

        # 조회
        result = StockQueries.get_daily_prices(db_session, sample_stock_data['ticker'])

        assert len(result) == 3
        # 날짜 오름차순 정렬 확인
        assert result[0].date == date(2024, 1, 1)
        assert result[2].date == date(2024, 1, 3)

    def test_get_daily_prices_start_date_filter(self, db_session, sample_stock_data):
        """일별 주가 조회 - 시작일 필터"""
        # 종목 추가
        stock = Stock(**sample_stock_data)
        db_session.add(stock)
        db_session.commit()

        # 주가 데이터 추가
        dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
        for d in dates:
            price = DailyPrice(
                ticker=sample_stock_data['ticker'],
                date=d,
                open=70000, high=71000, low=69000, close=70500, volume=1000000
            )
            db_session.add(price)
        db_session.commit()

        # 조회 (2024-01-02 이후)
        result = StockQueries.get_daily_prices(
            db_session,
            sample_stock_data['ticker'],
            start_date=date(2024, 1, 2)
        )

        assert len(result) == 2
        assert result[0].date == date(2024, 1, 2)
        assert result[1].date == date(2024, 1, 3)

    def test_get_daily_prices_end_date_filter(self, db_session, sample_stock_data):
        """일별 주가 조회 - 종료일 필터"""
        # 종목 추가
        stock = Stock(**sample_stock_data)
        db_session.add(stock)
        db_session.commit()

        # 주가 데이터 추가
        dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
        for d in dates:
            price = DailyPrice(
                ticker=sample_stock_data['ticker'],
                date=d,
                open=70000, high=71000, low=69000, close=70500, volume=1000000
            )
            db_session.add(price)
        db_session.commit()

        # 조회 (2024-01-02 이전)
        result = StockQueries.get_daily_prices(
            db_session,
            sample_stock_data['ticker'],
            end_date=date(2024, 1, 2)
        )

        assert len(result) == 2
        assert result[0].date == date(2024, 1, 1)
        assert result[1].date == date(2024, 1, 2)

    def test_get_daily_prices_date_range_filter(self, db_session, sample_stock_data):
        """일별 주가 조회 - 날짜 범위 필터"""
        # 종목 추가
        stock = Stock(**sample_stock_data)
        db_session.add(stock)
        db_session.commit()

        # 주가 데이터 추가
        dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4), date(2024, 1, 5)]
        for d in dates:
            price = DailyPrice(
                ticker=sample_stock_data['ticker'],
                date=d,
                open=70000, high=71000, low=69000, close=70500, volume=1000000
            )
            db_session.add(price)
        db_session.commit()

        # 조회 (2024-01-02 ~ 2024-01-04)
        result = StockQueries.get_daily_prices(
            db_session,
            sample_stock_data['ticker'],
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 4)
        )

        assert len(result) == 3
        assert result[0].date == date(2024, 1, 2)
        assert result[2].date == date(2024, 1, 4)

    def test_get_daily_prices_empty_result(self, db_session, sample_stock_data):
        """일별 주가 조회 - 빈 결과"""
        # 종목만 추가 (주가 데이터 없음)
        stock = Stock(**sample_stock_data)
        db_session.add(stock)
        db_session.commit()

        result = StockQueries.get_daily_prices(db_session, sample_stock_data['ticker'])
        assert len(result) == 0

    def test_get_latest_price(self, db_session, sample_stock_data):
        """최근 주가 조회"""
        # 종목 추가
        stock = Stock(**sample_stock_data)
        db_session.add(stock)
        db_session.commit()

        # 주가 데이터 추가 (순서 무작위)
        dates = [date(2024, 1, 1), date(2024, 1, 3), date(2024, 1, 2)]
        closes = [70000, 72000, 71000]
        for d, c in zip(dates, closes):
            price = DailyPrice(
                ticker=sample_stock_data['ticker'],
                date=d,
                open=70000, high=71000, low=69000, close=c, volume=1000000
            )
            db_session.add(price)
        db_session.commit()

        # 조회
        result = StockQueries.get_latest_price(db_session, sample_stock_data['ticker'])

        assert result is not None
        assert result.date == date(2024, 1, 3)  # 가장 최근 날짜
        assert result.close == 72000

    def test_get_latest_price_not_exists(self, db_session):
        """최근 주가 조회 - 미존재"""
        result = StockQueries.get_latest_price(db_session, '999999')
        assert result is None

    def test_get_market_caps_with_filters(self, db_session, sample_stock_data):
        """시가총액 조회 - 필터 적용"""
        # 종목 추가
        stock = Stock(**sample_stock_data)
        db_session.add(stock)
        db_session.commit()

        # 시가총액 데이터 추가
        dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
        for d in dates:
            mcap = MarketCap(
                ticker=sample_stock_data['ticker'],
                date=d,
                market_cap=1000000000000,
                trading_volume=5000000,
                trading_value=350000000000,
                outstanding_shares=100000000
            )
            db_session.add(mcap)
        db_session.commit()

        # 조회 (날짜 범위)
        result = StockQueries.get_market_caps(
            db_session,
            sample_stock_data['ticker'],
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 3)
        )

        assert len(result) == 2
        assert result[0].date == date(2024, 1, 2)
        assert result[1].date == date(2024, 1, 3)

    def test_get_fundamentals_with_filters(self, db_session, sample_stock_data):
        """펀더멘탈 조회 - 필터 적용"""
        # 종목 추가
        stock = Stock(**sample_stock_data)
        db_session.add(stock)
        db_session.commit()

        # 펀더멘탈 데이터 추가
        dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
        for i, d in enumerate(dates):
            fund = Fundamental(
                ticker=sample_stock_data['ticker'],
                date=d,
                bps=50000 + i * 100,
                per=15.0 + i * 0.5,
                pbr=2.0 + i * 0.1,
                eps=3500 + i * 10,
                div=1.5,
                dps=1000
            )
            db_session.add(fund)
        db_session.commit()

        # 조회 (시작일만)
        result = StockQueries.get_fundamentals(
            db_session,
            sample_stock_data['ticker'],
            start_date=date(2024, 1, 2)
        )

        assert len(result) == 2
        assert result[0].per == 15.5  # 2024-01-02
        assert result[1].per == 16.0  # 2024-01-03

    def test_get_trading_by_investor_with_filters(self, db_session, sample_stock_data):
        """투자자별 매매 조회 - 필터 적용"""
        # 종목 추가
        stock = Stock(**sample_stock_data)
        db_session.add(stock)
        db_session.commit()

        # 투자자 매매 데이터 추가
        dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
        for d in dates:
            trading = TradingByInvestor(
                ticker=sample_stock_data['ticker'],
                date=d,
                institution_net=1000000,
                foreigner_net=2000000,
                individual_net=-3000000
            )
            db_session.add(trading)
        db_session.commit()

        # 조회 (종료일만)
        result = StockQueries.get_trading_by_investor(
            db_session,
            sample_stock_data['ticker'],
            end_date=date(2024, 1, 2)
        )

        assert len(result) == 2
        assert result[0].date == date(2024, 1, 1)
        assert result[1].date == date(2024, 1, 2)

    def test_get_foreign_net_buying_days_limit(self, db_session, sample_stock_data):
        """외국인 순매수 최근 N일 조회 - limit 확인"""
        # 종목 추가
        stock = Stock(**sample_stock_data)
        db_session.add(stock)
        db_session.commit()

        # 10일치 데이터 추가
        for i in range(10):
            trading = TradingByInvestor(
                ticker=sample_stock_data['ticker'],
                date=date(2024, 1, 1) + timedelta(days=i),
                institution_net=1000000,
                foreigner_net=2000000 + i * 100000,
                individual_net=-3000000
            )
            db_session.add(trading)
        db_session.commit()

        # 최근 5일 조회
        result = StockQueries.get_foreign_net_buying_days(
            db_session,
            sample_stock_data['ticker'],
            days=5
        )

        assert len(result) == 5
        # 최근 날짜부터 내림차순
        assert result[0].date == date(2024, 1, 10)  # 가장 최근
        assert result[4].date == date(2024, 1, 6)   # 5번째

    def test_delete_old_data(self, db_session, sample_stock_data):
        """오래된 데이터 삭제"""
        # 종목 추가
        stock = Stock(**sample_stock_data)
        db_session.add(stock)
        db_session.commit()

        # 주가 및 시가총액 데이터 추가
        dates = [date(2023, 12, 1), date(2023, 12, 15), date(2024, 1, 1), date(2024, 1, 15)]
        for d in dates:
            price = DailyPrice(
                ticker=sample_stock_data['ticker'],
                date=d,
                open=70000, high=71000, low=69000, close=70500, volume=1000000
            )
            db_session.add(price)

            mcap = MarketCap(
                ticker=sample_stock_data['ticker'],
                date=d,
                market_cap=1000000000000,
                trading_volume=5000000,
                trading_value=350000000000,
                outstanding_shares=100000000
            )
            db_session.add(mcap)
        db_session.commit()

        # 2024-01-01 이전 데이터 삭제
        deleted_count = StockQueries.delete_old_data(
            db_session,
            sample_stock_data['ticker'],
            before_date=date(2024, 1, 1)
        )

        # 주가 2건 + 시가총액 2건 = 4건 삭제
        assert deleted_count == 4

        # 남은 데이터 확인
        remaining_prices = db_session.query(DailyPrice).filter_by(
            ticker=sample_stock_data['ticker']
        ).all()
        assert len(remaining_prices) == 2  # 2024-01-01, 2024-01-15

        remaining_mcaps = db_session.query(MarketCap).filter_by(
            ticker=sample_stock_data['ticker']
        ).all()
        assert len(remaining_mcaps) == 2
