# 完成首页的数据展示
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Literal

import pandas as pd
from numerize.numerize import numerize
from sqlalchemy import desc
from sqlalchemy.orm import Session

import db
from db.entity import (
    Account,
    CurrencyAsset,
    CurrencyTransaction,
    CurrencyType,
    ExchangedRate,
    StockTransaction,
    TransactionType,
)
from service.calculate import calculate_each_day_ticker_price

TRANSACTION_TYPE_DICT = {
    TransactionType.BUY: ":green[买入]",
    TransactionType.SELL: ":red[卖出]",
}


def format_decimal(data) -> str:
    return numerize(round(float(data), 2))


def get_current_account() -> tuple[Decimal, Decimal, CurrencyType, date]:
    """获取相应的财富总值

    Returns:
        tuple[Decimal, Decimal, CurrencyType, date]:
            - 今天的财富总值
            - 昨天的财富总值,用于计算财富变化
            - 货币计价类型, 默认 USD
            - 财富统计的日期
    """
    with Session(db.engine) as session:
        today, yesterday = session.query(Account).order_by(desc(Account.date)).limit(2)
        return (today.currency, yesterday.currency, today.currency_type, today.date)


def get_current_ticker() -> tuple[Decimal, Decimal, Literal[CurrencyType.USD], date]:
    """获取财富部分中股票总值

    Returns:
        tuple[Decimal, Decimal, Literal[CurrencyType.USD], date]:
            - 今天的股票总值
            - 昨天的财富总值
            - 货币计价类型
            - 股票总值统计的日期
    """
    current_date = date.today() - timedelta(1)
    yesterday = date.today() - timedelta(2)
    current_date_value = sum(
        [i[0] for i in calculate_each_day_ticker_price(current_date)]
    )
    yesterday_value = sum([i[0] for i in calculate_each_day_ticker_price(yesterday)])
    return (current_date_value, yesterday_value, CurrencyType.USD, current_date)


def get_current_currencies() -> List:
    """获取最新的所有货币类型财产的值

    Returns:
        List:
            - 货币名称
            - 账面总值(以美元计价)
    """
    current_date = date.today() - timedelta(1)
    res = []
    with Session(db.engine) as session:
        currency_assets = (
            session.query(CurrencyAsset)
            .filter(CurrencyAsset.date == current_date)
            .all()
        )
        for asset in currency_assets:
            rate = Decimal(1)
            if not asset.currency_type == CurrencyType.USD:
                rate = (
                    session.query(ExchangedRate)
                    .filter(ExchangedRate.currency_type == asset.currency_type)
                    .first()
                    .rate
                )
            res.append(
                (asset.currency_type.value, round(float(asset.currency / rate), 2))
            )

        return res


def get_ticker_transaction_details():
    with Session(db.engine) as session:
        res = [
            (
                stock.id,
                stock.ticker,
                TRANSACTION_TYPE_DICT[stock.type],
                format_decimal(stock.price),
                format_decimal(stock.shares),
                stock.date,
                stock.comment,
            )
            for stock in session.query(StockTransaction)
            .order_by(desc(StockTransaction.id))
            .all()
        ]
        df = pd.DataFrame(
            res,
            columns=[
                "ID",
                "代码",
                "操作记录",
                "价格",
                "份额",
                "日期",
                "备注",
            ],
        )
        df.set_index("ID", inplace=True)
        return df


def get_currency_transaction_details():
    with Session(db.engine) as session:
        res = [
            (
                currency.id,
                currency.currency_type.value,
                TRANSACTION_TYPE_DICT[currency.type],
                format_decimal(currency.currency),
                currency.date,
                currency.comment,
            )
            for currency in session.query(CurrencyTransaction)
            .order_by(desc(CurrencyTransaction.id))
            .all()
        ]
        df = pd.DataFrame(
            res,
            columns=[
                "ID",
                "货币类型",
                "操作记录",
                "价格",
                "日期",
                "备注",
            ],
        )
        df.set_index("ID", inplace=True)
        return df
