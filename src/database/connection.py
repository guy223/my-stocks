import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

# 상대 경로 처리
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import Base

logger = logging.getLogger(__name__)

class Database:
    """데이터베이스 연결 및 세션 관리"""

    def __init__(self, db_url: str = None):
        """
        Args:
            db_url: 데이터베이스 URL (기본값: SQLite)
        """
        if db_url is None:
            # 기본 SQLite 경로
            db_dir = os.path.join(os.path.dirname(__file__), '../../data')
            os.makedirs(db_dir, exist_ok=True)
            db_url = f'sqlite:///{db_dir}/stocks.db'

        self.engine = create_engine(
            db_url,
            echo=False,  # SQL 로그 출력 여부
            pool_pre_ping=True,  # 연결 유효성 검사
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        logger.info(f"데이터베이스 연결: {db_url}")

    def create_tables(self):
        """모든 테이블 생성"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("데이터베이스 테이블 생성 완료")

    def drop_tables(self):
        """모든 테이블 삭제 (주의!)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("데이터베이스 테이블 삭제 완료")

    @contextmanager
    def get_session(self) -> Session:
        """세션 컨텍스트 매니저"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def get_new_session(self) -> Session:
        """새 세션 생성"""
        return self.SessionLocal()
