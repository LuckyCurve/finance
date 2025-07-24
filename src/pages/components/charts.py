"""
This module contains functions for creating various financial charts for the Streamlit application.
"""

import datetime
from datetime import timedelta

import pandas as pd
import streamlit.components.v1 as components
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Sunburst
from pyecharts.globals import ThemeType

from pages.utils.common import get_pie_tooltip_formatter


def create_sunburst_chart(
    current_ticker_value: float,
    ticker_daily_price_df: pd.DataFrame,
    current_currencies: list[tuple[str, float]],
):
    """Creates and displays the asset allocation sunburst chart."""
    # current_currency = get_current_currencies() # 移除内部调用
    ticker_data = ticker_daily_price_df[
        ticker_daily_price_df["Date"].dt.date == datetime.date.today() - timedelta(1)
    ]
    # Prepare children data first
    stock_children = [
        {"name": row["Ticker"], "value": round(row["Price"], 2)}
        for _, row in ticker_data.iterrows()
    ]
    cash_children = [
        {"name": currency_type, "value": round(value, 2)}
        for currency_type, value in current_currencies
    ]

    sunburst_data = [
        {
            "name": "股市",
            "value": sum(child["value"] for child in stock_children),
            "children": stock_children,
        },
        {
            "name": "现金",
            "value": sum(child["value"] for child in cash_children),
            "children": cash_children,
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


def create_total_assets_line_chart(
    account_change_df: pd.DataFrame, currency_symbol: str
):
    """Creates and displays the daily total asset change line chart."""
    # account_change_df = calculate_account_change() # 移除内部调用
    account_change_df["Date"] = pd.to_datetime(account_change_df["Date"])

    values = account_change_df["Currency"]
    min_val, max_val = values.min(), values.max()
    buffer = (max_val - min_val) * 0.1 or (max_val * 0.01 if max_val > 0 else 1)
    min_value, max_value = min_val - buffer, max_val + buffer

    line_chart = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="100%"))
        .add_xaxis(
            xaxis_data=account_change_df["Date"].dt.strftime("%Y-%m-%d").tolist()
        )
        .add_yaxis(
            series_name="总财富",
            y_axis=account_change_df["Currency"].tolist(),
            label_opts=opts.LabelOpts(is_show=False),
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(
                        type_="max",
                        name="最大值",
                        itemstyle_opts=opts.ItemStyleOpts(color="#d94e5d"),
                    ),
                    opts.MarkPointItem(
                        type_="min",
                        name="最小值",
                        itemstyle_opts=opts.ItemStyleOpts(color="#50a3ba"),
                    ),
                ]
            ),
            markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")]),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="每日总资产变化"),  # 动态单位
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
            xaxis_opts=opts.AxisOpts(name="日期"),
            yaxis_opts=opts.AxisOpts(name="总财富", min_=min_value, max_=max_value),
        )
        .render_embed()
    )
    components.html(line_chart, height=600)


def create_stock_market_bar_chart(
    ticker_daily_price_df: pd.DataFrame, currency_symbol: str
):
    """Creates and displays the daily stock market value bar chart."""
    bar_chart = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="100%"))
        .add_xaxis(
            xaxis_data=ticker_daily_price_df["Date"]
            .dt.strftime("%Y-%m-%d")
            .unique()
            .tolist()
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="每日股票市值"),  # 动态单位
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


def create_stock_earn_rate_line_chart(earn_rate_df: pd.DataFrame):
    """Creates and displays the individual stock total earn rate line chart."""
    # earn_rate_df = calculate_ticker_daily_total_earn_rate() # 移除内部调用
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


def create_daily_change_line_chart(daily_change_df: pd.DataFrame, currency_symbol: str):
    """Creates and displays the daily individual stock change line chart."""
    # daily_change_df = calculate_ticker_daily_change() # 移除内部调用
    line_daily_change = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="100%"))
        .add_xaxis(
            xaxis_data=daily_change_df["Date"].dt.strftime("%Y-%m-%d").unique().tolist()
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="每日个股涨跌"),  # 动态单位
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


def create_historical_exchange_rate_chart(exchange_rate_df: pd.DataFrame):
    """Creates and displays the historical exchange rate line chart."""
    exchange_rate_df["日期"] = pd.to_datetime(exchange_rate_df["日期"])
    line_chart = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="100%"))
        .add_xaxis(
            xaxis_data=exchange_rate_df["日期"]
            .dt.strftime("%Y-%m-%d")
            .unique()
            .tolist()
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="历史汇率变化"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
            xaxis_opts=opts.AxisOpts(name="日期"),
            yaxis_opts=opts.AxisOpts(name="汇率"),
        )
    )

    for currency in exchange_rate_df["货币类型"].unique():
        currency_df = exchange_rate_df[exchange_rate_df["货币类型"] == currency]
        line_chart.add_yaxis(
            series_name=currency,
            y_axis=currency_df["汇率"].tolist(),
            label_opts=opts.LabelOpts(is_show=False),
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(
                        type_="max",
                        name="最大值",
                        itemstyle_opts=opts.ItemStyleOpts(color="#d94e5d"),
                    ),
                    opts.MarkPointItem(
                        type_="min",
                        name="最小值",
                        itemstyle_opts=opts.ItemStyleOpts(color="#50a3ba"),
                    ),
                ]
            ),
        )

    components.html(line_chart.render_embed(), height=600)
