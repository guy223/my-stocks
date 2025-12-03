import time
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd
from pykrx import stock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

class KRXClient:
    """KRX 데이터 수집 클라이언트"""

    # API 호출 간격 (초) - KRX 서버 차단 방지
    API_DELAY = 1.0

    # 재시도 설정
    MAX_RETRIES = 3
    RETRY_DELAY = 5.0

    def __init__(self, db_session: Session):
        """
        Args:
            db_session: SQLAlchemy 세션
        """
        self.session = db_session
        self.last_api_call = None

    def _wait_for_rate_limit(self):
        """API 호출 제한을 위한 대기"""
        if self.last_api_call:
            elapsed = time.time() - self.last_api_call
            if elapsed < self.API_DELAY:
                time.sleep(self.API_DELAY - elapsed)
        self.last_api_call = time.time()

    def _retry_on_error(self, func, *args, **kwargs):
        """에러 발생 시 재시도 로직"""
        for attempt in range(self.MAX_RETRIES):
            try:
                self._wait_for_rate_limit()
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.warning(f"API 호출 실패 (시도 {attempt + 1}/{self.MAX_RETRIES}): {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error(f"최대 재시도 횟수 초과: {func.__name__}")
                    raise

    def get_ohlcv(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        일별 OHLCV 데이터 조회

        Args:
            ticker: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)

        Returns:
            OHLCV 데이터프레임
        """
        logger.info(f"OHLCV 조회: {ticker} ({start_date} ~ {end_date})")
        return self._retry_on_error(
            stock.get_market_ohlcv,
            start_date, end_date, ticker
        )

    def get_market_cap(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        시가총액 및 거래 정보 조회

        Args:
            ticker: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)

        Returns:
            시가총액 데이터프레임
        """
        logger.info(f"시가총액 조회: {ticker} ({start_date} ~ {end_date})")
        return self._retry_on_error(
            stock.get_market_cap,
            start_date, end_date, ticker
        )

    def get_fundamental(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        펀더멘탈 지표 조회

        Args:
            ticker: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)

        Returns:
            펀더멘탈 데이터프레임
        """
        logger.info(f"펀더멘탈 조회: {ticker} ({start_date} ~ {end_date})")
        return self._retry_on_error(
            stock.get_market_fundamental,
            start_date, end_date, ticker
        )

    def get_trading_by_investor(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        투자자별 매매 동향 조회

        Args:
            ticker: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)

        Returns:
            투자자별 매매 데이터프레임
        """
        logger.info(f"투자자별 매매 조회: {ticker} ({start_date} ~ {end_date})")
        return self._retry_on_error(
            stock.get_market_trading_value_by_date,
            start_date, end_date, ticker
        )

    def get_short_selling_volume(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        공매도 거래량 조회

        Args:
            ticker: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)

        Returns:
            공매도 거래량 데이터프레임
        """
        logger.info(f"공매도 거래량 조회: {ticker} ({start_date} ~ {end_date})")
        try:
            df = self._retry_on_error(
                stock.get_shorting_volume_by_date,
                start_date, end_date, ticker
            )
            return df
        except Exception as e:
            logger.warning(f"공매도 거래량 조회 실패: {e}")
            return pd.DataFrame()

    def get_short_balance(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        공매도 잔고 조회

        Args:
            ticker: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)

        Returns:
            공매도 잔고 데이터프레임
        """
        logger.info(f"공매도 잔고 조회: {ticker} ({start_date} ~ {end_date})")
        try:
            df = self._retry_on_error(
                stock.get_shorting_balance_by_date,
                start_date, end_date, ticker
            )
            return df
        except Exception as e:
            logger.warning(f"공매도 잔고 조회 실패: {e}")
            return pd.DataFrame()
