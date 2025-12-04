#!/usr/bin/env python3
"""
관심 종목 데이터 수집 스크립트

이 스크립트는 관심 종목(WATCHLIST)의 최신 데이터를 수집합니다.
일반적으로 generate_daily_report.py가 자동으로 호출하므로,
수동으로 실행할 필요는 없습니다.

사용법:
  python examples/collect_watchlist_data.py              # 최근 5일 데이터 수집
  python examples/collect_watchlist_data.py --today      # 오늘 데이터만 수집
  python examples/collect_watchlist_data.py --month      # 최근 30일 데이터 수집
  python examples/collect_watchlist_data.py --force      # 강제 재수집
"""

import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_fetcher import fetch_watchlist_data
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='관심 종목 데이터 수집')

    parser.add_argument(
        'date',
        nargs='?',
        default=None,
        help='수집 기준 날짜 (YYYYMMDD), 생략 시 오늘'
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--today',
        action='store_const',
        const='today',
        dest='mode',
        help='오늘 데이터만 수집'
    )
    mode_group.add_argument(
        '--month',
        action='store_const',
        const='month',
        dest='mode',
        help='최근 30일 데이터 수집'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='강제 재수집 (기존 데이터가 있어도 재수집)'
    )

    parser.set_defaults(mode='recent')  # 기본값: 최근 5일

    args = parser.parse_args()

    # 날짜 설정
    date_str = args.date if args.date else datetime.now().strftime('%Y%m%d')

    # 데이터 수집 실행
    try:
        result = fetch_watchlist_data(
            date_str=date_str,
            fetch_mode=args.mode,
            force=args.force
        )

        # 결과 요약
        print(f"\n{'='*60}")
        print(f"📊 수집 완료 요약")
        print(f"{'='*60}")
        print(f"날짜: {result['date']}")
        print(f"모드: {result['mode']}")
        print(f"성공: {result['total_success']}개")
        print(f"실패: {result['total_failed']}개")
        print(f"스킵: {result['skipped']}개")
        print(f"{'='*60}\n")

        if result['total_failed'] > 0:
            print("⚠️  일부 데이터 수집에 실패했습니다. 로그를 확인하세요.")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"데이터 수집 실패: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
