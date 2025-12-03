from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import date, datetime
from typing import List, Optional
import sys
import os

# 상대 경로 처리
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import (
    Stock, DailyPrice, MarketCap, Fundamental,
    TradingByInvestor, ShortSelling, ShortBalance
)

class StockQueries:
    """주식 데이터 조회 쿼리"""

    @staticmethod
    def get_stock(session: Session, ticker: str) -> Optional[Stock]:
        """종목 정보 조회"""
        return session.query(Stock).filter_by(ticker=ticker).first()

    @staticmethod
    def get_all_stocks(session: Session) -> List[Stock]:
        """전체 종목 조회"""
        return session.query(Stock).all()

    @staticmethod
    def get_daily_prices(
        session: Session,
        ticker: str,
        start_date: date = None,
        end_date: date = None
    ) -> List[DailyPrice]:
        """일별 주가 조회"""
        query = session.query(DailyPrice).filter_by(ticker=ticker)

        if start_date:
            query = query.filter(DailyPrice.date >= start_date)
        if end_date:
            query = query.filter(DailyPrice.date <= end_date)

        return query.order_by(DailyPrice.date).all()

    @staticmethod
    def get_latest_price(session: Session, ticker: str) -> Optional[DailyPrice]:
        """최근 주가 조회"""
        return session.query(DailyPrice).filter_by(ticker=ticker)\
            .order_by(desc(DailyPrice.date)).first()

    @staticmethod
    def get_market_caps(
        session: Session,
        ticker: str,
        start_date: date = None,
        end_date: date = None
    ) -> List[MarketCap]:
        """시가총액 데이터 조회"""
        query = session.query(MarketCap).filter_by(ticker=ticker)

        if start_date:
            query = query.filter(MarketCap.date >= start_date)
        if end_date:
            query = query.filter(MarketCap.date <= end_date)

        return query.order_by(MarketCap.date).all()

    @staticmethod
    def get_fundamentals(
        session: Session,
        ticker: str,
        start_date: date = None,
        end_date: date = None
    ) -> List[Fundamental]:
        """펀더멘탈 데이터 조회"""
        query = session.query(Fundamental).filter_by(ticker=ticker)

        if start_date:
            query = query.filter(Fundamental.date >= start_date)
        if end_date:
            query = query.filter(Fundamental.date <= end_date)

        return query.order_by(Fundamental.date).all()

    @staticmethod
    def get_trading_by_investor(
        session: Session,
        ticker: str,
        start_date: date = None,
        end_date: date = None
    ) -> List[TradingByInvestor]:
        """투자자별 매매 데이터 조회"""
        query = session.query(TradingByInvestor).filter_by(ticker=ticker)

        if start_date:
            query = query.filter(TradingByInvestor.date >= start_date)
        if end_date:
            query = query.filter(TradingByInvestor.date <= end_date)

        return query.order_by(TradingByInvestor.date).all()

    @staticmethod
    def get_foreign_net_buying_days(
        session: Session,
        ticker: str,
        days: int = 5
    ) -> List[TradingByInvestor]:
        """최근 N일간 외국인 순매수 데이터"""
        return session.query(TradingByInvestor).filter_by(ticker=ticker)\
            .order_by(desc(TradingByInvestor.date)).limit(days).all()

    @staticmethod
    def delete_old_data(session: Session, ticker: str, before_date: date) -> int:
        """특정 날짜 이전 데이터 삭제"""
        count = 0
        count = count + session.query(DailyPrice).filter(
            and_(DailyPrice.ticker == ticker, DailyPrice.date < before_date)
        ).delete()
        count = count + session.query(MarketCap).filter(
            and_(MarketCap.ticker == ticker, MarketCap.date < before_date)
        ).delete()
        session.commit()
        return count
