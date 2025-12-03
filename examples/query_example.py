import logging
import sys
import os
from datetime import datetime, timedelta

# src 디렉토리를 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.connection import Database
from database.queries import StockQueries

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """데이터 조회 예제"""

    # 데이터베이스 연결
    db = Database()

    with db.get_session() as session:
        # HD현대일렉트릭 데이터 조회
        ticker = '267260'

        # 1. 종목 정보
        stock = StockQueries.get_stock(session, ticker)
        if stock:
            logger.info(f"종목: {stock.name} ({stock.ticker})")
            logger.info(f"시장: {stock.market}")
        else:
            logger.warning(f"종목 정보 없음: {ticker}")
            return

        # 2. 최근 주가
        latest_price = StockQueries.get_latest_price(session, ticker)
        if latest_price:
            logger.info(f"\n최근 주가 ({latest_price.date}):")
            logger.info(f"  시가: {latest_price.open:,}원")
            logger.info(f"  고가: {latest_price.high:,}원")
            logger.info(f"  저가: {latest_price.low:,}원")
            logger.info(f"  종가: {latest_price.close:,}원")
            logger.info(f"  거래량: {latest_price.volume:,}주")

        # 3. 최근 30일 주가
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        prices = StockQueries.get_daily_prices(session, ticker, start_date, end_date)
        logger.info(f"\n최근 30일 주가 데이터: {len(prices)}건")

        # 4. 외국인 순매수 동향 (최근 5일)
        foreign_data = StockQueries.get_foreign_net_buying_days(session, ticker, days=5)
        if foreign_data:
            logger.info("\n외국인 순매수 (최근 5일):")
            for data in foreign_data:
                if data.foreigner_net is not None:
                    logger.info(f"  {data.date}: {data.foreigner_net:,}원")
                else:
                    logger.info(f"  {data.date}: 데이터 없음")

        # 5. 펀더멘탈 지표
        fundamentals = StockQueries.get_fundamentals(session, ticker, start_date, end_date)
        if fundamentals:
            latest_fund = fundamentals[-1]
            logger.info(f"\n펀더멘탈 지표 ({latest_fund.date}):")
            logger.info(f"  PER: {latest_fund.per}" if latest_fund.per else "  PER: N/A")
            logger.info(f"  PBR: {latest_fund.pbr}" if latest_fund.pbr else "  PBR: N/A")
            logger.info(f"  EPS: {latest_fund.eps:,}원" if latest_fund.eps else "  EPS: N/A")
            logger.info(f"  BPS: {latest_fund.bps:,}원" if latest_fund.bps else "  BPS: N/A")

        # 6. 현대로템 데이터도 조회
        logger.info("\n" + "=" * 60)
        ticker2 = '064350'
        stock2 = StockQueries.get_stock(session, ticker2)
        if stock2:
            logger.info(f"종목: {stock2.name} ({stock2.ticker})")
            latest_price2 = StockQueries.get_latest_price(session, ticker2)
            if latest_price2:
                logger.info(f"\n최근 주가 ({latest_price2.date}):")
                logger.info(f"  종가: {latest_price2.close:,}원")
                logger.info(f"  거래량: {latest_price2.volume:,}주")

if __name__ == '__main__':
    main()
