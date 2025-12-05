#!/usr/bin/env python3
"""
CLI 명령어 엔트리 포인트

uv run 명령어로 실행 가능한 CLI 인터페이스를 제공합니다.
"""

import sys
import os


def report_command():
    """
    일일 리포트 생성 CLI

    사용법:
        uv run report
        uv run report 20251203
        uv run report --fetch
        uv run report --no-fetch
        uv run report --mode month
    """
    # examples 디렉토리의 스크립트 임포트
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    examples_dir = os.path.join(project_root, 'examples')
    sys.path.insert(0, examples_dir)

    from generate_daily_report import main
    main()


def test_command():
    """
    단위 테스트 실행 CLI

    사용법:
        uv run test-stocks
        uv run test-stocks tests/unit/test_krx_client.py
        uv run test-stocks -v
        uv run test-stocks --cov=src
    """
    import pytest

    # sys.argv[0]는 스크립트 이름이므로 제거하고 나머지 인자만 전달
    args = sys.argv[1:]

    # 인자가 없으면 기본 pytest 설정 사용
    sys.exit(pytest.main(args))


def collect_command():
    """
    관심 종목 데이터 수집 CLI

    사용법:
        uv run collect
        uv run collect --today
        uv run collect --month
        uv run collect --force
        uv run collect 20251203
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    examples_dir = os.path.join(project_root, 'examples')
    sys.path.insert(0, examples_dir)

    from collect_watchlist_data import main
    main()


def query_command():
    """
    데이터베이스 조회 CLI

    사용법:
        uv run query
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    examples_dir = os.path.join(project_root, 'examples')
    sys.path.insert(0, examples_dir)

    from query_example import main
    main()


# 직접 실행 시 도움말 표시
if __name__ == '__main__':
    print("""
my-stocks CLI 명령어
==================

사용 가능한 명령어:
  uv run report        일일 리포트 생성
  uv run test-stocks   단위 테스트 실행
  uv run collect       데이터 수집
  uv run query         데이터 조회

자세한 사용법:
  uv run report --help
  uv run test-stocks --help
  uv run collect --help
    """)
