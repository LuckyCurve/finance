"""
This Streamlit application provides a comprehensive financial dashboard,
displaying current wealth, stock data, asset allocation, and transaction details.
It includes functionality to switch between different currency views for wealth and stock metrics.
"""

from typing import Tuple

import pandas as pd
import streamlit

from adaptor.inbound.show_data import CurrencyType
from pages.components.charts import (
    create_daily_change_line_chart,
    create_stock_earn_rate_line_chart,
    create_stock_market_bar_chart,
    create_sunburst_chart,
    create_total_assets_line_chart,
)
from pages.components.metrics import display_finance_metrics
from service.dashboard_data import fetch_initial_dashboard_data, get_converted_financial_data


def _render_title() -> None:
    """渲染页面标题。"""
    streamlit.title(":rainbow[我的财富看板]")


def _get_currency_selection(all_currencies: list) -> CurrencyType:
    """
    显示货币选择框并返回选定的货币类型。

    Args:
        all_currencies (list): 所有可用货币符号的列表。

    Returns:
        CurrencyType: 用户选择的货币类型。
    """
    selected_currency_symbol = streamlit.selectbox(
        "选择显示货币",
        options=all_currencies,
    )
    return CurrencyType(selected_currency_symbol)


def _display_dashboard_charts(
    current_ticker_value: float, ticker_daily_price_df: pd.DataFrame
) -> None:
    """
    显示财富看板的各种图表。

    Args:
        current_ticker_value (float): 当前股票的总市值。
        ticker_daily_price_df (pd.DataFrame): 包含股票每日价格的DataFrame。
    """
    streamlit.write("\n")  # 添加一些垂直间距

    # 创建并显示资产配置旭日图
    create_sunburst_chart(current_ticker_value, ticker_daily_price_df)
    # 创建并显示总资产折线图
    create_total_assets_line_chart()
    # 创建并显示股票市值柱状图
    create_stock_market_bar_chart(ticker_daily_price_df)
    # 创建并显示股票收益率折线图
    create_stock_earn_rate_line_chart()
    # 创建并显示每日变化折线图
    create_daily_change_line_chart()


def current_finance_summary() -> None:
    """
    主函数，用于显示当前财富看板仪表盘。
    该函数负责协调数据获取、处理和UI渲染。
    """
    _render_title()

    # 1. 数据获取阶段
    # 从服务层获取所有初始数据
    current_account, current_ticker, ticker_daily_price_df, exchange_rates_df = (
        fetch_initial_dashboard_data()
    )

    # 2. 货币选择与数据转换阶段
    # 获取所有支持的货币类型
    all_currencies = [currency.value for currency in CurrencyType]
    # 显示货币选择框并获取用户选择
    selected_currency_type = _get_currency_selection(all_currencies)

    # 根据用户选择的货币，转换账户和股票的财务数据
    converted_account, converted_ticker = get_converted_financial_data(
        current_account, current_ticker, selected_currency_type, exchange_rates_df
    )

    # 3. UI展示阶段
    # 显示财务指标（如总资产、股票市值等）
    display_finance_metrics(
        converted_account, converted_ticker, selected_currency_type.value
    )

    # 显示各种图表
    _display_dashboard_charts(current_ticker[0], ticker_daily_price_df)


if __name__ == "__main__":
    # 配置Streamlit页面
    streamlit.set_page_config(
        page_title="当前财富看板",  # 页面标题
        page_icon="💰",  # 页面图标
        layout="wide",  # 页面布局为宽屏
        initial_sidebar_state="collapsed",  # 初始侧边栏状态为折叠
    )
    # 运行主仪表盘函数
    current_finance_summary()
