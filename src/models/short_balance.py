from sqlalchemy import Column, String, Integer, BigInteger, Date, DateTime, Float, ForeignKey, Index, UniqueConstraint
from .stock import Base
from datetime import datetime

class ShortBalance(Base):
    __tablename__ = 'short_balance'

    # 컬럼 정의
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey('stocks.ticker'), nullable=False, comment='종목코드')
    date = Column(Date, nullable=False, comment='거래일자')
    balance_quantity = Column(BigInteger, nullable=True, comment='공매도 잔고 수량')
    balance_value = Column(BigInteger, nullable=True, comment='공매도 잔고 금액 (원)')
    balance_ratio = Column(Float, nullable=True, comment='공매도 잔고 비율 (%)')
    created_at = Column(DateTime, default=datetime.now, comment='등록일시')

    # 제약조건 및 인덱스
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='uq_ticker_date_balance'),
        Index('idx_ticker_date_balance', 'ticker', 'date'),
    )

    def __repr__(self):
        return f"<ShortBalance(ticker='{self.ticker}', date='{self.date}', balance_ratio={self.balance_ratio})>"
