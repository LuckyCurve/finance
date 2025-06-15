import datetime
from datetime import date, timedelta
from decimal import Decimal
from typing import Literal

import streamlit
from numerize.numerize import numerize
from sqlalchemy import desc
from sqlalchemy.orm import Session

import db
from db.common import Base
from db.entity import Account, CurrencyType
from service.calculate import (
    calculate_account_change,
    calculate_each_daily_ticker_price,
    calculate_ticker_daily_change,
    calculate_ticker_daily_price,
)
from service.sync import sync

Base.metadata.create_all(db.engine)
sync()


def format_decimal(data):
    return numerize(round(float(data), 2))


def get_current_account() -> tuple[Decimal, Decimal, CurrencyType, date]:
    with Session(db.engine) as session:
        today, yesterday = session.query(Account).order_by(desc(Account.date)).limit(2)
        return (today.currency, yesterday.currency, today.currency_type, today.date)


def get_current_ticker() -> tuple[int, int, Literal[CurrencyType.USD], date]:
    current_date = datetime.date.today() - timedelta(1)
    yesterday = datetime.date.today() - timedelta(2)
    current_date_value = sum(
        [i[0] for i in calculate_each_daily_ticker_price(current_date)]
    )
    yesterday_value = sum([i[0] for i in calculate_each_daily_ticker_price(yesterday)])
    return (current_date_value, yesterday_value, CurrencyType.USD, current_date)


if __name__ == "__main__":
    streamlit.set_page_config(page_title="我的财富看板", layout="wide")
    streamlit.title("我的财富看板")

    current_account = get_current_account()
    current_ticker = get_current_ticker()

    col1, col2 = streamlit.columns(2)
    col1.metric(
        label=f"我的财富总值 {current_account[3]}",
        value=f"{format_decimal(current_account[0])} {current_account[2].value}",
        delta=f"{format_decimal(current_account[0] - current_account[1])}",
    )
    col2.metric(
        label=f"我的股市数据 {current_ticker[3]}",
        value=f"{format_decimal(current_ticker[0])} {current_ticker[2].value}",
        delta=f"{format_decimal(current_ticker[0] - current_ticker[1])}",
    )

    account_change_df = calculate_account_change()
    ticker_daily_price_df = calculate_ticker_daily_price()
    ticker_daily_change_df = calculate_ticker_daily_change()

    col1, col2 = streamlit.columns(2)
    col1.caption("每日总资产变化图（含汇率波动）")
    col1.bar_chart(
        account_change_df,
        x="Date",
        y="Currency",
        x_label="日期",
        y_label="总财富",
    )

    col2.caption("每日股票份额")
    col2.bar_chart(
        ticker_daily_price_df,
        x="Date",
        y="Price",
        color="Ticker",
        x_label="日期",
        y_label="市场价格",
    )
    col2.caption("每日个股涨跌图（含汇率波动）")
    col2.bar_chart(
        ticker_daily_change_df,
        x="Date",
        y="Earn",
        color="Ticker",
        x_label="日期",
        y_label="涨跌幅",
    )


def date():
    pass
    # buy_stock("0700.HK", date(2025, 6, 11), 165, 303.03)
    # buy_stock("0700.HK", date(2025, 6, 11), 166, 343.8)
    # buy_stock("GOOGL", date(2025, 6, 11), 1.8184, 154.17)
    # buy_stock("IAU", date(2025, 6, 11), 4.5126, 55.48)
    # buy_stock("SPLG", date(2025, 6, 11), 30.5197, 64.02)
    # buy_stock("GGB", date(2025, 6, 11), 338.9833, 2.95)
    # buy_stock("BIDU", date(2025, 6, 11), 15.3333, 84.57)
    # buy_stock("QQQM", date(2025, 6, 11), 4.6773, 213.87)
    # buy_stock("SGOV", date(2025, 6, 11), 222.4285, 100.49)
    # buy_stock("PDD", date(2025, 6, 11), 0.8267, 121.38)
    # buy_currency(645576.25, CurrencyType.CNY, comment="微众银行")
    # buy_currency(51714.94, CurrencyType.CNY, comment="招商银行")
    # buy_currency(129715.35, CurrencyType.HKD, comment="汇丰香港")
    # buy_currency(1228.95, CurrencyType.USD, comment="富途牛牛货币基金")
