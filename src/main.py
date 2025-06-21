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
    calculate_ticker_daily_total_earn_rate,
)
from service.sync import sync


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

    col.caption("每日股票份额")
    col.bar_chart(
        ticker_daily_price_df,
        x="Date",
        y="Price",
        color="Ticker",
        x_label="日期",
        y_label="市场价格",
    )


def draw_right(col: DeltaGenerator):
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

    col.caption("个股营收百分比%")
    col.line_chart(
        calculate_ticker_daily_total_earn_rate(),
        x="Date",
        y="TotalEarnRate",
        color="Ticker",
        x_label="日期",
        y_label="总收益百分比",
    )

    col.caption("每日个股涨跌图")
    col.line_chart(
        calculate_ticker_daily_change(),
        x="Date",
        y="Earn",
        color="Ticker",
        x_label="日期",
        y_label="涨跌幅",
    )


if __name__ == "__main__":
    streamlit.set_page_config(page_title="我的财富看板", page_icon="💰", layout="wide")
    streamlit.title(":rainbow[我的财富看板]")

    with streamlit.spinner("数据同步中...", show_time=True):
        Base.metadata.create_all(db.engine)
        sync()

    current_account = get_current_account()
    current_ticker = get_current_ticker()
    ticker_daily_price_df = calculate_ticker_daily_price()

    col1, col2 = streamlit.columns(2)

    draw_left(col1)
    draw_right(col2)

    streamlit.balloons()
    # streamlit.snow()
