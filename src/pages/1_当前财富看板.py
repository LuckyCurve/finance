"""
This Streamlit application provides a comprehensive financial dashboard,
displaying current wealth, stock data, asset allocation, and transaction details.
It includes functionality to switch between different currency views for wealth and stock metrics.
"""

import datetime
from datetime import timedelta
from typing import Tuple

import pandas as pd
import streamlit
import streamlit.components.v1 as components

# Pyecharts imports
from pyecharts import options as opts
from pyecharts.charts import Pie, Sunburst
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType

# Local application imports
from adaptor.inbound.show_data import (
    CurrencyType,
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


def get_pie_tooltip_formatter(total_assets: float) -> JsCode:
    return JsCode(
        f"""
        function (params) {{
            var total_assets = {total_assets};
            var formatted_value = new Intl.NumberFormat('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }}).format(params.value);
            var percentage = ((params.value / total_assets) * 100).toFixed(2);
            return params.marker + '<b>' + params.name + '</b><br/>' + formatted_value + ' (' + percentage + '%)';
        }}
        """
    )


def draw_left(
    current_account: Tuple,
    original_current_ticker: Tuple,
    ticker_daily_price_df: pd.DataFrame,
    selected_currency_symbol: str,
) -> None:
    """
    Draws the left column of the finance dashboard, including total wealth metric,
    asset allocation pie chart, daily total asset change chart, and daily stock share chart.

    Args:
        current_account (Tuple): Tuple containing current account details (value, yesterday's value, currency type, date).
        original_current_ticker (Tuple): Tuple containing original ticker details (value, yesterday's value, currency type, date)
                                         used for the asset allocation pie chart to keep it in USD.
        ticker_daily_price_df (pd.DataFrame): DataFrame with daily ticker prices.
        selected_currency_type (CurrencyType): The currency type selected by the user for display.
        selected_currency_symbol (str): The symbol of the selected currency.
    """
    streamlit.metric(
        label=f"我的财富总值 {current_account[3]}",
        value=f"{format_decimal(current_account[0])} {selected_currency_symbol}",
        delta=f"{format_decimal(current_account[0] - current_account[1])}",
    )

    current_currency = get_current_currencies()
    ticker_data = ticker_daily_price_df[
        ticker_daily_price_df["Date"].dt.date == datetime.date.today() - timedelta(1)
    ]

    sunburst_data = [
        {
            "name": "股市",
            "value": round(float(original_current_ticker[0]), 2),
            "children": [
                {"name": row["Ticker"], "value": round(row["Price"], 2)}
                for _, row in ticker_data.iterrows()
            ],
        },
        {
            "name": "现金",
            "value": sum(v for _, v in current_currency),
            "children": [
                {"name": currency_type, "value": round(value, 2)}
                for currency_type, value in current_currency
            ],
        },
    ]

    total_assets = sum(item.get("value", 0) for item in sunburst_data)
    pie_tooltip_formatter = get_pie_tooltip_formatter(total_assets)

    html = (
        Sunburst(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="100%"))
        .add(
            "",
            data_pair=sunburst_data,
            radius=[0, "90%"],
            highlight_policy="ancestor",
            levels=[
                {},
                {
                    "r0": "15%",
                    "r": "55%",
                    "itemStyle": {"borderWidth": 2},
                    "label": {"rotate": "tangential"},
                },
                {"r0": "55%", "r": "80%", "label": {"align": "right"}},
            ],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="总的资产分配"),
            tooltip_opts=opts.TooltipOpts(formatter=pie_tooltip_formatter),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}", font_size=14, position="outside")
        )
        .render_embed()
    )
    components.html(html, height=600)

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


def draw_right(
    current_ticker: Tuple,
    ticker_daily_price_df: pd.DataFrame,
    selected_currency_symbol: str,
) -> None:
    """
    Draws the right column of the finance dashboard, including stock data metric,
    held stock share pie chart, individual stock revenue percentage chart, and daily stock change chart.

    Args:
        current_ticker (Tuple): Tuple containing current ticker details (value, yesterday's value, currency type, date).
        ticker_daily_price_df (pd.DataFrame): DataFrame with daily ticker prices.
        selected_currency_type (CurrencyType): The currency type selected by the user for display.
        selected_currency_symbol (str): The symbol of the selected currency.
    """
    streamlit.metric(
        label=f"我的股市数据 {current_ticker[3]}",
        value=f"{format_decimal(current_ticker[0])} {selected_currency_symbol}",
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

    total_ticker_value = sum(v for _, v in pie_data)
    pie_tooltip_formatter = get_pie_tooltip_formatter(total_ticker_value)

    html = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.DARK))
        .add("市场份额", pie_data, radius=["30%", "60%"])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="持有股票份额"),
            tooltip_opts=opts.TooltipOpts(formatter=pie_tooltip_formatter),
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


def draw_details(exchange_rate: pd.DataFrame) -> None:
    """
    Draws the detailed sections of the finance dashboard, including exchange rate fluctuations,
    stock transaction details, and cash transaction details.
    """
    streamlit.caption("股票交易详细数据")
    ticker_details = get_ticker_transaction_details()
    streamlit.table(ticker_details)

    streamlit.caption("现金交易详细数据")
    currency_details = get_currency_transaction_details()
    streamlit.table(currency_details)


def convert_value(
    value: float,
    original_currency_type: CurrencyType,
    target_currency_type: CurrencyType,
    exchange_rates: pd.DataFrame,
) -> float:
    """
    Converts a financial value from its original currency to a target currency using provided exchange rates.

    Args:
        value (float): The financial value to convert.
        original_currency_type (CurrencyType): The original currency type of the value.
        target_currency_type (CurrencyType): The desired target currency type.
        exchange_rates (pd.DataFrame): DataFrame containing exchange rates, with columns "货币类型" and "汇率".

    Returns:
        float: The converted value in the target currency.
    """
    if original_currency_type == target_currency_type:
        return value

    # Convert original to USD first if it's not USD
    if original_currency_type != CurrencyType.USD:
        original_rate_row = exchange_rates[
            exchange_rates["货币类型"] == original_currency_type.value
        ]
        if not original_rate_row.empty:
            original_rate = original_rate_row["汇率"].iloc[0]
            value_in_usd = value / original_rate
        else:
            value_in_usd = value  # Assume 1:1 if rate not found
    else:
        value_in_usd = value

    # Convert from USD to target currency
    if target_currency_type != CurrencyType.USD:
        target_rate_row = exchange_rates[
            exchange_rates["货币类型"] == target_currency_type.value
        ]
        if not target_rate_row.empty:
            target_rate = target_rate_row["汇率"].iloc[0]
            return value_in_usd * target_rate
        else:
            return value_in_usd  # Assume 1:1 if rate not found
    else:
        return value_in_usd


def _get_initial_data() -> Tuple[Tuple, Tuple, pd.DataFrame]:
    """Fetches initial account, ticker, and daily price data."""
    current_account = get_current_account()
    current_ticker = get_current_ticker()
    ticker_daily_price_df = calculate_ticker_daily_price()
    return current_account, current_ticker, ticker_daily_price_df


def _handle_currency_selection_and_conversion(
    current_account: Tuple, current_ticker: Tuple, exchange_rates_df: pd.DataFrame
) -> Tuple[Tuple, Tuple, str]:
    """Handles currency selection and converts account/ticker values."""
    all_currencies = [currency.value for currency in CurrencyType]

    selected_currency_symbol = streamlit.selectbox(
        "选择显示货币",
        options=all_currencies,
    )
    selected_currency_type = CurrencyType(selected_currency_symbol)

    converted_account_value = convert_value(
        float(current_account[0]),
        current_account[2],
        selected_currency_type,
        exchange_rates_df,
    )
    converted_account_yesterday_value = convert_value(
        float(current_account[1]),
        current_account[2],
        selected_currency_type,
        exchange_rates_df,
    )
    converted_account = (
        converted_account_value,
        converted_account_yesterday_value,
        selected_currency_type,
        current_account[3],
    )

    converted_ticker_value = convert_value(
        float(current_ticker[0]),
        current_ticker[2],
        selected_currency_type,
        exchange_rates_df,
    )
    converted_ticker_yesterday_value = convert_value(
        float(current_ticker[1]),
        current_ticker[2],
        selected_currency_type,
        exchange_rates_df,
    )
    converted_ticker = (
        converted_ticker_value,
        converted_ticker_yesterday_value,
        selected_currency_type,
        current_ticker[3],
    )

    return (
        converted_account,
        converted_ticker,
        selected_currency_symbol,
    )


def current_finance_summary() -> None:
    """Main function to display the current finance summary dashboard."""
    streamlit.title(":rainbow[我的财富看板]")

    current_account, current_ticker, ticker_daily_price_df = _get_initial_data()
    exchange_rates = get_exchange_rate_details()

    (
        converted_account,
        converted_ticker,
        selected_currency_symbol,
    ) = _handle_currency_selection_and_conversion(
        current_account, current_ticker, exchange_rates
    )

    col1, col2 = streamlit.columns(2)

    with col1:
        draw_left(
            converted_account,
            current_ticker,
            ticker_daily_price_df,
            selected_currency_symbol,
        )
    with col2:
        draw_right(
            converted_ticker,
            ticker_daily_price_df,
            selected_currency_symbol,
        )

    draw_details(exchange_rates)


if __name__ == "__main__":
    streamlit.set_page_config(
        page_title="当前财富看板",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    current_finance_summary()
