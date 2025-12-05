#!/usr/bin/env python3
"""
data_fetcher 모듈 단위 테스트

관심 종목 데이터 수집 로직 테스트:
- check_data_exists: 데이터 존재 여부 확인
- fetch_stock_data: 개별 종목 데이터 수집
- fetch_watchlist_data: 관심 종목 배치 수집
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch
import pandas as pd

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_fetcher import check_data_exists, fetch_stock_data, fetch_watchlist_data


class TestCheckDataExists:
    """check_data_exists 함수 테스트"""

    def test_data_exists_returns_true(self, mocker):
        """데이터가 존재하면 True 반환"""
        # Given: 특정 날짜의 데이터가 존재하는 상황
        mock_latest_price = Mock()
        mock_latest_price.date = datetime(2025, 12, 4).date()

        mock_session = MagicMock()
        mock_queries = mocker.patch('data_fetcher.StockQueries')
        mock_queries.get_latest_price.return_value = mock_latest_price

        mock_db = mocker.patch('data_fetcher.Database')
        mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session

        # When: 동일한 날짜로 확인
        result = check_data_exists("000001", "20251204")

        # Then: True 반환
        assert result is True
        mock_queries.get_latest_price.assert_called_once_with(mock_session, "000001")

    def test_data_not_exists_returns_false(self, mocker):
        """데이터가 없으면 False 반환"""
        # Given: 데이터가 없는 상황
        mock_session = MagicMock()
        mock_queries = mocker.patch('data_fetcher.StockQueries')
        mock_queries.get_latest_price.return_value = None

        mock_db = mocker.patch('data_fetcher.Database')
        mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session

        # When
        result = check_data_exists("000001", "20251204")

        # Then
        assert result is False

    def test_data_exists_different_date_returns_false(self, mocker):
        """다른 날짜의 데이터가 있으면 False 반환"""
        # Given: 다른 날짜의 데이터만 존재
        mock_latest_price = Mock()
        mock_latest_price.date = datetime(2025, 12, 3).date()

        mock_session = MagicMock()
        mock_queries = mocker.patch('data_fetcher.StockQueries')
        mock_queries.get_latest_price.return_value = mock_latest_price

        mock_db = mocker.patch('data_fetcher.Database')
        mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session

        # When: 다른 날짜로 확인
        result = check_data_exists("000001", "20251204")

        # Then: False 반환
        assert result is False

    def test_invalid_date_format_raises_error(self):
        """잘못된 날짜 포맷은 ValueError 발생"""
        # When/Then
        with pytest.raises(ValueError):
            check_data_exists("000001", "2025-12-04")  # 잘못된 포맷

        with pytest.raises(ValueError):
            check_data_exists("000001", "20251332")  # 존재하지 않는 날짜


class TestFetchStockData:
    """fetch_stock_data 함수 테스트"""

    @pytest.fixture
    def mock_components(self, mocker):
        """공통 모킹 컴포넌트"""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_saver = MagicMock()

        # Database, KRXClient, DataSaver 모킹
        mock_db = mocker.patch('data_fetcher.Database')
        mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session

        mocker.patch('data_fetcher.KRXClient', return_value=mock_client)
        mocker.patch('data_fetcher.DataSaver', return_value=mock_saver)

        return {
            'session': mock_session,
            'client': mock_client,
            'saver': mock_saver
        }

    def test_fetch_mode_today(self, mock_components, mocker):
        """today 모드: 당일 데이터만 수집"""
        # Given
        client = mock_components['client']
        saver = mock_components['saver']

        # 빈 DataFrame 반환 (날짜 범위만 확인하므로)
        client.get_ohlcv.return_value = pd.DataFrame()
        client.get_market_cap.return_value = pd.DataFrame()
        client.get_fundamental.return_value = pd.DataFrame()
        client.get_trading_by_investor.return_value = pd.DataFrame()
        client.get_short_selling_volume.return_value = pd.DataFrame()
        client.get_short_balance.return_value = pd.DataFrame()

        # When
        result = fetch_stock_data("000001", "테스트종목", "KOSPI", "20251204", "today")

        # Then: start_date == end_date
        assert result['success'] is True
        assert result['ticker'] == "000001"
        # today 모드이므로 동일한 날짜로 호출
        client.get_ohlcv.assert_called_once_with("000001", "20251204", "20251204")

    def test_fetch_mode_recent_5days(self, mock_components):
        """recent 모드: 최근 5일 데이터 수집"""
        # Given
        client = mock_components['client']

        # 빈 DataFrame 반환
        for method in ['get_ohlcv', 'get_market_cap', 'get_fundamental',
                       'get_trading_by_investor', 'get_short_selling_volume',
                       'get_short_balance']:
            getattr(client, method).return_value = pd.DataFrame()

        # When
        result = fetch_stock_data("000001", "테스트종목", "KOSPI", "20251204", "recent")

        # Then: 5일 전부터 수집
        assert result['success'] is True
        client.get_ohlcv.assert_called_once_with("000001", "20251129", "20251204")

    def test_fetch_mode_month_30days(self, mock_components):
        """month 모드: 최근 30일 데이터 수집"""
        # Given
        client = mock_components['client']

        for method in ['get_ohlcv', 'get_market_cap', 'get_fundamental',
                       'get_trading_by_investor', 'get_short_selling_volume',
                       'get_short_balance']:
            getattr(client, method).return_value = pd.DataFrame()

        # When
        result = fetch_stock_data("000001", "테스트종목", "KOSPI", "20251204", "month")

        # Then: 30일 전부터 수집
        assert result['success'] is True
        client.get_ohlcv.assert_called_once_with("000001", "20251104", "20251204")

    def test_all_data_types_success(self, mock_components):
        """모든 데이터 타입 수집 성공"""
        # Given
        client = mock_components['client']
        saver = mock_components['saver']

        # 모든 데이터가 있는 DataFrame 반환
        sample_df = pd.DataFrame({'col1': [1, 2, 3]})
        client.get_ohlcv.return_value = sample_df
        client.get_market_cap.return_value = sample_df
        client.get_fundamental.return_value = sample_df
        client.get_trading_by_investor.return_value = sample_df
        client.get_short_selling_volume.return_value = sample_df
        client.get_short_balance.return_value = sample_df

        # saver는 저장 건수 반환
        saver.save_daily_prices.return_value = 3
        saver.save_market_caps.return_value = 3
        saver.save_fundamentals.return_value = 3
        saver.save_trading_by_investor.return_value = 3
        saver.save_short_selling.return_value = 3
        saver.save_short_balance.return_value = 3

        # When
        result = fetch_stock_data("000001", "테스트종목", "KOSPI", "20251204", "today")

        # Then
        assert result['success'] is True
        assert result['counts']['daily_price'] == 3
        assert result['counts']['market_cap'] == 3
        assert result['counts']['fundamental'] == 3
        assert result['counts']['trading'] == 3
        assert result['counts']['short_selling'] == 3
        assert result['counts']['short_balance'] == 3
        assert len(result['errors']) == 0

    def test_partial_success_some_data_fails(self, mock_components):
        """일부 데이터 실패 시 나머지는 계속 수집"""
        # Given
        client = mock_components['client']
        saver = mock_components['saver']

        # 일부는 성공, 일부는 실패
        sample_df = pd.DataFrame({'col1': [1, 2, 3]})
        client.get_ohlcv.return_value = sample_df
        client.get_market_cap.side_effect = Exception("시가총액 조회 실패")
        client.get_fundamental.return_value = sample_df
        client.get_trading_by_investor.side_effect = Exception("매매 조회 실패")
        client.get_short_selling_volume.return_value = pd.DataFrame()
        client.get_short_balance.return_value = pd.DataFrame()

        saver.save_daily_prices.return_value = 3
        saver.save_fundamentals.return_value = 3

        # When
        result = fetch_stock_data("000001", "테스트종목", "KOSPI", "20251204", "today")

        # Then: 성공은 기록되고, 실패는 errors에 기록
        assert result['success'] is True
        assert result['counts']['daily_price'] == 3
        assert result['counts']['fundamental'] == 3
        assert 'market_cap' not in result['counts']
        assert 'trading' not in result['counts']
        assert len(result['errors']) == 2
        assert any("시가총액" in err for err in result['errors'])
        assert any("매매" in err for err in result['errors'])

    def test_ohlcv_fails_continues_others(self, mock_components):
        """OHLCV 실패해도 다른 데이터는 수집"""
        # Given
        client = mock_components['client']
        saver = mock_components['saver']

        # OHLCV만 실패
        client.get_ohlcv.side_effect = Exception("주가 조회 실패")
        sample_df = pd.DataFrame({'col1': [1, 2, 3]})
        client.get_market_cap.return_value = sample_df
        client.get_fundamental.return_value = sample_df
        client.get_trading_by_investor.return_value = sample_df
        client.get_short_selling_volume.return_value = pd.DataFrame()
        client.get_short_balance.return_value = pd.DataFrame()

        saver.save_market_caps.return_value = 3
        saver.save_fundamentals.return_value = 3
        saver.save_trading_by_investor.return_value = 3

        # When
        result = fetch_stock_data("000001", "테스트종목", "KOSPI", "20251204", "today")

        # Then
        assert result['success'] is True
        assert 'daily_price' not in result['counts']
        assert result['counts']['market_cap'] == 3
        assert len(result['errors']) == 1

    def test_short_selling_fails_silently(self, mock_components):
        """공매도 데이터 실패는 조용히 무시"""
        # Given
        client = mock_components['client']
        saver = mock_components['saver']

        sample_df = pd.DataFrame({'col1': [1, 2, 3]})
        client.get_ohlcv.return_value = sample_df
        client.get_market_cap.return_value = pd.DataFrame()
        client.get_fundamental.return_value = pd.DataFrame()
        client.get_trading_by_investor.return_value = pd.DataFrame()
        # 공매도만 실패
        client.get_short_selling_volume.side_effect = Exception("공매도 조회 실패")
        client.get_short_balance.side_effect = Exception("잔고 조회 실패")

        saver.save_daily_prices.return_value = 3

        # When
        result = fetch_stock_data("000001", "테스트종목", "KOSPI", "20251204", "today")

        # Then: 공매도 실패는 errors에 추가되지 않음 (silent fail)
        assert result['success'] is True
        assert 'short_selling' not in result['counts']
        assert 'short_balance' not in result['counts']
        # 공매도 오류는 errors에 추가되지 않음
        assert not any("공매도" in err for err in result['errors'])

    def test_client_error_handled_gracefully(self, mock_components):
        """KRXClient 생성 실패 시 전체 실패로 처리"""
        # Given: Database는 정상, Client 생성 실패
        mock_components['client']  # 이미 모킹되었지만 side_effect 설정

        # Database context manager는 예외를 발생시켜야 함
        # 실제로는 KRXClient 생성이 아니라 내부 로직에서 발생
        # 대신 전체를 감싸는 try-except를 테스트
        with patch('data_fetcher.Database') as mock_db:
            mock_db.return_value.get_session.return_value.__enter__.side_effect = Exception("DB 연결 실패")

            # When
            result = fetch_stock_data("000001", "테스트종목", "KOSPI", "20251204", "today")

            # Then
            assert result['success'] is False
            assert len(result['errors']) > 0
            assert any("전체 수집 실패" in err for err in result['errors'])

    def test_saver_error_recorded_in_result(self, mock_components):
        """DataSaver 저장 실패는 errors에 기록"""
        # Given
        client = mock_components['client']
        saver = mock_components['saver']

        sample_df = pd.DataFrame({'col1': [1, 2, 3]})
        client.get_ohlcv.return_value = sample_df
        client.get_market_cap.return_value = pd.DataFrame()
        client.get_fundamental.return_value = pd.DataFrame()
        client.get_trading_by_investor.return_value = pd.DataFrame()
        client.get_short_selling_volume.return_value = pd.DataFrame()
        client.get_short_balance.return_value = pd.DataFrame()

        # save 시점에 오류 발생
        saver.save_daily_prices.side_effect = Exception("DB 저장 실패")

        # When
        result = fetch_stock_data("000001", "테스트종목", "KOSPI", "20251204", "today")

        # Then
        assert result['success'] is True  # 다른 데이터는 수집 가능
        assert 'daily_price' not in result['counts']
        assert len(result['errors']) > 0


class TestFetchWatchlistData:
    """fetch_watchlist_data 함수 테스트"""

    @pytest.fixture
    def mock_watchlist(self, mocker):
        """테스트용 WATCHLIST"""
        return mocker.patch('data_fetcher.WATCHLIST', [
            ("000001", "테스트종목1", "KOSPI"),
            ("000002", "테스트종목2", "KOSDAQ"),
        ])

    def test_skip_when_data_exists(self, mocker, mock_watchlist):
        """데이터가 이미 있으면 스킵"""
        # Given: check_data_exists가 True 반환
        mock_check = mocker.patch('data_fetcher.check_data_exists', return_value=True)
        mock_fetch = mocker.patch('data_fetcher.fetch_stock_data')

        # When
        result = fetch_watchlist_data("20251204", "today", force=False)

        # Then: fetch_stock_data 호출되지 않음
        assert result['skipped'] == 2
        assert result['total_success'] == 0
        assert result['total_failed'] == 0
        assert mock_check.call_count == 2
        mock_fetch.assert_not_called()

    def test_fetch_when_data_missing(self, mocker, mock_watchlist):
        """데이터가 없으면 수집"""
        # Given
        mock_check = mocker.patch('data_fetcher.check_data_exists', return_value=False)
        mock_fetch = mocker.patch('data_fetcher.fetch_stock_data')
        mock_fetch.return_value = {'success': True, 'ticker': '000001', 'counts': {}, 'errors': []}

        # When
        result = fetch_watchlist_data("20251204", "today", force=False)

        # Then
        assert result['skipped'] == 0
        assert result['total_success'] == 2
        assert result['total_failed'] == 0
        assert mock_fetch.call_count == 2

    def test_force_refetch_overrides_skip(self, mocker, mock_watchlist):
        """force=True면 기존 데이터 무시하고 재수집"""
        # Given: 데이터가 있어도
        mock_check = mocker.patch('data_fetcher.check_data_exists', return_value=True)
        mock_fetch = mocker.patch('data_fetcher.fetch_stock_data')
        mock_fetch.return_value = {'success': True, 'ticker': '000001', 'counts': {}, 'errors': []}

        # When: force=True
        result = fetch_watchlist_data("20251204", "today", force=True)

        # Then: check 호출되지 않고 바로 수집
        mock_check.assert_not_called()
        assert result['skipped'] == 0
        assert result['total_success'] == 2
        assert mock_fetch.call_count == 2

    def test_multiple_stocks_success(self, mocker, mock_watchlist):
        """여러 종목 수집 성공"""
        # Given
        mock_check = mocker.patch('data_fetcher.check_data_exists', return_value=False)
        mock_fetch = mocker.patch('data_fetcher.fetch_stock_data')

        # 각 종목별 다른 결과
        mock_fetch.side_effect = [
            {'success': True, 'ticker': '000001', 'name': '테스트1', 'counts': {'daily_price': 5}, 'errors': []},
            {'success': True, 'ticker': '000002', 'name': '테스트2', 'counts': {'daily_price': 3}, 'errors': []},
        ]

        # When
        result = fetch_watchlist_data("20251204", "recent", force=False)

        # Then
        assert result['total_success'] == 2
        assert result['total_failed'] == 0
        assert len(result['stocks']) == 2
        assert result['stocks'][0]['ticker'] == '000001'
        assert result['stocks'][1]['ticker'] == '000002'

    def test_partial_failure_continues(self, mocker, mock_watchlist):
        """일부 실패해도 나머지는 계속 수집"""
        # Given
        mock_check = mocker.patch('data_fetcher.check_data_exists', return_value=False)
        mock_fetch = mocker.patch('data_fetcher.fetch_stock_data')

        # 첫 번째는 성공, 두 번째는 실패
        mock_fetch.side_effect = [
            {'success': True, 'ticker': '000001', 'counts': {}, 'errors': []},
            {'success': False, 'ticker': '000002', 'counts': {}, 'errors': ['전체 수집 실패']},
        ]

        # When
        result = fetch_watchlist_data("20251204", "today", force=False)

        # Then
        assert result['total_success'] == 1
        assert result['total_failed'] == 1
        assert len(result['stocks']) == 2

    def test_result_statistics_correct(self, mocker, mock_watchlist):
        """결과 통계가 정확하게 집계"""
        # Given
        mock_check = mocker.patch('data_fetcher.check_data_exists')
        # 첫 번째는 이미 있음, 두 번째는 없음
        mock_check.side_effect = [True, False]

        mock_fetch = mocker.patch('data_fetcher.fetch_stock_data')
        mock_fetch.return_value = {'success': True, 'ticker': '000002', 'counts': {}, 'errors': []}

        # When
        result = fetch_watchlist_data("20251204", "today", force=False)

        # Then
        assert result['skipped'] == 1
        assert result['total_success'] == 1
        assert result['total_failed'] == 0
        assert result['date'] == "20251204"
        assert result['mode'] == "today"

    def test_default_date_uses_today(self, mocker, mock_watchlist):
        """date_str이 None이면 오늘 날짜 사용"""
        # Given
        mock_check = mocker.patch('data_fetcher.check_data_exists', return_value=True)

        # When
        result = fetch_watchlist_data(date_str=None, fetch_mode="today", force=False)

        # Then: 오늘 날짜가 설정됨
        today_str = datetime.now().strftime('%Y%m%d')
        assert result['date'] == today_str
        # check 호출 시 오늘 날짜 사용
        mock_check.assert_called_with("000002", today_str)

    def test_custom_date_string(self, mocker, mock_watchlist):
        """특정 날짜 문자열 사용"""
        # Given
        mock_check = mocker.patch('data_fetcher.check_data_exists', return_value=True)

        # When
        result = fetch_watchlist_data(date_str="20251203", fetch_mode="month", force=False)

        # Then
        assert result['date'] == "20251203"
        assert result['mode'] == "month"
        mock_check.assert_called_with("000002", "20251203")
