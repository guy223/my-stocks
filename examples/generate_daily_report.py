#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
일일 리포트 생성 스크립트

사용법:
  python examples/generate_daily_report.py                 # 오늘 날짜, 자동 데이터 수집
  python examples/generate_daily_report.py 20251203        # 특정 날짜, 자동 데이터 수집
  python examples/generate_daily_report.py --no-fetch      # 데이터 수집 없이 리포트만 생성
  python examples/generate_daily_report.py --fetch         # 강제로 최신 데이터 재수집
  python examples/generate_daily_report.py 20251203 --fetch  # 특정 날짜 + 강제 재수집
"""

import logging
import sys
import os
import argparse
from datetime import datetime, timedelta

# src 디렉토리를 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from report.daily_report import DailyReport
from data_fetcher import fetch_watchlist_data

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='일일 투자 리포트 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  %(prog)s                    # 오늘 날짜 리포트 (자동 데이터 수집)
  %(prog)s 20251203           # 2025-12-03 리포트 (자동 데이터 수집)
  %(prog)s --no-fetch         # 데이터 수집 없이 리포트만 생성
  %(prog)s --fetch            # 강제로 최신 데이터 재수집
  %(prog)s 20251203 --fetch   # 특정 날짜 + 강제 재수집
        """
    )

    parser.add_argument(
        'date',
        nargs='?',
        default=None,
        help='리포트 날짜 (YYYYMMDD 형식, 생략 시 오늘 날짜)'
    )

    fetch_group = parser.add_mutually_exclusive_group()
    fetch_group.add_argument(
        '--fetch',
        action='store_true',
        help='강제로 최신 데이터 재수집 (기존 데이터가 있어도 재수집)'
    )
    fetch_group.add_argument(
        '--no-fetch',
        action='store_true',
        help='데이터 수집 비활성화 (DB에 있는 데이터만 사용)'
    )

    parser.add_argument(
        '--mode',
        choices=['today', 'recent', 'month'],
        default='recent',
        help='데이터 수집 범위 (today: 당일만, recent: 최근 5일, month: 최근 30일)'
    )

    return parser.parse_args()

def main():
    """메인 실행 함수"""
    args = parse_arguments()

    # 날짜 설정
    if args.date:
        date_str = args.date
        # 날짜 형식 검증
        try:
            datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            logger.error(f"잘못된 날짜 형식: {date_str} (YYYYMMDD 형식이어야 합니다)")
            sys.exit(1)
    else:
        date_str = datetime.now().strftime('%Y%m%d')

    logger.info(f"일일 리포트 생성 시작: {date_str}")

    try:
        # 데이터 수집 단계
        if not args.no_fetch:
            logger.info("\n" + "="*60)
            logger.info("1단계: 관심 종목 최신 데이터 수집")
            logger.info("="*60)

            fetch_result = fetch_watchlist_data(
                date_str=date_str,
                fetch_mode=args.mode,
                force=args.fetch
            )

            # 수집 실패가 있어도 리포트는 생성 (기존 데이터 사용)
            if fetch_result['total_failed'] > 0:
                logger.warning(
                    f"⚠️  일부 데이터 수집 실패 ({fetch_result['total_failed']}개). "
                    f"기존 데이터로 리포트를 생성합니다."
                )
        else:
            logger.info("\n데이터 수집 스킵 (--no-fetch 옵션)")

        # 리포트 생성 단계
        logger.info("\n" + "="*60)
        logger.info("2단계: 일일 리포트 생성")
        logger.info("="*60 + "\n")

        report_generator = DailyReport()

        # 데이터 없으면 어제 날짜로 재시도
        try:
            report = report_generator.generate_report(date_str)
            actual_date = date_str
        except ValueError as e:
            if "데이터 없음" in str(e):
                # 어제 날짜로 재시도
                yesterday = datetime.strptime(date_str, '%Y%m%d') - timedelta(days=1)
                yesterday_str = yesterday.strftime('%Y%m%d')
                logger.warning(f"⚠️  {date_str} 데이터가 없습니다. {yesterday_str}로 리포트를 생성합니다.")
                report = report_generator.generate_report(yesterday_str)
                actual_date = yesterday_str
            else:
                raise

        # 콘솔 출력
        print(report)

        # 파일 저장
        filepath = report_generator.save_report(report, f"daily_report_{actual_date}.txt")

        logger.info(f"\n✅ 리포트 생성 완료: {filepath}")

    except KeyboardInterrupt:
        logger.info("\n\n사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ 리포트 생성 실패: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
