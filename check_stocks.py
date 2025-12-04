#!/usr/bin/env python3
"""데이터베이스의 종목 확인"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import Database
from database.queries import StockQueries

def main():
    with Database().get_session() as session:
        stocks = StockQueries.get_all_stocks(session)

        print(f"\n총 {len(stocks)}개 종목이 저장되어 있습니다.\n")

        if stocks:
            print("저장된 종목 목록:")
            print("-" * 60)
            for stock in stocks[:20]:  # 처음 20개만
                print(f"{stock.ticker:8s} {stock.name:20s} {stock.market}")

            if len(stocks) > 20:
                print(f"\n... 외 {len(stocks) - 20}개 종목")
        else:
            print("저장된 종목이 없습니다.")
            print("\n예시 종목 추가:")
            print("uv run python examples/collect_stock_data.py")

if __name__ == "__main__":
    main()
