from sqlalchemy import Column, String, Integer, BigInteger, Date, DateTime, ForeignKey, Index, UniqueConstraint
from .stock import Base
from datetime import datetime

class MarketCap(Base):
    __tablename__ = 'market_cap'

    # 컬럼 정의
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey('stocks.ticker'), nullable=False, comment='종목코드')
    date = Column(Date, nullable=False, comment='거래일자')
    market_cap = Column(BigInteger, nullable=False, comment='시가총액 (원)')
    trading_volume = Column(BigInteger, nullable=False, comment='거래량')
    trading_value = Column(BigInteger, nullable=False, comment='거래대금 (원)')
    outstanding_shares = Column(BigInteger, nullable=False, comment='상장주식수')
    created_at = Column(DateTime, default=datetime.now, comment='등록일시')

    # 제약조건 및 인덱스
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='uq_ticker_date_cap'),
        Index('idx_ticker_date_cap', 'ticker', 'date'),
    )

    def __repr__(self):
        return f"<MarketCap(ticker='{self.ticker}', date='{self.date}', market_cap={self.market_cap})>"
