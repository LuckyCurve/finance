from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session
from yfinance import Ticker

import db
from db.entity import AssetType, StockTransaction, TransactionType


def buy_stock(symbol: str, date: date, number: str | float, price: str | float) -> None:
    if not stock_exists(symbol):
        raise Exception(f"{symbol} 不存在，请重新输入")
    t = StockTransaction(
        date=date,
        type=TransactionType.BUY,
        trade_type=AssetType.TICKER,
        ticker=symbol,
        shares=Decimal(number),
        price=Decimal(price),
    )
    with Session(db.engine) as session:
        session.add(t)
        session.commit()


def stock_exists(symbol: str) -> bool:
    t = Ticker(symbol)
    return "open" in t.info
