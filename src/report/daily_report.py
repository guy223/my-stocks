import logging
import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# 상대 경로 처리
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis.market_summary import MarketSummary
from database.connection import Database
from database.queries import StockQueries

logger = logging.getLogger(__name__)

class DailyReport:
    """일일 투자 리포트 생성기"""

    def __init__(self):
        self.market_summary = MarketSummary()
        self.db = Database()

    def format_number(self, num):
        """숫자 포맷팅 (천 단위 콤마)"""
        if pd.isna(num):
            return "N/A"
        if isinstance(num, (int, float)):
            return f"{num:,.0f}"
        return str(num)

    def format_percentage(self, num):
        """퍼센트 포맷팅"""
        if pd.isna(num):
            return "N/A"
        if isinstance(num, (int, float)):
            sign = "+" if num > 0 else ""
            return f"{sign}{num:.2f}%"
        return str(num)

    def format_change(self, num):
        """변동 폭 포맷팅"""
        if pd.isna(num):
            return "N/A"
        if isinstance(num, (int, float)):
            sign = "+" if num > 0 else ""
            return f"{sign}{num:,.2f}"
        return str(num)

    def generate_market_overview(self, date_str: str) -> str:
        """시장 개황 섹션 생성"""
        try:
            indices = self.market_summary.get_index_info(date_str)
        except Exception as e:
            # 데이터 없음 예외를 상위로 전파
            if "데이터 없음" in str(e) or isinstance(e, ValueError):
                raise ValueError(f"데이터 없음: {date_str}") from e
            # 다른 예외는 그대로 전파
            raise

        report = "=" * 80 + "\n"
        report = report + f"📊 시장 개황 ({date_str})\n"
        report = report + "=" * 80 + "\n\n"

        if 'kospi' in indices:
            kospi = indices['kospi']
            report = report + f"▶ KOSPI: {self.format_number(kospi['close'])} "
            report = report + f"({self.format_change(kospi['change'])}, {self.format_percentage(kospi['change_pct'])})\n"
            report = report + f"  거래량: {self.format_number(kospi['volume'])}\n\n"

        if 'kosdaq' in indices:
            kosdaq = indices['kosdaq']
            report = report + f"▶ KOSDAQ: {self.format_number(kosdaq['close'])} "
            report = report + f"({self.format_change(kosdaq['change'])}, {self.format_percentage(kosdaq['change_pct'])})\n"
            report = report + f"  거래량: {self.format_number(kosdaq['volume'])}\n\n"

        return report

    def generate_top_movers(self, date_str: str, market: str = "KOSPI") -> str:
        """급등/급락 종목 섹션 생성"""
        report = "-" * 80 + "\n"
        report = report + f"📈 {market} 주요 동향\n"
        report = report + "-" * 80 + "\n\n"

        # 급등 종목
        gainers = self.market_summary.get_top_gainers(date_str, market, 5)
        if not gainers.empty:
            report = report + "▶ 급등 상위 5종목:\n"
            for idx, row in gainers.iterrows():
                report = report + f"  {row['종목명']:15s} {self.format_number(row['종가']):>12s}원  "
                report = report + f"{self.format_percentage(row['등락률']):>8s}  거래량: {self.format_number(row['거래량'])}\n"
            report = report + "\n"

        # 급락 종목
        losers = self.market_summary.get_top_losers(date_str, market, 5)
        if not losers.empty:
            report = report + "▶ 급락 상위 5종목:\n"
            for idx, row in losers.iterrows():
                report = report + f"  {row['종목명']:15s} {self.format_number(row['종가']):>12s}원  "
                report = report + f"{self.format_percentage(row['등락률']):>8s}  거래량: {self.format_number(row['거래량'])}\n"
            report = report + "\n"

        # 거래대금 상위
        volume = self.market_summary.get_top_volume(date_str, market, 5)
        if not volume.empty:
            report = report + "▶ 거래대금 상위 5종목:\n"
            for idx, row in volume.iterrows():
                등락률 = self.format_percentage(row.get('등락률', 0))
                거래대금억 = row['거래대금'] / 100000000
                report = report + f"  {row['종목명']:15s} {self.format_number(row['종가']):>12s}원  "
                report = report + f"{등락률:>8s}  거래대금: {거래대금억:,.0f}억\n"
            report = report + "\n"

        return report

    def generate_watchlist_section(self, date_str: str) -> str:
        """관심 종목 섹션 생성"""
        report = "-" * 80 + "\n"
        report = report + "⭐ 관심 종목 분석\n"
        report = report + "-" * 80 + "\n\n"

        date_obj = datetime.strptime(date_str, '%Y%m%d').date()

        with self.db.get_session() as session:
            # 모든 등록된 종목
            stocks = StockQueries.get_all_stocks(session)

            for stock in stocks:
                ticker = stock.ticker
                name = stock.name

                # 최근 주가
                latest = StockQueries.get_latest_price(session, ticker)
                if latest and latest.date == date_obj:
                    등락률 = ((latest.close - latest.open) / latest.open * 100)

                    report = report + f"▶ {name} ({ticker})\n"
                    report = report + f"  종가: {self.format_number(latest.close)}원  "
                    report = report + f"등락률: {self.format_percentage(등락률)}  "
                    report = report + f"거래량: {self.format_number(latest.volume)}\n"

                    # 외국인 순매수 (최근 5일)
                    foreign = StockQueries.get_foreign_net_buying_days(session, ticker, 5)
                    if foreign:
                        report = report + f"  외국인 순매수 (최근 5일):\n"
                        for f in foreign:
                            if f.foreigner_net is not None:
                                외국인억 = f.foreigner_net / 100000000
                                report = report + f"    {f.date}: {외국인억:,.1f}억\n"

                    # 펀더멘탈
                    fundamentals = StockQueries.get_fundamentals(session, ticker)
                    if fundamentals:
                        latest_fund = fundamentals[-1]
                        if latest_fund.date == date_obj:
                            report = report + f"  펀더멘탈: "
                            if latest_fund.per:
                                report = report + f"PER {latest_fund.per:.2f}  "
                            if latest_fund.pbr:
                                report = report + f"PBR {latest_fund.pbr:.2f}  "
                            if latest_fund.eps:
                                report = report + f"EPS {self.format_number(latest_fund.eps)}원"
                            report = report + "\n"

                    report = report + "\n"

        return report

    def generate_report(self, date_str: str = None) -> str:
        """
        일일 리포트 생성

        Args:
            date_str: 날짜 (YYYYMMDD), None이면 오늘

        Returns:
            리포트 텍스트
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y%m%d')

        logger.info(f"일일 리포트 생성 중: {date_str}")

        report = "\n"
        report = report + "╔" + "=" * 78 + "╗\n"
        report = report + "║" + " " * 25 + "📋 일일 투자 리포트" + " " * 34 + "║\n"
        report = report + "║" + " " * 78 + "║\n"
        report = report + "║" + f"  생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " " * 47 + "║\n"
        report = report + "╚" + "=" * 78 + "╝\n\n"

        # 1. 시장 개황
        report = report + self.generate_market_overview(date_str)

        # 2. KOSPI 주요 동향
        report = report + self.generate_top_movers(date_str, "KOSPI")

        # 3. KOSDAQ 주요 동향
        report = report + self.generate_top_movers(date_str, "KOSDAQ")

        # 4. 관심 종목 분석
        report = report + self.generate_watchlist_section(date_str)

        report = report + "=" * 80 + "\n"
        report = report + "리포트 생성 완료\n"
        report = report + "=" * 80 + "\n"

        return report

    def save_report(self, report: str, filename: str = None):
        """
        리포트를 파일로 저장

        Args:
            report: 리포트 텍스트
            filename: 파일명 (None이면 자동 생성)
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"daily_report_{timestamp}.txt"

        # reports 디렉토리 생성
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'reports')
        os.makedirs(reports_dir, exist_ok=True)

        filepath = os.path.join(reports_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"리포트 저장 완료: {filepath}")
        return filepath
