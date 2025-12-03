from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stocks'

    # 컬럼 정의
    ticker = Column(String(10), primary_key=True, comment='종목코드')
    name = Column(String(100), nullable=False, comment='종목명')
    market = Column(String(20), nullable=False, comment='시장구분 (KOSPI/KOSDAQ)')
    created_at = Column(DateTime, default=datetime.now, comment='등록일시')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='수정일시')

    # 인덱스
    __table_args__ = (
        Index('idx_market', 'market'),
    )

    def __repr__(self):
        return f"<Stock(ticker='{self.ticker}', name='{self.name}', market='{self.market}')>"
