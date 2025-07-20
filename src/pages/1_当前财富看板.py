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
from pyecharts.charts import Bar, Line, Sunburst
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType

# Local application imports
from adaptor.inbound.show_data import (
    CurrencyType,
    format_decimal,
    get_current_account,
    get_current_currencies,
    get_current_ticker,
    get_exchange_rate_details,
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
        streamlit.metric(
            label=f"我的财富总值 {converted_account[3]}",
            value=f"{format_decimal(converted_account[0])} {selected_currency_symbol}",
            delta=f"{format_decimal(converted_account[0] - converted_account[1])}",
        )
    with col2:
        streamlit.metric(
            label=f"我的股市数据 {converted_ticker[3]}",
            value=f"{format_decimal(converted_ticker[0])} {selected_currency_symbol}",
            delta=f"{format_decimal(converted_ticker[0] - converted_ticker[1])}",
        )

    streamlit.write("\n")
    streamlit.write("\n")
    streamlit.write("\n")
    streamlit.write("\n")

    # Asset allocation sunburst chart
    current_currency = get_current_currencies()
    ticker_data = ticker_daily_price_df[
        ticker_daily_price_df["Date"].dt.date == datetime.date.today() - timedelta(1)
    ]
    sunburst_data = [
        {
            "name": "股市",
            "value": round(float(current_ticker[0]), 2),
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
    sunburst_chart = (
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
            label_opts=opts.LabelOpts(
                formatter="{b}", font_size=14, position="outside"
            ),
            color=[
                "#6E7074",
                "#5470C6",
                "#91CC75",
                "#EE6666",
                "#FC8452",
                "#73C0DE",
                "#3BA272",
                "#FC8452",
                "#9A60B4",
                "#EA7CCC",
            ],
        )
        .render_embed()
    )
    components.html(sunburst_chart, height=600)

    # Daily total asset change chart with optimized display for small changes
    account_change_df = calculate_account_change()
    account_change_df["Date"] = pd.to_datetime(account_change_df["Date"])

    # Calculate dynamic min/max values to better show small changes
    values = account_change_df["Currency"]
    min_val = values.min()
    max_val = values.max()

    # Add a buffer to the min and max to ensure the line is not at the very edge
    buffer = (max_val - min_val) * 0.1  # 10% buffer
    if buffer == 0:  # Handle case where all values are the same
        buffer = (
            max_val * 0.01 if max_val > 0 else 1
        )  # 1% of the value or 1 if value is 0

    min_value = min_val - buffer
    max_value = max_val + buffer

    line_chart = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="100%"))
        .add_xaxis(
            xaxis_data=account_change_df["Date"].dt.strftime("%Y-%m-%d").tolist()
        )
        .add_yaxis(
            series_name="总财富",
            y_axis=account_change_df["Currency"].tolist(),
            markpoint_opts=opts.MarkPointOpts(
                data=[opts.MarkPointItem(type_="max"), opts.MarkPointItem(type_="min")]
            ),
            markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")]),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="每日总资产变化", subtitle="单位: 美元"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
            xaxis_opts=opts.AxisOpts(name="日期"),
            yaxis_opts=opts.AxisOpts(name="总财富", min_=min_value, max_=max_value),
        )
        .render_embed()
    )
    components.html(line_chart, height=600)

    # Daily stock share bar chart
    bar_chart = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="100%"))
        .add_xaxis(
            xaxis_data=ticker_daily_price_df["Date"]
            .dt.strftime("%Y-%m-%d")
            .unique()
            .tolist()
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="每日股票市值", subtitle="单位: 美元"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
            xaxis_opts=opts.AxisOpts(name="日期"),
            yaxis_opts=opts.AxisOpts(name="市场价格"),
        )
    )
    for ticker in ticker_daily_price_df["Ticker"].unique():
        ticker_df = ticker_daily_price_df[ticker_daily_price_df["Ticker"] == ticker]
        bar_chart.add_yaxis(
            series_name=ticker,
            y_axis=ticker_df["Price"].tolist(),
            stack="total",
            label_opts=opts.LabelOpts(is_show=False),
        )
    components.html(bar_chart.render_embed(), height=600)

    # Individual stock revenue percentage chart
    earn_rate_df = calculate_ticker_daily_total_earn_rate()
    line_earn_rate = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="100%"))
        .add_xaxis(
            xaxis_data=earn_rate_df["Date"].dt.strftime("%Y-%m-%d").unique().tolist()
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="个股总收益率", subtitle="单位: %"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
            xaxis_opts=opts.AxisOpts(name="日期"),
            yaxis_opts=opts.AxisOpts(name="总收益百分比"),
        )
    )
    for ticker in earn_rate_df["Ticker"].unique():
        ticker_df = earn_rate_df[earn_rate_df["Ticker"] == ticker]
        line_earn_rate.add_yaxis(
            series_name=ticker,
            y_axis=ticker_df["TotalEarnRate"].tolist(),
            label_opts=opts.LabelOpts(is_show=False),
        )
    components.html(line_earn_rate.render_embed(), height=600)

    # Daily individual stock change chart
    daily_change_df = calculate_ticker_daily_change()
    line_daily_change = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="100%"))
        .add_xaxis(
            xaxis_data=daily_change_df["Date"].dt.strftime("%Y-%m-%d").unique().tolist()
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="每日个股涨跌", subtitle="单位: 美元"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
            xaxis_opts=opts.AxisOpts(name="日期"),
            yaxis_opts=opts.AxisOpts(name="涨跌幅"),
        )
    )
    for ticker in daily_change_df["Ticker"].unique():
        ticker_df = daily_change_df[daily_change_df["Ticker"] == ticker]
        line_daily_change.add_yaxis(
            series_name=ticker,
            y_axis=ticker_df["Earn"].tolist(),
            label_opts=opts.LabelOpts(is_show=False),
        )
    components.html(line_daily_change.render_embed(), height=600)


if __name__ == "__main__":
    streamlit.set_page_config(
        page_title="当前财富看板",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    current_finance_summary()
