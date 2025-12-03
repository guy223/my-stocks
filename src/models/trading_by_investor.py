from sqlalchemy import Column, String, Integer, BigInteger, Date, DateTime, ForeignKey, Index, UniqueConstraint
from .stock import Base
from datetime import datetime

class TradingByInvestor(Base):
    __tablename__ = 'trading_by_investor'

    # 컬럼 정의
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey('stocks.ticker'), nullable=False, comment='종목코드')
    date = Column(Date, nullable=False, comment='거래일자')

    # 매매 주체별 순매수 금액 (단위: 원)
    institution_net = Column(BigInteger, nullable=True, comment='기관 순매수')
    foreigner_net = Column(BigInteger, nullable=True, comment='외국인 순매수')
    individual_net = Column(BigInteger, nullable=True, comment='개인 순매수')

    # 세부 기관별
    financial_net = Column(BigInteger, nullable=True, comment='금융투자 순매수')
    insurance_net = Column(BigInteger, nullable=True, comment='보험 순매수')
    trust_net = Column(BigInteger, nullable=True, comment='투신 순매수')
    private_equity_net = Column(BigInteger, nullable=True, comment='사모 순매수')
    pension_net = Column(BigInteger, nullable=True, comment='연기금 순매수')

    created_at = Column(DateTime, default=datetime.now, comment='등록일시')

    # 제약조건 및 인덱스
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='uq_ticker_date_trading'),
        Index('idx_ticker_date_trading', 'ticker', 'date'),
        Index('idx_foreigner_net', 'foreigner_net'),
    )

    def __repr__(self):
        return f"<TradingByInvestor(ticker='{self.ticker}', date='{self.date}', foreigner_net={self.foreigner_net})>"
