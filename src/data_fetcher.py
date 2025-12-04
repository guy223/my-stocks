#!/usr/bin/env python3
"""
데이터 수집 유틸리티 모듈

관심 종목의 최신 데이터를 수집하는 재사용 가능한 함수들을 제공합니다.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import logging

sys.path.insert(0, os.path.dirname(__file__))

from database.connection import Database
from database.queries import StockQueries
from krx.client import KRXClient
from krx.saver import DataSaver
from config import WATCHLIST

logger = logging.getLogger(__name__)


def check_data_exists(ticker: str, date_str: str) -> bool:
    """
    특정 날짜의 데이터가 DB에 있는지 확인

    Args:
        ticker: 종목 코드
        date_str: 날짜 (YYYYMMDD)

    Returns:
        데이터 존재 여부
    """
    target_date = datetime.strptime(date_str, '%Y%m%d').date()

    with Database().get_session() as session:
        latest = StockQueries.get_latest_price(session, ticker)
        if latest and latest.date == target_date:
            return True
    return False


def fetch_stock_data(
    ticker: str,
    name: str,
    market: str,
    date_str: str,
    fetch_mode: str = 'today'
) -> dict:
    """
    특정 종목의 데이터 수집

    Args:
        ticker: 종목 코드
        name: 종목명
        market: 시장 (KOSPI/KOSDAQ)
        date_str: 기준 날짜 (YYYYMMDD)
        fetch_mode: 수집 모드
            - 'today': 당일 데이터만
            - 'recent': 최근 5일
            - 'month': 최근 30일

    Returns:
        수집 결과 딕셔너리
    """
    # 날짜 범위 계산
    end_date = datetime.strptime(date_str, '%Y%m%d')

    if fetch_mode == 'today':
        start_date = end_date
    elif fetch_mode == 'recent':
        start_date = end_date - timedelta(days=5)
    else:  # 'month'
        start_date = end_date - timedelta(days=30)

    date_str_start = start_date.strftime("%Y%m%d")
    date_str_end = end_date.strftime("%Y%m%d")

    result = {
        'ticker': ticker,
        'name': name,
        'success': True,
        'counts': {},
        'errors': []
    }

    logger.info(f"📊 {name} ({ticker}) 데이터 수집 중... ({date_str_start} ~ {date_str_end})")

    try:
        with Database().get_session() as session:
            client = KRXClient(session)
            saver = DataSaver(session)

            # 1. 종목 정보 저장
            saver.save_stock(ticker, name, market)

            # 2. 일별 주가 데이터
            try:
                ohlcv = client.get_ohlcv(ticker, date_str_start, date_str_end)
                if not ohlcv.empty:
                    count = saver.save_daily_prices(ticker, ohlcv)
                    result['counts']['daily_price'] = count
                    logger.info(f"  ✓ 일별 주가: {count}건")
            except Exception as e:
                logger.warning(f"  ✗ 일별 주가 실패: {e}")
                result['errors'].append(f"일별 주가: {e}")

            # 3. 시가총액 데이터
            try:
                market_cap = client.get_market_cap(ticker, date_str_start, date_str_end)
                if not market_cap.empty:
                    count = saver.save_market_caps(ticker, market_cap)
                    result['counts']['market_cap'] = count
                    logger.info(f"  ✓ 시가총액: {count}건")
            except Exception as e:
                logger.warning(f"  ✗ 시가총액 실패: {e}")
                result['errors'].append(f"시가총액: {e}")

            # 4. 펀더멘탈 데이터
            try:
                fundamental = client.get_fundamental(ticker, date_str_start, date_str_end)
                if not fundamental.empty:
                    count = saver.save_fundamentals(ticker, fundamental)
                    result['counts']['fundamental'] = count
                    logger.info(f"  ✓ 펀더멘탈: {count}건")
            except Exception as e:
                logger.warning(f"  ✗ 펀더멘탈 실패: {e}")
                result['errors'].append(f"펀더멘탈: {e}")

            # 5. 투자자별 매매 데이터
            try:
                trading = client.get_trading_by_investor(ticker, date_str_start, date_str_end)
                if not trading.empty:
                    count = saver.save_trading_by_investor(ticker, trading)
                    result['counts']['trading'] = count
                    logger.info(f"  ✓ 투자자별 매매: {count}건")
            except Exception as e:
                logger.warning(f"  ✗ 투자자별 매매 실패: {e}")
                result['errors'].append(f"투자자별 매매: {e}")

            # 6. 공매도 데이터 (선택적)
            try:
                short_selling = client.get_short_selling_volume(ticker, date_str_start, date_str_end)
                if not short_selling.empty:
                    count = saver.save_short_selling(ticker, short_selling)
                    result['counts']['short_selling'] = count
            except Exception:
                pass  # 공매도는 실패해도 무시

            try:
                short_balance = client.get_short_balance(ticker, date_str_start, date_str_end)
                if not short_balance.empty:
                    count = saver.save_short_balance(ticker, short_balance)
                    result['counts']['short_balance'] = count
            except Exception:
                pass  # 공매도는 실패해도 무시

    except Exception as e:
        logger.error(f"  ✗ {name} 수집 중 오류: {e}")
        result['success'] = False
        result['errors'].append(f"전체 수집 실패: {e}")

    return result


def fetch_watchlist_data(
    date_str: Optional[str] = None,
    fetch_mode: str = 'today',
    force: bool = False
) -> dict:
    """
    관심 종목 리스트의 데이터 수집

    Args:
        date_str: 기준 날짜 (YYYYMMDD), None이면 오늘
        fetch_mode: 수집 모드 ('today', 'recent', 'month')
        force: True면 기존 데이터가 있어도 재수집

    Returns:
        전체 수집 결과 딕셔너리
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y%m%d')

    logger.info(f"\n{'='*60}")
    logger.info(f"📈 관심 종목 데이터 수집 시작: {date_str}")
    logger.info(f"   모드: {fetch_mode}, 강제수집: {force}")
    logger.info(f"{'='*60}")

    results = {
        'date': date_str,
        'mode': fetch_mode,
        'stocks': [],
        'total_success': 0,
        'total_failed': 0,
        'skipped': 0
    }

    for ticker, name, market in WATCHLIST:
        # 스마트 모드: 데이터가 있으면 스킵
        if not force and check_data_exists(ticker, date_str):
            logger.info(f"⏭️  {name} ({ticker}): 데이터 이미 존재 (스킵)")
            results['skipped'] += 1
            continue

        # 데이터 수집
        stock_result = fetch_stock_data(ticker, name, market, date_str, fetch_mode)
        results['stocks'].append(stock_result)

        if stock_result['success']:
            results['total_success'] += 1
        else:
            results['total_failed'] += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"✅ 수집 완료: 성공 {results['total_success']}개, "
               f"실패 {results['total_failed']}개, "
               f"스킵 {results['skipped']}개")
    logger.info(f"{'='*60}\n")

    return results
