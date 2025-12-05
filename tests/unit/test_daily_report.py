#!/usr/bin/env python3
"""
daily_report 모듈 단위 테스트

일일 리포트 생성 로직 테스트:
- 포맷팅 헬퍼 함수 (format_number, format_percentage, format_change)
- 시장 개황 생성 (generate_market_overview)
- 주요 동향 생성 (generate_top_movers)
- 관심 종목 섹션 생성 (generate_watchlist_section)
- 전체 리포트 생성 (generate_report)
- 리포트 저장 (save_report)
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch, mock_open
import pandas as pd
import numpy as np

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from report.daily_report import DailyReport


class TestFormatHelpers:
    """포맷팅 헬퍼 함수 테스트 (격리 가능, 모킹 불필요)"""

    @pytest.fixture
    def report(self, mocker):
        """MarketSummary, Database 모킹하여 DailyReport 생성"""
        mocker.patch('report.daily_report.MarketSummary')
        mocker.patch('report.daily_report.Database')
        return DailyReport()

    def test_format_number_with_int(self, report):
        """정수 포맷팅"""
        assert report.format_number(1000) == "1,000"
        assert report.format_number(1234567) == "1,234,567"
        assert report.format_number(0) == "0"

    def test_format_number_with_float(self, report):
        """실수 포맷팅 (소수점 제거)"""
        assert report.format_number(1000.5) == "1,000"
        assert report.format_number(1234.99) == "1,235"

    def test_format_number_with_none(self, report):
        """None 값 처리"""
        assert report.format_number(None) == "N/A"

    def test_format_number_with_nan(self, report):
        """NaN 값 처리"""
        assert report.format_number(np.nan) == "N/A"
        assert report.format_number(pd.NA) == "N/A"

    def test_format_percentage_positive(self, report):
        """양수 퍼센트 포맷팅 (+ 기호 포함)"""
        assert report.format_percentage(5.67) == "+5.67%"
        assert report.format_percentage(10) == "+10.00%"

    def test_format_percentage_negative(self, report):
        """음수 퍼센트 포맷팅 (- 기호 자동)"""
        assert report.format_percentage(-3.45) == "-3.45%"
        assert report.format_percentage(-10) == "-10.00%"

    def test_format_percentage_zero(self, report):
        """0% 포맷팅"""
        assert report.format_percentage(0) == "0.00%"

    def test_format_percentage_with_nan(self, report):
        """NaN 퍼센트 처리"""
        assert report.format_percentage(np.nan) == "N/A"

    def test_format_change_with_arrow(self, report):
        """변동 폭 포맷팅 (부호 포함)"""
        assert report.format_change(100.50) == "+100.50"
        assert report.format_change(-50.25) == "-50.25"
        assert report.format_change(0) == "0.00"

    def test_format_change_with_nan(self, report):
        """NaN 변동 폭 처리"""
        assert report.format_change(np.nan) == "N/A"


class TestGenerateMarketOverview:
    """시장 개황 섹션 생성 테스트"""

    @pytest.fixture
    def report(self, mocker):
        """모킹된 DailyReport"""
        mock_summary = mocker.patch('report.daily_report.MarketSummary')
        mocker.patch('report.daily_report.Database')
        return DailyReport()

    def test_market_overview_success(self, report, mocker):
        """정상적인 시장 개황 생성"""
        # Given: 정상 지수 데이터
        mock_indices = {
            'kospi': {
                'close': 2500.00,
                'change': 50.00,
                'change_pct': 2.04,
                'volume': 500000000
            },
            'kosdaq': {
                'close': 850.00,
                'change': -10.00,
                'change_pct': -1.16,
                'volume': 800000000
            }
        }

        report.market_summary.get_index_info = Mock(return_value=mock_indices)

        # When
        result = report.generate_market_overview("20251204")

        # Then
        assert "📊 시장 개황" in result
        assert "20251204" in result
        assert "KOSPI" in result
        assert "2,500" in result
        assert "+50.00" in result
        assert "+2.04%" in result
        assert "KOSDAQ" in result
        assert "850" in result
        assert "-10.00" in result
        assert "-1.16%" in result

    def test_market_overview_empty_data(self, report, mocker):
        """데이터가 없을 때"""
        # Given: 빈 딕셔너리
        report.market_summary.get_index_info = Mock(return_value={})

        # When
        result = report.generate_market_overview("20251204")

        # Then: 헤더만 있고 데이터는 없음
        assert "📊 시장 개황" in result
        assert "KOSPI" not in result
        assert "KOSDAQ" not in result


class TestGenerateTopMovers:
    """주요 동향 섹션 생성 테스트"""

    @pytest.fixture
    def report(self, mocker):
        """모킹된 DailyReport"""
        mocker.patch('report.daily_report.MarketSummary')
        mocker.patch('report.daily_report.Database')
        return DailyReport()

    def test_top_gainers_formatting(self, report):
        """급등 종목 포맷팅"""
        # Given
        gainers_df = pd.DataFrame({
            '종목명': ['삼성전자', 'SK하이닉스'],
            '종가': [70000, 120000],
            '등락률': [5.5, 3.2],
            '거래량': [10000000, 5000000]
        })

        report.market_summary.get_top_gainers = Mock(return_value=gainers_df)
        report.market_summary.get_top_losers = Mock(return_value=pd.DataFrame())
        report.market_summary.get_top_volume = Mock(return_value=pd.DataFrame())

        # When
        result = report.generate_top_movers("20251204", "KOSPI")

        # Then
        assert "급등 상위 5종목" in result
        assert "삼성전자" in result
        assert "70,000원" in result
        assert "+5.50%" in result

    def test_top_losers_formatting(self, report):
        """급락 종목 포맷팅"""
        # Given
        losers_df = pd.DataFrame({
            '종목명': ['현대차', '기아'],
            '종가': [180000, 85000],
            '등락률': [-2.5, -4.1],
            '거래량': [3000000, 4000000]
        })

        report.market_summary.get_top_gainers = Mock(return_value=pd.DataFrame())
        report.market_summary.get_top_losers = Mock(return_value=losers_df)
        report.market_summary.get_top_volume = Mock(return_value=pd.DataFrame())

        # When
        result = report.generate_top_movers("20251204", "KOSDAQ")

        # Then
        assert "급락 상위 5종목" in result
        assert "현대차" in result
        assert "-2.50%" in result

    def test_top_volume_formatting(self, report):
        """거래대금 상위 포맷팅"""
        # Given
        volume_df = pd.DataFrame({
            '종목명': ['삼성전자', 'NAVER'],
            '종가': [70000, 200000],
            '등락률': [1.0, -0.5],
            '거래대금': [50000000000, 30000000000]  # 500억, 300억
        })

        report.market_summary.get_top_gainers = Mock(return_value=pd.DataFrame())
        report.market_summary.get_top_losers = Mock(return_value=pd.DataFrame())
        report.market_summary.get_top_volume = Mock(return_value=volume_df)

        # When
        result = report.generate_top_movers("20251204", "KOSPI")

        # Then
        assert "거래대금 상위 5종목" in result
        assert "500억" in result
        assert "300억" in result

    def test_empty_dataframe_handled(self, report):
        """빈 DataFrame 처리"""
        # Given: 모두 빈 결과
        report.market_summary.get_top_gainers = Mock(return_value=pd.DataFrame())
        report.market_summary.get_top_losers = Mock(return_value=pd.DataFrame())
        report.market_summary.get_top_volume = Mock(return_value=pd.DataFrame())

        # When
        result = report.generate_top_movers("20251204", "KOSPI")

        # Then: 섹션 헤더만 있음
        assert "📈 KOSPI 주요 동향" in result
        assert "급등 상위 5종목" not in result
        assert "급락 상위 5종목" not in result


class TestGenerateWatchlistSection:
    """관심 종목 섹션 생성 테스트"""

    @pytest.fixture
    def report(self, mocker):
        """모킹된 DailyReport"""
        mocker.patch('report.daily_report.MarketSummary')

        # Database context manager 모킹
        mock_db = mocker.patch('report.daily_report.Database')
        mock_session = MagicMock()
        mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session

        daily_report = DailyReport()
        daily_report.db_session = mock_session  # 테스트용
        return daily_report

    def test_watchlist_with_price_data(self, report, mocker):
        """주가 데이터가 있는 종목"""
        # Given
        mock_stock = Mock()
        mock_stock.ticker = "000001"
        mock_stock.name = "테스트종목"

        mock_price = Mock()
        mock_price.date = datetime(2025, 12, 4).date()
        mock_price.close = 50000
        mock_price.open = 48000
        mock_price.volume = 1000000

        mock_queries = mocker.patch('report.daily_report.StockQueries')
        mock_queries.get_all_stocks.return_value = [mock_stock]
        mock_queries.get_latest_price.return_value = mock_price
        mock_queries.get_foreign_net_buying_days.return_value = []
        mock_queries.get_fundamentals.return_value = []

        # When
        result = report.generate_watchlist_section("20251204")

        # Then
        assert "⭐ 관심 종목 분석" in result
        assert "테스트종목 (000001)" in result
        assert "50,000원" in result
        # 등락률 계산: (50000-48000)/48000 * 100 = 4.17%
        assert "+" in result  # 양수 등락률

    def test_watchlist_no_price_data_skipped(self, report, mocker):
        """주가 데이터가 없으면 스킵"""
        # Given
        mock_stock = Mock()
        mock_stock.ticker = "000001"
        mock_stock.name = "테스트종목"

        mock_queries = mocker.patch('report.daily_report.StockQueries')
        mock_queries.get_all_stocks.return_value = [mock_stock]
        mock_queries.get_latest_price.return_value = None

        # When
        result = report.generate_watchlist_section("20251204")

        # Then
        assert "⭐ 관심 종목 분석" in result
        # 종목이 표시되지 않음
        assert "테스트종목" not in result

    def test_foreign_net_buy_calculation(self, report, mocker):
        """외국인 순매수 계산"""
        # Given
        mock_stock = Mock()
        mock_stock.ticker = "000001"
        mock_stock.name = "테스트종목"

        mock_price = Mock()
        mock_price.date = datetime(2025, 12, 4).date()
        mock_price.close = 50000
        mock_price.open = 48000
        mock_price.volume = 1000000

        mock_foreign = Mock()
        mock_foreign.date = datetime(2025, 12, 3).date()
        mock_foreign.foreigner_net = 500000000  # 5억

        mock_queries = mocker.patch('report.daily_report.StockQueries')
        mock_queries.get_all_stocks.return_value = [mock_stock]
        mock_queries.get_latest_price.return_value = mock_price
        mock_queries.get_foreign_net_buying_days.return_value = [mock_foreign]
        mock_queries.get_fundamentals.return_value = []

        # When
        result = report.generate_watchlist_section("20251204")

        # Then
        assert "외국인 순매수 (최근 5일)" in result
        assert "5.0억" in result

    def test_fundamental_display(self, report, mocker):
        """펀더멘탈 표시"""
        # Given
        mock_stock = Mock()
        mock_stock.ticker = "000001"
        mock_stock.name = "테스트종목"

        mock_price = Mock()
        mock_price.date = datetime(2025, 12, 4).date()
        mock_price.close = 50000
        mock_price.open = 48000
        mock_price.volume = 1000000

        mock_fund = Mock()
        mock_fund.date = datetime(2025, 12, 4).date()
        mock_fund.per = 12.5
        mock_fund.pbr = 1.8
        mock_fund.eps = 4000

        mock_queries = mocker.patch('report.daily_report.StockQueries')
        mock_queries.get_all_stocks.return_value = [mock_stock]
        mock_queries.get_latest_price.return_value = mock_price
        mock_queries.get_foreign_net_buying_days.return_value = []
        mock_queries.get_fundamentals.return_value = [mock_fund]

        # When
        result = report.generate_watchlist_section("20251204")

        # Then
        assert "펀더멘탈" in result
        assert "PER 12.50" in result
        assert "PBR 1.80" in result
        assert "EPS 4,000원" in result

    def test_null_handling_in_fundamentals(self, report, mocker):
        """펀더멘탈 NULL 값 처리"""
        # Given
        mock_stock = Mock()
        mock_stock.ticker = "000001"
        mock_stock.name = "테스트종목"

        mock_price = Mock()
        mock_price.date = datetime(2025, 12, 4).date()
        mock_price.close = 50000
        mock_price.open = 48000
        mock_price.volume = 1000000

        mock_fund = Mock()
        mock_fund.date = datetime(2025, 12, 4).date()
        mock_fund.per = None
        mock_fund.pbr = 1.5
        mock_fund.eps = None

        mock_queries = mocker.patch('report.daily_report.StockQueries')
        mock_queries.get_all_stocks.return_value = [mock_stock]
        mock_queries.get_latest_price.return_value = mock_price
        mock_queries.get_foreign_net_buying_days.return_value = []
        mock_queries.get_fundamentals.return_value = [mock_fund]

        # When
        result = report.generate_watchlist_section("20251204")

        # Then: PBR만 표시
        assert "펀더멘탈" in result
        assert "PBR 1.50" in result
        # PER, EPS는 None이므로 표시되지 않음


class TestGenerateReport:
    """전체 리포트 생성 테스트"""

    @pytest.fixture
    def report(self, mocker):
        """모킹된 DailyReport"""
        mocker.patch('report.daily_report.MarketSummary')
        mock_db = mocker.patch('report.daily_report.Database')
        mock_session = MagicMock()
        mock_db.return_value.get_session.return_value.__enter__.return_value = mock_session

        daily_report = DailyReport()

        # 각 섹션 생성 메서드 모킹
        mocker.patch.object(daily_report, 'generate_market_overview', return_value="시장 개황\n")
        mocker.patch.object(daily_report, 'generate_top_movers', return_value="주요 동향\n")
        mocker.patch.object(daily_report, 'generate_watchlist_section', return_value="관심 종목\n")

        return daily_report

    def test_generate_report_default_date(self, report):
        """날짜 미지정 시 오늘 날짜 사용"""
        # When
        result = report.generate_report(date_str=None)

        # Then
        assert "📋 일일 투자 리포트" in result
        assert "생성일시:" in result

    def test_generate_report_custom_date(self, report):
        """특정 날짜 지정"""
        # When
        result = report.generate_report(date_str="20251204")

        # Then
        assert "📋 일일 투자 리포트" in result
        # 모킹된 섹션들이 포함
        assert "시장 개황" in result
        assert "주요 동향" in result
        assert "관심 종목" in result

    def test_generate_report_calls_all_sections(self, report):
        """모든 섹션 생성 메서드 호출"""
        # When
        result = report.generate_report("20251204")

        # Then: 각 메서드가 호출됨
        report.generate_market_overview.assert_called_once_with("20251204")
        # generate_top_movers는 KOSPI, KOSDAQ 각각 호출
        assert report.generate_top_movers.call_count == 2
        report.generate_watchlist_section.assert_called_once_with("20251204")


class TestSaveReport:
    """리포트 저장 테스트"""

    @pytest.fixture
    def report(self, mocker):
        """모킹된 DailyReport"""
        mocker.patch('report.daily_report.MarketSummary')
        mocker.patch('report.daily_report.Database')
        return DailyReport()

    def test_save_report_creates_directory(self, report, mocker):
        """reports 디렉토리 생성"""
        # Given
        mock_makedirs = mocker.patch('report.daily_report.os.makedirs')
        mock_open_func = mocker.patch('builtins.open', mock_open())

        # When
        result = report.save_report("테스트 리포트", "test.txt")

        # Then: makedirs 호출됨
        mock_makedirs.assert_called_once()
        assert mock_makedirs.call_args[1]['exist_ok'] is True

    def test_save_report_file_content(self, report, mocker):
        """파일 내용 저장"""
        # Given
        mocker.patch('report.daily_report.os.makedirs')
        mock_file = mock_open()
        mocker.patch('builtins.open', mock_file)

        # When
        report.save_report("테스트 리포트 내용", "test.txt")

        # Then: 파일에 내용 기록
        mock_file().write.assert_called_once_with("테스트 리포트 내용")

    def test_save_report_returns_filepath(self, report, mocker):
        """파일 경로 반환"""
        # Given
        mocker.patch('report.daily_report.os.makedirs')
        mocker.patch('builtins.open', mock_open())

        # When
        result = report.save_report("테스트", "test.txt")

        # Then: 경로 문자열 반환
        assert isinstance(result, str)
        assert "test.txt" in result
        assert "reports" in result
