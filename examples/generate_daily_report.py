#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
일일 리포트 생성 스크립트

사용법:
  python examples/generate_daily_report.py              # 오늘 날짜로 생성
  python examples/generate_daily_report.py 20251203     # 특정 날짜로 생성
"""

import logging
import sys
import os
from datetime import datetime

# src 디렉토리를 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from report.daily_report import DailyReport

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """메인 실행 함수"""

    # 날짜 인자 확인
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        date_str = datetime.now().strftime('%Y%m%d')

    logger.info(f"일일 리포트 생성 시작: {date_str}")

    try:
        # 리포트 생성
        report_generator = DailyReport()
        report = report_generator.generate_report(date_str)

        # 콘솔 출력
        print(report)

        # 파일 저장
        filepath = report_generator.save_report(report)

        logger.info(f"리포트 생성 완료: {filepath}")

    except Exception as e:
        logger.error(f"리포트 생성 실패: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
