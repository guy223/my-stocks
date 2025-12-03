from sqlalchemy import Column, String, Integer, Date, DateTime, Float, ForeignKey, Index, UniqueConstraint
from .stock import Base
from datetime import datetime

class Fundamental(Base):
    __tablename__ = 'fundamental'

    # 컬럼 정의
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey('stocks.ticker'), nullable=False, comment='종목코드')
    date = Column(Date, nullable=False, comment='거래일자')
    bps = Column(Integer, nullable=True, comment='주당순자산가치 (원)')
    per = Column(Float, nullable=True, comment='주가수익률')
    pbr = Column(Float, nullable=True, comment='주가순자산비율')
    eps = Column(Integer, nullable=True, comment='주당순이익 (원)')
    div = Column(Float, nullable=True, comment='배당수익률')
    dps = Column(Integer, nullable=True, comment='주당배당금 (원)')
    created_at = Column(DateTime, default=datetime.now, comment='등록일시')

    # 제약조건 및 인덱스
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='uq_ticker_date_fund'),
        Index('idx_ticker_date_fund', 'ticker', 'date'),
    )

    def __repr__(self):
        return f"<Fundamental(ticker='{self.ticker}', date='{self.date}', per={self.per}, pbr={self.pbr})>"
