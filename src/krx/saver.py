import logging
import sys
import os
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

# 상대 경로 처리
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import (
    Stock, DailyPrice, MarketCap, Fundamental,
    TradingByInvestor, ShortSelling, ShortBalance
)

logger = logging.getLogger(__name__)

class DataSaver:
    """수집한 데이터를 데이터베이스에 저장"""

    def __init__(self, db_session: Session):
        self.session = db_session

    def save_stock(self, ticker: str, name: str, market: str) -> Stock:
        """
        종목 정보 저장

        Args:
            ticker: 종목코드
            name: 종목명
            market: 시장 (KOSPI/KOSDAQ)

        Returns:
            저장된 Stock 객체
        """
        stock = self.session.query(Stock).filter_by(ticker=ticker).first()
        if not stock:
            stock = Stock(ticker=ticker, name=name, market=market)
            self.session.add(stock)
            self.session.commit()
            logger.info(f"종목 등록: {ticker} ({name})")
        return stock

    def save_daily_prices(self, ticker: str, df: pd.DataFrame) -> int:
        """
        일별 주가 데이터 저장

        Args:
            ticker: 종목코드
            df: OHLCV 데이터프레임

        Returns:
            저장된 레코드 수
        """
        if df.empty:
            logger.warning(f"빈 데이터프레임: {ticker}")
            return 0

        saved_count = 0
        for date, row in df.iterrows():
            try:
                price = DailyPrice(
                    ticker=ticker,
                    date=date.date() if hasattr(date, 'date') else date,
                    open=int(row['시가']),
                    high=int(row['고가']),
                    low=int(row['저가']),
                    close=int(row['종가']),
                    volume=int(row['거래량'])
                )
                self.session.add(price)
                self.session.commit()
                saved_count = saved_count + 1
            except IntegrityError:
                self.session.rollback()
                logger.debug(f"중복 데이터 스킵: {ticker} {date}")
            except Exception as e:
                self.session.rollback()
                logger.error(f"저장 실패: {ticker} {date} - {e}")

        logger.info(f"일별 주가 저장 완료: {ticker} ({saved_count}건)")
        return saved_count

    def save_market_caps(self, ticker: str, df: pd.DataFrame) -> int:
        """
        시가총액 데이터 저장

        Args:
            ticker: 종목코드
            df: 시가총액 데이터프레임

        Returns:
            저장된 레코드 수
        """
        if df.empty:
            return 0

        saved_count = 0
        for date, row in df.iterrows():
            try:
                cap = MarketCap(
                    ticker=ticker,
                    date=date.date() if hasattr(date, 'date') else date,
                    market_cap=int(row['시가총액']),
                    trading_volume=int(row['거래량']),
                    trading_value=int(row['거래대금']),
                    outstanding_shares=int(row['상장주식수'])
                )
                self.session.add(cap)
                self.session.commit()
                saved_count = saved_count + 1
            except IntegrityError:
                self.session.rollback()
            except Exception as e:
                self.session.rollback()
                logger.error(f"시가총액 저장 실패: {ticker} {date} - {e}")

        logger.info(f"시가총액 저장 완료: {ticker} ({saved_count}건)")
        return saved_count

    def save_fundamentals(self, ticker: str, df: pd.DataFrame) -> int:
        """
        펀더멘탈 데이터 저장

        Args:
            ticker: 종목코드
            df: 펀더멘탈 데이터프레임

        Returns:
            저장된 레코드 수
        """
        if df.empty:
            return 0

        saved_count = 0
        for date, row in df.iterrows():
            try:
                fund = Fundamental(
                    ticker=ticker,
                    date=date.date() if hasattr(date, 'date') else date,
                    bps=int(row['BPS']) if pd.notna(row['BPS']) else None,
                    per=float(row['PER']) if pd.notna(row['PER']) else None,
                    pbr=float(row['PBR']) if pd.notna(row['PBR']) else None,
                    eps=int(row['EPS']) if pd.notna(row['EPS']) else None,
                    div=float(row['DIV']) if pd.notna(row['DIV']) else None,
                    dps=int(row['DPS']) if pd.notna(row['DPS']) else None
                )
                self.session.add(fund)
                self.session.commit()
                saved_count = saved_count + 1
            except IntegrityError:
                self.session.rollback()
            except Exception as e:
                self.session.rollback()
                logger.error(f"펀더멘탈 저장 실패: {ticker} {date} - {e}")

        logger.info(f"펀더멘탈 저장 완료: {ticker} ({saved_count}건)")
        return saved_count

    def save_trading_by_investor(self, ticker: str, df: pd.DataFrame) -> int:
        """
        투자자별 매매 동향 저장

        Args:
            ticker: 종목코드
            df: 투자자별 매매 데이터프레임

        Returns:
            저장된 레코드 수
        """
        if df.empty:
            return 0

        saved_count = 0
        for date, row in df.iterrows():
            try:
                trading = TradingByInvestor(
                    ticker=ticker,
                    date=date.date() if hasattr(date, 'date') else date,
                    institution_net=int(row['기관합계']) if '기관합계' in row else None,
                    foreigner_net=int(row['외국인합계']) if '외국인합계' in row else None,
                    individual_net=int(row['개인']) if '개인' in row else None,
                    financial_net=int(row['금융투자']) if '금융투자' in row else None,
                    insurance_net=int(row['보험']) if '보험' in row else None,
                    trust_net=int(row['투신']) if '투신' in row else None,
                    private_equity_net=int(row['사모']) if '사모' in row else None,
                    pension_net=int(row['연기금']) if '연기금' in row else None
                )
                self.session.add(trading)
                self.session.commit()
                saved_count = saved_count + 1
            except IntegrityError:
                self.session.rollback()
            except Exception as e:
                self.session.rollback()
                logger.error(f"투자자별 매매 저장 실패: {ticker} {date} - {e}")

        logger.info(f"투자자별 매매 저장 완료: {ticker} ({saved_count}건)")
        return saved_count

    def save_short_selling(self, ticker: str, df: pd.DataFrame) -> int:
        """
        공매도 데이터 저장

        Args:
            ticker: 종목코드
            df: 공매도 데이터프레임

        Returns:
            저장된 레코드 수
        """
        if df.empty:
            return 0

        saved_count = 0
        for date, row in df.iterrows():
            try:
                short = ShortSelling(
                    ticker=ticker,
                    date=date.date() if hasattr(date, 'date') else date,
                    short_volume=int(row['거래량']) if '거래량' in row else None,
                    short_value=int(row['거래대금']) if '거래대금' in row else None
                )
                self.session.add(short)
                self.session.commit()
                saved_count = saved_count + 1
            except IntegrityError:
                self.session.rollback()
            except Exception as e:
                self.session.rollback()
                logger.error(f"공매도 저장 실패: {ticker} {date} - {e}")

        logger.info(f"공매도 저장 완료: {ticker} ({saved_count}건)")
        return saved_count

    def save_short_balance(self, ticker: str, df: pd.DataFrame) -> int:
        """
        공매도 잔고 저장

        Args:
            ticker: 종목코드
            df: 공매도 잔고 데이터프레임

        Returns:
            저장된 레코드 수
        """
        if df.empty:
            return 0

        saved_count = 0
        for date, row in df.iterrows():
            try:
                balance = ShortBalance(
                    ticker=ticker,
                    date=date.date() if hasattr(date, 'date') else date,
                    balance_quantity=int(row['잔고수량']) if '잔고수량' in row else None,
                    balance_value=int(row['잔고금액']) if '잔고금액' in row else None,
                    balance_ratio=float(row['잔고비율']) if '잔고비율' in row else None
                )
                self.session.add(balance)
                self.session.commit()
                saved_count = saved_count + 1
            except IntegrityError:
                self.session.rollback()
            except Exception as e:
                self.session.rollback()
                logger.error(f"공매도 잔고 저장 실패: {ticker} {date} - {e}")

        logger.info(f"공매도 잔고 저장 완료: {ticker} ({saved_count}건)")
        return saved_count
