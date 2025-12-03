"""
KRXClient 클래스 테스트
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from krx.client import KRXClient


class TestKRXClient:
    """KRXClient 클래스 테스트"""

    def test_init(self, db_session):
        """클라이언트 초기화"""
        client = KRXClient(db_session)
        assert client.session == db_session
        assert client.last_api_call is None

    def test_wait_for_rate_limit_first_call(self, db_session):
        """첫 API 호출 시 대기 없음"""
        client = KRXClient(db_session)
        # time.sleep는 conftest.py의 autouse fixture에서 이미 mock됨
        client._wait_for_rate_limit()
        assert client.last_api_call is not None

    def test_wait_for_rate_limit_updates_last_call_time(self, db_session):
        """rate limit 호출 시 마지막 호출 시간 업데이트"""
        client = KRXClient(db_session)

        # 첫 호출
        assert client.last_api_call is None
        client._wait_for_rate_limit()

        # 마지막 호출 시간이 설정됨
        assert client.last_api_call is not None
        first_call_time = client.last_api_call

        # 두 번째 호출
        client._wait_for_rate_limit()
        second_call_time = client.last_api_call

        # 시간이 업데이트됨
        assert second_call_time >= first_call_time

    def test_retry_on_error_success_first_try(self, db_session):
        """첫 시도에서 성공"""
        client = KRXClient(db_session)
        mock_func = MagicMock(return_value="성공")

        result = client._retry_on_error(mock_func, "arg1", kwarg1="kwarg1")

        assert result == "성공"
        assert mock_func.call_count == 1
        mock_func.assert_called_with("arg1", kwarg1="kwarg1")

    def test_retry_on_error_success_second_try(self, db_session):
        """두 번째 시도에서 성공"""
        client = KRXClient(db_session)
        mock_func = MagicMock(__name__='test_func')

        # 첫 번째 실패, 두 번째 성공
        mock_func.side_effect = [Exception("첫 번째 실패"), "성공"]

        result = client._retry_on_error(mock_func)

        assert result == "성공"
        assert mock_func.call_count == 2  # 두 번 호출됨

    def test_retry_on_error_max_retries_exceeded(self, db_session):
        """최대 재시도 횟수 초과"""
        client = KRXClient(db_session)
        mock_func = MagicMock(__name__='test_func', side_effect=Exception("항상 실패"))

        with pytest.raises(Exception, match="항상 실패"):
            client._retry_on_error(mock_func)

        assert mock_func.call_count == client.MAX_RETRIES  # MAX_RETRIES(3)번 시도

    def test_get_ohlcv_success(self, db_session, mocker, sample_ohlcv_df, weekday_date):
        """OHLCV 조회 성공"""
        mock_stock = mocker.patch('krx.client.stock')
        mock_stock.get_market_ohlcv.return_value = sample_ohlcv_df

        client = KRXClient(db_session)
        result = client.get_ohlcv('005930', weekday_date, weekday_date)

        assert not result.empty
        assert len(result) == 5
        mock_stock.get_market_ohlcv.assert_called_once()

    def test_get_ohlcv_with_retry(self, db_session, mocker, sample_ohlcv_df, weekday_date):
        """OHLCV 조회 재시도 후 성공"""
        mock_sleep = mocker.patch('krx.client.time.sleep')
        mock_stock = mocker.patch('krx.client.stock')

        # 첫 시도 실패, 두 번째 성공
        mock_stock.get_market_ohlcv.side_effect = [
            Exception("네트워크 오류"),
            sample_ohlcv_df
        ]

        client = KRXClient(db_session)
        result = client.get_ohlcv('005930', weekday_date, weekday_date)

        assert not result.empty
        assert mock_stock.get_market_ohlcv.call_count == 2
        assert mock_sleep.call_count >= 1  # 재시도 전 대기

    def test_get_market_cap_success(self, db_session, mocker, sample_market_cap_df, weekday_date):
        """시가총액 조회 성공"""
        mock_stock = mocker.patch('krx.client.stock')
        mock_stock.get_market_cap.return_value = sample_market_cap_df

        client = KRXClient(db_session)
        result = client.get_market_cap('005930', weekday_date, weekday_date)

        assert not result.empty
        assert '시가총액' in result.columns
        mock_stock.get_market_cap.assert_called_once()

    def test_get_fundamental_success(self, db_session, mocker, sample_fundamental_df, weekday_date):
        """펀더멘탈 조회 성공"""
        mock_stock = mocker.patch('krx.client.stock')
        mock_stock.get_market_fundamental.return_value = sample_fundamental_df

        client = KRXClient(db_session)
        result = client.get_fundamental('005930', weekday_date, weekday_date)

        assert not result.empty
        assert 'PER' in result.columns
        assert 'PBR' in result.columns
        mock_stock.get_market_fundamental.assert_called_once()

    def test_get_trading_by_investor_success(self, db_session, mocker, sample_trading_df, weekday_date):
        """투자자별 매매 조회 성공"""
        mock_stock = mocker.patch('krx.client.stock')
        mock_stock.get_market_trading_value_by_date.return_value = sample_trading_df

        client = KRXClient(db_session)
        result = client.get_trading_by_investor('005930', weekday_date, weekday_date)

        assert not result.empty
        assert '외국인합계' in result.columns
        assert '기관합계' in result.columns
        mock_stock.get_market_trading_value_by_date.assert_called_once()

    def test_get_short_selling_volume_success(self, db_session, mocker, sample_short_selling_df, weekday_date):
        """공매도 거래량 조회 성공"""
        mock_stock = mocker.patch('krx.client.stock')
        mock_stock.get_shorting_volume_by_date.return_value = sample_short_selling_df

        client = KRXClient(db_session)
        result = client.get_short_selling_volume('005930', weekday_date, weekday_date)

        assert not result.empty
        assert '거래량' in result.columns
        mock_stock.get_shorting_volume_by_date.assert_called_once()

    def test_get_short_selling_volume_failure_returns_empty(self, db_session, mocker, weekday_date):
        """공매도 거래량 조회 실패 시 빈 DataFrame 반환"""
        mock_stock = mocker.patch('krx.client.stock')
        mock_stock.get_shorting_volume_by_date.side_effect = Exception("조회 실패")

        client = KRXClient(db_session)
        result = client.get_short_selling_volume('005930', weekday_date, weekday_date)

        assert result.empty
        # 예외를 포착하고 빈 DataFrame 반환해야 함

    def test_get_short_balance_success(self, db_session, mocker, sample_short_balance_df, weekday_date):
        """공매도 잔고 조회 성공"""
        mock_stock = mocker.patch('krx.client.stock')
        mock_stock.get_shorting_balance_by_date.return_value = sample_short_balance_df

        client = KRXClient(db_session)
        result = client.get_short_balance('005930', weekday_date, weekday_date)

        assert not result.empty
        assert '잔고수량' in result.columns
        assert '잔고비율' in result.columns
        mock_stock.get_shorting_balance_by_date.assert_called_once()

    def test_get_short_balance_failure_returns_empty(self, db_session, mocker, weekday_date):
        """공매도 잔고 조회 실패 시 빈 DataFrame 반환"""
        mock_stock = mocker.patch('krx.client.stock')
        mock_stock.get_shorting_balance_by_date.side_effect = Exception("조회 실패")

        client = KRXClient(db_session)
        result = client.get_short_balance('005930', weekday_date, weekday_date)

        assert result.empty
        # 예외를 포착하고 빈 DataFrame 반환해야 함
