"""
该Streamlit应用程序显示股票和现金的详细交易数据。
它从服务层获取数据，并以表格形式展示。
"""

import streamlit

import pandas as pd

from service.transaction_details_service import (
    fetch_currency_transaction_details,
    fetch_ticker_transaction_details,
)


def _render_title() -> None:
    """渲染页面标题。"""
    streamlit.title(":rainbow[交易详细数据]")


def _display_ticker_transaction_details(ticker_details_df: pd.DataFrame) -> None:
    """
    显示股票交易详细数据。

    Args:
        ticker_details_df (pd.DataFrame): 包含股票交易详情的DataFrame。
    """
    streamlit.caption("股票交易详细数据")
    streamlit.table(ticker_details_df)


def _display_currency_transaction_details(currency_details_df: pd.DataFrame) -> None:
    """
    显示现金交易详细数据。

    Args:
        currency_details_df (pd.DataFrame): 包含现金交易详情的DataFrame。
    """
    streamlit.caption("现金交易详细数据")
    streamlit.table(currency_details_df)


def transaction_details() -> None:
    """
    主函数，用于显示交易详细数据页面。
    该函数负责协调数据获取和UI渲染。
    """
    _render_title()

    # 1. 数据获取阶段
    # 获取股票交易详细数据
    ticker_details = fetch_ticker_transaction_details()
    # 获取现金交易详细数据
    currency_details = fetch_currency_transaction_details()

    # 2. UI展示阶段
    # 显示股票交易详情
    _display_ticker_transaction_details(ticker_details)
    # 显示现金交易详情
    _display_currency_transaction_details(currency_details)


if __name__ == "__main__":
    # 配置Streamlit页面
    streamlit.set_page_config(
        page_title="交易详细数据",  # 页面标题
        page_icon="📜",  # 页面图标
        layout="wide",  # 页面布局为宽屏
        initial_sidebar_state="collapsed",  # 初始侧边栏状态为折叠
    )
    # 运行主函数
    transaction_details()
