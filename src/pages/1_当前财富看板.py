import datetime
from datetime import timedelta
from typing import Tuple

import pandas as pd
import streamlit
import streamlit.components.v1 as components
from pyecharts import options as opts
from pyecharts.charts import Pie
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType

from adaptor.inbound.show_data import (
    format_decimal,
    get_currency_transaction_details,
    get_current_account,
    get_current_currencies,
    get_current_ticker,
    get_exchange_rate_details,
    get_ticker_transaction_details,
)
from service.calculate import (
    calculate_account_change,
    calculate_ticker_daily_change,
    calculate_ticker_daily_price,
    calculate_ticker_daily_total_earn_rate,
)

PIE_TOOLTIP_FORMATTER = JsCode(
    "function (params) { return params.marker + '<b>' + params.name + '</b> ' + params.value.toFixed(2) + ' (' + params.percent.toFixed(2) + '%)'; }"
)


def draw_left(
    current_account: Tuple, current_ticker: Tuple, ticker_daily_price_df: pd.DataFrame
) -> None:
    streamlit.metric(
        label=f"我的财富总值 {current_account[3]}",
        value=f"{format_decimal(current_account[0])} {current_account[2].value}",
        delta=f"{format_decimal(current_account[0] - current_account[1])}",
    )

    current_currency = get_current_currencies()

    data = [
        [
            "股市",
            round(float(current_ticker[0]), 2),
        ]
    ] + [[currency_type, value] for currency_type, value in current_currency]
    data = sorted(data, key=lambda x: x[1], reverse=True)

    html = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add(
            series_name="资产分配",
            data_pair=data,
            radius="50%",
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="总的资产分配",
            ),
            tooltip_opts=opts.TooltipOpts(formatter=PIE_TOOLTIP_FORMATTER),
        )
        .render_embed()
    )
    components.html(html, height=500)

    account_change_df = calculate_account_change()
    streamlit.caption("每日总资产变化图")
    streamlit.line_chart(
        account_change_df,
        x="Date",
        y="Currency",
        x_label="日期",
        y_label="总财富",
    )

    streamlit.caption("每日股票份额")
    streamlit.bar_chart(
        ticker_daily_price_df,
        x="Date",
        y="Price",
        color="Ticker",
        x_label="日期",
        y_label="市场价格",
    )


def draw_right(current_ticker: Tuple, ticker_daily_price_df: pd.DataFrame) -> None:
    streamlit.metric(
        label=f"我的股市数据 {current_ticker[3]}",
        value=f"{format_decimal(current_ticker[0])} {current_ticker[2].value}",
        delta=f"{format_decimal(current_ticker[0] - current_ticker[1])}",
    )

    data = ticker_daily_price_df[
        ticker_daily_price_df["Date"].dt.date == datetime.date.today() - timedelta(1)
    ]
    pie_data = [
        (row["Ticker"], row["Price"])
        for _, row in data[["Price", "Ticker"]]
        .sort_values(by="Price", ascending=False)
        .iterrows()
    ]

    html = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add("市场份额", pie_data, radius=["30%", "60%"])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="持有股票份额"),
            tooltip_opts=opts.TooltipOpts(formatter=PIE_TOOLTIP_FORMATTER),
        )
        .render_embed()
    )

    components.html(html, height=500)

    streamlit.caption("个股营收百分比%")
    streamlit.line_chart(
        calculate_ticker_daily_total_earn_rate(),
        x="Date",
        y="TotalEarnRate",
        color="Ticker",
        x_label="日期",
        y_label="总收益百分比",
    )

    streamlit.caption("每日个股涨跌图")
    streamlit.line_chart(
        calculate_ticker_daily_change(),
        x="Date",
        y="Earn",
        color="Ticker",
        x_label="日期",
        y_label="涨跌幅",
    )


def draw_details() -> None:
    streamlit.caption("汇率波动")
    exchange_rate = get_exchange_rate_details()
    streamlit.line_chart(
        exchange_rate,
        x="日期",
        y="汇率",
        color="货币类型",
        x_label="日期",
        y_label="汇率",
    )

    streamlit.caption("股票交易详细数据")
    ticker_details = get_ticker_transaction_details()
    streamlit.table(ticker_details)

    streamlit.caption("现金交易详细数据")
    currency_details = get_currency_transaction_details()
    streamlit.table(currency_details)


def current_finance_summary(
    current_account: Tuple, current_ticker: Tuple, ticker_daily_price_df: pd.DataFrame
) -> None:
    streamlit.title(":rainbow[我的财富看板]")

    col1, col2 = streamlit.columns(2)

    with col1:
        draw_left(current_account, current_ticker, ticker_daily_price_df)
    with col2:
        draw_right(current_ticker, ticker_daily_price_df)

    draw_details()


if __name__ == "__main__":
    streamlit.set_page_config(
        page_title="当前财富看板",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="collapsed",  # 关键设置：默认收起侧边栏
    )
    current_account = get_current_account()
    current_ticker = get_current_ticker()
    ticker_daily_price_df = calculate_ticker_daily_price()

    current_finance_summary(current_account, current_ticker, ticker_daily_price_df)
