import logging
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
from pykrx import stock

# 상대 경로 처리
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class MarketSummary:
    """시장 전체 동향 분석"""

    def __init__(self):
        pass

    def get_index_info(self, date_str: str) -> dict:
        """
        KOSPI, KOSDAQ 지수 정보 조회

        Args:
            date_str: 날짜 (YYYYMMDD)

        Returns:
            지수 정보 딕셔너리
        """
        try:
            # 전일 대비 계산을 위해 전일 날짜도 필요
            date = datetime.strptime(date_str, '%Y%m%d')
            prev_date = date - timedelta(days=1)

            # 주말 고려 (최대 3일 전까지 확인)
            for i in range(1, 4):
                prev_date_str = (date - timedelta(days=i)).strftime('%Y%m%d')
                try:
                    kospi_prev = stock.get_index_ohlcv(prev_date_str, prev_date_str, "1001")
                    if not kospi_prev.empty:
                        break
                except:
                    continue

            # KOSPI 지수
            kospi = stock.get_index_ohlcv(date_str, date_str, "1001")
            kosdaq = stock.get_index_ohlcv(date_str, date_str, "2001")

            result = {}

            if not kospi.empty:
                kospi_close = kospi.iloc[0]['종가']
                kospi_volume = kospi.iloc[0]['거래량']

                # 전일 대비 계산
                try:
                    kospi_prev_close = kospi_prev.iloc[0]['종가']
                    kospi_change = kospi_close - kospi_prev_close
                    kospi_change_pct = (kospi_change / kospi_prev_close) * 100
                except:
                    kospi_change = 0
                    kospi_change_pct = 0

                result['kospi'] = {
                    'close': kospi_close,
                    'change': kospi_change,
                    'change_pct': kospi_change_pct,
                    'volume': kospi_volume
                }

            if not kosdaq.empty:
                kosdaq_close = kosdaq.iloc[0]['종가']
                kosdaq_volume = kosdaq.iloc[0]['거래량']

                try:
                    kosdaq_prev = stock.get_index_ohlcv(prev_date_str, prev_date_str, "2001")
                    kosdaq_prev_close = kosdaq_prev.iloc[0]['종가']
                    kosdaq_change = kosdaq_close - kosdaq_prev_close
                    kosdaq_change_pct = (kosdaq_change / kosdaq_prev_close) * 100
                except:
                    kosdaq_change = 0
                    kosdaq_change_pct = 0

                result['kosdaq'] = {
                    'close': kosdaq_close,
                    'change': kosdaq_change,
                    'change_pct': kosdaq_change_pct,
                    'volume': kosdaq_volume
                }

            return result

        except Exception as e:
            logger.error(f"지수 정보 조회 실패: {e}")
            return {}

    def get_top_gainers(self, date_str: str, market: str = "KOSPI", n: int = 5) -> pd.DataFrame:
        """
        등락률 상위 종목 조회

        Args:
            date_str: 날짜 (YYYYMMDD)
            market: 시장 (KOSPI/KOSDAQ)
            n: 조회할 종목 수

        Returns:
            상위 종목 데이터프레임
        """
        try:
            df = stock.get_market_ohlcv_by_ticker(date_str, market=market)
            if df.empty:
                return pd.DataFrame()

            # 등락률 계산
            df['등락률'] = ((df['종가'] - df['시가']) / df['시가'] * 100).round(2)

            # 거래대금 계산
            df['거래대금'] = df['종가'] * df['거래량']

            # 상위 N개 선택
            top = df.nlargest(n, '등락률')[['종가', '등락률', '거래량', '거래대금']]

            # 종목명 추가
            tickers = stock.get_market_ticker_list(date_str, market=market)
            ticker_names = {}
            for ticker in top.index:
                try:
                    name = stock.get_market_ticker_name(ticker)
                    ticker_names[ticker] = name
                except:
                    ticker_names[ticker] = ticker

            top.insert(0, '종목명', top.index.map(ticker_names))

            return top

        except Exception as e:
            logger.error(f"급등 종목 조회 실패: {e}")
            return pd.DataFrame()

    def get_top_losers(self, date_str: str, market: str = "KOSPI", n: int = 5) -> pd.DataFrame:
        """
        등락률 하위 종목 조회

        Args:
            date_str: 날짜 (YYYYMMDD)
            market: 시장 (KOSPI/KOSDAQ)
            n: 조회할 종목 수

        Returns:
            하위 종목 데이터프레임
        """
        try:
            df = stock.get_market_ohlcv_by_ticker(date_str, market=market)
            if df.empty:
                return pd.DataFrame()

            # 등락률 계산
            df['등락률'] = ((df['종가'] - df['시가']) / df['시가'] * 100).round(2)

            # 거래대금 계산
            df['거래대금'] = df['종가'] * df['거래량']

            # 하위 N개 선택
            bottom = df.nsmallest(n, '등락률')[['종가', '등락률', '거래량', '거래대금']]

            # 종목명 추가
            ticker_names = {}
            for ticker in bottom.index:
                try:
                    name = stock.get_market_ticker_name(ticker)
                    ticker_names[ticker] = name
                except:
                    ticker_names[ticker] = ticker

            bottom.insert(0, '종목명', bottom.index.map(ticker_names))

            return bottom

        except Exception as e:
            logger.error(f"급락 종목 조회 실패: {e}")
            return pd.DataFrame()

    def get_top_volume(self, date_str: str, market: str = "KOSPI", n: int = 5) -> pd.DataFrame:
        """
        거래대금 상위 종목 조회

        Args:
            date_str: 날짜 (YYYYMMDD)
            market: 시장 (KOSPI/KOSDAQ)
            n: 조회할 종목 수

        Returns:
            거래대금 상위 종목 데이터프레임
        """
        try:
            df = stock.get_market_cap_by_ticker(date_str, market=market)
            if df.empty:
                return pd.DataFrame()

            # 거래대금 상위 N개
            top = df.nlargest(n, '거래대금')[['종가', '거래량', '거래대금', '시가총액']]

            # 등락률 추가
            ohlcv = stock.get_market_ohlcv_by_ticker(date_str, market=market)
            if not ohlcv.empty:
                top['등락률'] = ((ohlcv.loc[top.index, '종가'] - ohlcv.loc[top.index, '시가']) / ohlcv.loc[top.index, '시가'] * 100).round(2)

            # 종목명 추가
            ticker_names = {}
            for ticker in top.index:
                try:
                    name = stock.get_market_ticker_name(ticker)
                    ticker_names[ticker] = name
                except:
                    ticker_names[ticker] = ticker

            top.insert(0, '종목명', top.index.map(ticker_names))

            return top

        except Exception as e:
            logger.error(f"거래대금 상위 종목 조회 실패: {e}")
            return pd.DataFrame()

    def get_foreign_net_buy_top(self, date_str: str, market: str = "KOSPI", n: int = 5) -> pd.DataFrame:
        """
        외국인 순매수 상위 종목 조회

        Args:
            date_str: 날짜 (YYYYMMDD)
            market: 시장 (KOSPI/KOSDAQ)
            n: 조회할 종목 수

        Returns:
            외국인 순매수 상위 종목 데이터프레임
        """
        try:
            df = stock.get_market_trading_value_by_date(date_str, date_str, market=market)
            if df.empty:
                return pd.DataFrame()

            # 종목별로 재구성
            result = []
            for ticker in stock.get_market_ticker_list(date_str, market=market):
                try:
                    trading = stock.get_market_trading_value_by_date(date_str, date_str, ticker)
                    if not trading.empty and '외국인합계' in trading.columns:
                        foreign_net = trading.iloc[0]['외국인합계']
                        name = stock.get_market_ticker_name(ticker)

                        # 주가 정보
                        ohlcv = stock.get_market_ohlcv(date_str, date_str, ticker)
                        if not ohlcv.empty:
                            close = ohlcv.iloc[0]['종가']
                            result.append({
                                '종목코드': ticker,
                                '종목명': name,
                                '외국인순매수': foreign_net,
                                '종가': close
                            })
                except:
                    continue

            if not result:
                return pd.DataFrame()

            df_result = pd.DataFrame(result)
            df_result = df_result.nlargest(n, '외국인순매수')
            df_result = df_result.set_index('종목코드')

            return df_result

        except Exception as e:
            logger.error(f"외국인 순매수 조회 실패: {e}")
            return pd.DataFrame()

    def get_market_summary(self, date_str: str) -> dict:
        """
        전체 시장 요약 정보

        Args:
            date_str: 날짜 (YYYYMMDD)

        Returns:
            시장 요약 딕셔너리
        """
        logger.info(f"시장 요약 정보 수집 중: {date_str}")

        summary = {
            'date': date_str,
            'indices': self.get_index_info(date_str),
            'kospi': {
                'top_gainers': self.get_top_gainers(date_str, "KOSPI", 5),
                'top_losers': self.get_top_losers(date_str, "KOSPI", 5),
                'top_volume': self.get_top_volume(date_str, "KOSPI", 5),
            },
            'kosdaq': {
                'top_gainers': self.get_top_gainers(date_str, "KOSDAQ", 5),
                'top_losers': self.get_top_losers(date_str, "KOSDAQ", 5),
                'top_volume': self.get_top_volume(date_str, "KOSDAQ", 5),
            }
        }

        return summary
