from sqlalchemy import Column, String, Integer, BigInteger, Date, DateTime, ForeignKey, Index, UniqueConstraint
from .stock import Base
from datetime import datetime

class DailyPrice(Base):
    __tablename__ = 'daily_price'

    # 컬럼 정의
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey('stocks.ticker'), nullable=False, comment='종목코드')
    date = Column(Date, nullable=False, comment='거래일자')
    open = Column(Integer, nullable=False, comment='시가')
    high = Column(Integer, nullable=False, comment='고가')
    low = Column(Integer, nullable=False, comment='저가')
    close = Column(Integer, nullable=False, comment='종가')
    volume = Column(BigInteger, nullable=False, comment='거래량')
    created_at = Column(DateTime, default=datetime.now, comment='등록일시')

    # 제약조건 및 인덱스
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='uq_ticker_date'),
        Index('idx_ticker_date', 'ticker', 'date'),
        Index('idx_date', 'date'),
    )

    def __repr__(self):
        return f"<DailyPrice(ticker='{self.ticker}', date='{self.date}', close={self.close})>"
