import datetime
from datetime import timedelta

import pandas
import plotly
import plotly.express
import streamlit
from streamlit.delta_generator import DeltaGenerator

import db
from adaptor.inbound.show_data import (
    format_decimal,
    get_current_account,
    get_current_currencies,
    get_current_ticker,
)
from db.common import Base
from service.calculate import (
    calculate_account_change,
    calculate_ticker_daily_change,
    calculate_ticker_daily_price,
)
from service.sync import sync

Base.metadata.create_all(db.engine)
sync()


def draw_left(col: DeltaGenerator):
    col.metric(
        label=f"我的财富总值 {current_account[3]}",
        value=f"{format_decimal(current_account[0])} {current_account[2].value}",
        delta=f"{format_decimal(current_account[0] - current_account[1])}",
    )

    current_currency = get_current_currencies()

    data = pandas.DataFrame(
        {
            "资产类型": ["股市"]
            + [currency_type for currency_type, _ in current_currency],
            "价格": [current_ticker[0]] + [value for _, value in current_currency],
        }
    )
    fig = plotly.express.pie(data, names="资产类型", values="价格")
    col.caption("资产分配")
    col.plotly_chart(fig)

    account_change_df = calculate_account_change()
    col.caption("每日总资产变化图")
    col.line_chart(
        account_change_df,
        x="Date",
        y="Currency",
        x_label="日期",
        y_label="总财富",
    )


def draw_right(col: DeltaGenerator):
    ticker_daily_change_df = calculate_ticker_daily_change()
    ticker_daily_price_df = calculate_ticker_daily_price()
    col.metric(
        label=f"我的股市数据 {current_ticker[3]}",
        value=f"{format_decimal(current_ticker[0])} {current_ticker[2].value}",
        delta=f"{format_decimal(current_ticker[0] - current_ticker[1])}",
    )

    data = ticker_daily_price_df[
        ticker_daily_price_df["Date"].dt.date == datetime.date.today() - timedelta(1)
    ]
    data = data[["Price", "Ticker"]]
    fig = plotly.express.pie(data, names="Ticker", values="Price")
    col.caption("持有股票份额")
    col.plotly_chart(fig)
    col.caption("每日股票份额")
    col.bar_chart(
        ticker_daily_price_df,
        x="Date",
        y="Price",
        color="Ticker",
        x_label="日期",
        y_label="市场价格",
    )
    col.caption("每日个股涨跌图")
    col.line_chart(
        ticker_daily_change_df,
        x="Date",
        y="Earn",
        color="Ticker",
        x_label="日期",
        y_label="涨跌幅",
    )


if __name__ == "__main__":
    streamlit.set_page_config(page_title="我的财富看板", page_icon="💰", layout="wide")
    streamlit.title(":rainbow[我的财富看板]")

    current_account = get_current_account()
    current_ticker = get_current_ticker()

    col1, col2 = streamlit.columns(2)

    draw_left(col1)
    draw_right(col2)


def test():
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
