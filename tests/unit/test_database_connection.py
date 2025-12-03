"""
Database 클래스 테스트
"""

import pytest
from sqlalchemy import inspect
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from database.connection import Database
from models import Stock


class TestDatabase:
    """Database 클래스 테스트"""

    def test_init_with_default_url(self):
        """기본 SQLite URL로 초기화"""
        db = Database()
        assert db.engine is not None
        assert 'stocks.db' in str(db.engine.url)

    def test_init_with_custom_url(self):
        """커스텀 URL로 초기화 (인메모리)"""
        db = Database(db_url='sqlite:///:memory:')
        assert db.engine is not None
        assert str(db.engine.url) == 'sqlite:///:memory:'

    def test_create_tables(self, test_database):
        """7개 테이블 생성 확인"""
        # 테이블 존재 확인
        inspector = inspect(test_database.engine)
        tables = inspector.get_table_names()

        expected_tables = [
            'stocks', 'daily_price', 'market_cap', 'fundamental',
            'trading_by_investor', 'short_selling', 'short_balance'
        ]

        for table in expected_tables:
            assert table in tables, f"테이블 {table}이 생성되지 않았습니다"

    def test_drop_tables(self):
        """테이블 삭제 확인"""
        db = Database(db_url='sqlite:///:memory:')
        db.create_tables()

        # 테이블이 생성되었는지 확인
        inspector = inspect(db.engine)
        assert len(inspector.get_table_names()) > 0

        # 테이블 삭제
        db.drop_tables()

        # 테이블이 삭제되었는지 확인
        inspector = inspect(db.engine)
        assert len(inspector.get_table_names()) == 0

    def test_get_session_context_manager(self, test_database):
        """세션 컨텍스트 매니저 사용"""
        session_id = None

        with test_database.get_session() as session:
            # 세션 사용 가능 확인
            assert session is not None
            assert session.is_active

            # 데이터 저장
            stock = Stock(ticker='005930', name='삼성전자', market='KOSPI')
            session.add(stock)
            session.commit()
            session_id = id(session)

        # 컨텍스트 종료 후 세션 닫힘 확인
        # (세션 객체는 여전히 참조 가능하지만 닫힌 상태)

        # 데이터 영속성 확인
        with test_database.get_session() as new_session:
            result = new_session.query(Stock).filter_by(ticker='005930').first()
            assert result is not None
            assert result.name == '삼성전자'

    def test_get_session_auto_close_on_error(self, test_database):
        """예외 발생 시에도 세션 자동 종료"""
        try:
            with test_database.get_session() as session:
                stock = Stock(ticker='005930', name='삼성전자', market='KOSPI')
                session.add(stock)
                session.commit()

                # 의도적 예외 발생
                raise ValueError("테스트 예외")
        except ValueError:
            pass

        # 첫 번째 데이터는 commit 되었으므로 존재
        with test_database.get_session() as session:
            result = session.query(Stock).filter_by(ticker='005930').first()
            assert result is not None

    def test_get_new_session(self, test_database):
        """독립적인 세션 생성"""
        session1 = test_database.get_new_session()
        session2 = test_database.get_new_session()

        # 서로 다른 세션 객체
        assert id(session1) != id(session2)

        # 수동으로 세션 종료 필요
        session1.close()
        session2.close()

    def test_transaction_commit(self, test_database):
        """트랜잭션 커밋 확인"""
        with test_database.get_session() as session:
            stock = Stock(ticker='005930', name='삼성전자', market='KOSPI')
            session.add(stock)
            session.commit()

        # 새 세션에서 데이터 조회 가능
        with test_database.get_session() as session:
            result = session.query(Stock).filter_by(ticker='005930').first()
            assert result is not None
            assert result.name == '삼성전자'

    def test_transaction_rollback(self, test_database):
        """트랜잭션 롤백 확인"""
        with test_database.get_session() as session:
            stock = Stock(ticker='005930', name='삼성전자', market='KOSPI')
            session.add(stock)
            # commit하지 않고 롤백
            session.rollback()

        # 롤백 후 데이터 미존재
        with test_database.get_session() as session:
            result = session.query(Stock).filter_by(ticker='005930').first()
            assert result is None

    def test_multiple_sessions_independence(self, test_database):
        """여러 세션의 독립성 확인"""
        # 첫 번째 세션에서 데이터 추가
        with test_database.get_session() as session1:
            stock1 = Stock(ticker='005930', name='삼성전자', market='KOSPI')
            session1.add(stock1)
            session1.commit()

        # 두 번째 세션에서 다른 데이터 추가
        with test_database.get_session() as session2:
            stock2 = Stock(ticker='000660', name='SK하이닉스', market='KOSPI')
            session2.add(stock2)
            session2.commit()

        # 세 번째 세션에서 모두 조회 가능
        with test_database.get_session() as session3:
            stocks = session3.query(Stock).all()
            assert len(stocks) == 2
            tickers = [s.ticker for s in stocks]
            assert '005930' in tickers
            assert '000660' in tickers
