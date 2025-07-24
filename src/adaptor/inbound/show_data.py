# 完成首页的数据展示
from datetime import date, timedelta
from decimal import Decimal

import pandas as pd
import streamlit
from numerize.numerize import numerize
from sqlalchemy import desc
from sqlalchemy.orm import Session

import db
from db.entity import (
    Account,
    AccountData,
    CurrencyAsset,
    CurrencyTransaction,
    CurrencyType,
    ExchangedRate,
    StockTransaction,
    TickerData,
    TransactionType,
)
from service.calculate import calculate_each_day_ticker_price

TRANSACTION_TYPE_DICT = {
    TransactionType.BUY: ":green[买入]",
    TransactionType.SELL: ":red[卖出]",
}


def format_decimal(data: Decimal | float | int) -> str:
    return numerize(round(float(data), 2))


@streamlit.cache_data
def get_current_account() -> AccountData:  # 修改返回类型提示
    """获取相应的财富总值

    Returns:
        AccountData: # 修改返回类型提示
            - 今天的财富总值
            - 昨天的财富总值,用于计算财富变化
            - 货币计价类型, 默认 USD
            - 财富统计的日期
    """
    with Session(db.engine) as session:
        today, yesterday = session.query(Account).order_by(desc(Account.date)).limit(2)
        # 确保返回的类型与 AccountData 的定义一致
        return AccountData(
            total_value=float(today.currency),
            yesterday_value=float(yesterday.currency),
            currency_type=today.currency_type,
            update_time=today.date,
        )


@streamlit.cache_data
def get_current_ticker() -> TickerData:  # 修改返回类型提示
    """获取财富部分中股票总值

    Returns:
        AccountData: # 修改返回类型提示
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
    # 确保返回的类型与 TickerData 的定义一致
    return TickerData(
        total_value=float(current_date_value),
        yesterday_value=float(yesterday_value),
        currency_type=CurrencyType.USD,
        update_time=current_date,
    )


@streamlit.cache_data
def get_current_currencies() -> list[tuple[str, float]]:
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


@streamlit.cache_data
def get_ticker_transaction_details() -> pd.DataFrame:
    with Session(db.engine) as session:
        res = [
            (
                stock.id,
                stock.ticker,
                TRANSACTION_TYPE_DICT[stock.type],
                format_decimal(stock.price),
                format_decimal(stock.shares),
                stock.date,
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
            ],
        )
        df.set_index("ID", inplace=True)
        return df


@streamlit.cache_data
def get_currency_transaction_details() -> pd.DataFrame:
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


@streamlit.cache_data
def get_exchange_rate_details() -> pd.DataFrame:
    with Session(db.engine) as session:
        res = [
            (
                rate.id,
                rate.currency_type.value,
                float(rate.rate),
                rate.date,
            )
            for rate in session.query(ExchangedRate)
            .filter(ExchangedRate.currency_type != CurrencyType.USD)
            .all()
        ]
        df = pd.DataFrame(
            res,
            columns=["ID", "货币类型", "汇率", "日期"],
        )
        return df
