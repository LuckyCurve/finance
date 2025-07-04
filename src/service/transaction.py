from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

import db
from db.entity import (
    AssetType,
    CurrencyTransaction,
    CurrencyType,
    StockTransaction,
    TransactionType,
)
from service.sync import search_ticker_symbol


def buy_currency(
    currency: float | str | Decimal, currency_type: CurrencyType, comment: str
) -> None:
    if not isinstance(currency, Decimal):
        currency = Decimal(currency)

    t = CurrencyTransaction(
        date=date.today(),
        type=TransactionType.BUY,
        currency=Decimal(currency),
        currency_type=currency_type,
        comment=comment,
    )
    with Session(db.engine) as session:
        session.add(t)
        session.commit()


def sell_currency(
    currency: float | str | Decimal, currency_type: CurrencyType, comment: str
) -> None:
    if not isinstance(currency, Decimal):
        currency = Decimal(currency)

    t = CurrencyTransaction(
        date=date.today(),
        type=TransactionType.SELL,
        currency=Decimal(currency),
        currency_type=currency_type,
        comment=comment,
    )
    with Session(db.engine) as session:
        session.add(t)
        session.commit()


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
    return search_ticker_symbol(symbol) is not None
