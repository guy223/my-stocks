import logging
import sys
import os
from datetime import datetime, timedelta
from pykrx import stock as pykrx_stock

# src 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from database.connection import Database
from krx.client import KRXClient
from krx.saver import DataSaver

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def collect_stock_data(ticker: str, name: str, market: str, days: int = 365):
    """
    종목 데이터 수집

    Args:
        ticker: 종목코드
        name: 종목명
        market: 시장 (KOSPI/KOSDAQ)
        days: 수집 기간 (일)
    """
    # 날짜 계산
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')

    logger.info(f"{'=' * 60}")
    logger.info(f"종목: {name} ({ticker})")
    logger.info(f"기간: {start_str} ~ {end_str}")
    logger.info(f"{'=' * 60}")

    # 데이터베이스 연결
    db = Database()
    db.create_tables()

    with db.get_session() as session:
        # 클라이언트 및 저장 객체 생성
        krx_client = KRXClient(session)
        saver = DataSaver(session)

        # 1. 종목 정보 저장
        saver.save_stock(ticker, name, market)

        try:
            # 2. OHLCV 데이터 수집 및 저장
            logger.info("1/6: OHLCV 데이터 수집 중...")
            ohlcv_df = krx_client.get_ohlcv(ticker, start_str, end_str)
            saver.save_daily_prices(ticker, ohlcv_df)

            # 3. 시가총액 데이터 수집 및 저장
            logger.info("2/6: 시가총액 데이터 수집 중...")
            cap_df = krx_client.get_market_cap(ticker, start_str, end_str)
            saver.save_market_caps(ticker, cap_df)

            # 4. 펀더멘탈 데이터 수집 및 저장
            logger.info("3/6: 펀더멘탈 데이터 수집 중...")
            fund_df = krx_client.get_fundamental(ticker, start_str, end_str)
            saver.save_fundamentals(ticker, fund_df)

            # 5. 투자자별 매매 동향 수집 및 저장
            logger.info("4/6: 투자자별 매매 동향 수집 중...")
            trading_df = krx_client.get_trading_by_investor(ticker, start_str, end_str)
            saver.save_trading_by_investor(ticker, trading_df)

            # 6. 공매도 데이터 수집 및 저장
            logger.info("5/6: 공매도 데이터 수집 중...")
            short_df = krx_client.get_short_selling_volume(ticker, start_str, end_str)
            saver.save_short_selling(ticker, short_df)

            # 7. 공매도 잔고 수집 및 저장
            logger.info("6/6: 공매도 잔고 수집 중...")
            balance_df = krx_client.get_short_balance(ticker, start_str, end_str)
            saver.save_short_balance(ticker, balance_df)

            logger.info(f"✓ {name} ({ticker}) 데이터 수집 완료")

        except Exception as e:
            logger.error(f"✗ 데이터 수집 실패: {e}", exc_info=True)
            raise

def main():
    """메인 실행 함수"""

    # 테스트 종목 정보
    stocks = [
        {
            'ticker': '267260',
            'name': 'HD현대일렉트릭',
            'market': 'KOSPI'
        },
        {
            'ticker': '064350',
            'name': '현대로템',
            'market': 'KOSPI'
        }
    ]

    # 각 종목별 데이터 수집 (최근 1년)
    for stock_info in stocks:
        try:
            collect_stock_data(
                ticker=stock_info['ticker'],
                name=stock_info['name'],
                market=stock_info['market'],
                days=365  # 1년
            )
        except Exception as e:
            logger.error(f"종목 처리 실패: {stock_info['name']} - {e}")
            continue

    logger.info("=" * 60)
    logger.info("전체 데이터 수집 완료")
    logger.info("=" * 60)

if __name__ == '__main__':
    main()
