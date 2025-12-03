from sqlalchemy import Column, String, Integer, BigInteger, Date, DateTime, ForeignKey, Index, UniqueConstraint
from .stock import Base
from datetime import datetime

class ShortSelling(Base):
    __tablename__ = 'short_selling'

    # 컬럼 정의
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey('stocks.ticker'), nullable=False, comment='종목코드')
    date = Column(Date, nullable=False, comment='거래일자')
    short_volume = Column(BigInteger, nullable=True, comment='공매도 거래량')
    short_value = Column(BigInteger, nullable=True, comment='공매도 거래대금 (원)')
    created_at = Column(DateTime, default=datetime.now, comment='등록일시')

    # 제약조건 및 인덱스
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='uq_ticker_date_short'),
        Index('idx_ticker_date_short', 'ticker', 'date'),
    )

    def __repr__(self):
        return f"<ShortSelling(ticker='{self.ticker}', date='{self.date}', short_volume={self.short_volume})>"
