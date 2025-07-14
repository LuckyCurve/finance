import datetime
from datetime import timedelta

import streamlit
from streamlit_echarts import st_echarts

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


def draw_left(current_account, current_ticker, ticker_daily_price_df):
    streamlit.metric(
        label=f"我的财富总值 {current_account[3]}",
        value=f"{format_decimal(current_account[0])} {current_account[2].value}",
        delta=f"{format_decimal(current_account[0] - current_account[1])}",
    )

    current_currency = get_current_currencies()

    data = [{"value": round(float(current_ticker[0]), 2), "name": "股市"}] + [
        {"value": value, "name": currency_type}
        for currency_type, value in current_currency
    ]
    data = sorted(data, key=lambda x: x["value"], reverse=True)

    basic_pie_options = {
        "title": {"text": "资产分配", "left": "center"},
        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
        "legend": {"orient": "vertical", "left": "left"},
        "series": [
            {
                "name": "资产分配",
                "type": "pie",
                "radius": "50%",
                "data": data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    }
                },
            }
        ],
    }
    st_echarts(options=basic_pie_options, height="400px", theme="dark")
    # data = pandas.DataFrame(
    #     {
    #         "资产类型": ["股市"]
    #         + [currency_type for currency_type, _ in current_currency],
    #         "价格": [current_ticker[0]] + [value for _, value in current_currency],
    #     }
    # )
    # fig = plotly.express.pie(data, names="资产类型", values="价格")
    # col.caption("资产分配")
    # col.plotly_chart(fig)

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


def draw_right(current_ticker, ticker_daily_price_df):
    streamlit.metric(
        label=f"我的股市数据 {current_ticker[3]}",
        value=f"{format_decimal(current_ticker[0])} {current_ticker[2].value}",
        delta=f"{format_decimal(current_ticker[0] - current_ticker[1])}",
    )

    data = ticker_daily_price_df[
        ticker_daily_price_df["Date"].dt.date == datetime.date.today() - timedelta(1)
    ]
    data = data[["Price", "Ticker"]]

    data = (
        data.sort_values(by="Price", ascending=False)  # 👈 排序
        .rename(columns={"Price": "value", "Ticker": "name"})[["value", "name"]]
        .to_dict(orient="records")
    )

    rose_pie_options = {
        "title": {"text": "持有股票份额", "left": "center"},
        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
        "legend": {"top": "7%", "left": "center"},
        "series": [
            {
                "name": "市场份额",
                "type": "pie",
                "radius": ["30%", "60%"],  # 内径和外径
                "avoidLabelOverlap": False,
                "data": data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    }
                },
                "labelLine": {"show": False},
                "label": {"show": False, "position": "center"},
            }
        ],
    }
    st_echarts(options=rose_pie_options, height="400px", theme="dark")

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


def draw_details():
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


def current_finance_summary(current_account, current_ticker, ticker_daily_price_df):
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
