"""
该Streamlit应用程序提供汇率查询和货币换算工具。
它显示最新的汇率，并允许用户在不同货币之间进行金额换算。
"""

import streamlit
from datetime import date
from typing import Dict

import pandas as pd

from pages.components.charts import create_historical_exchange_rate_chart
from service.exchange_rate_service import (
    convert_currency,
    fetch_historical_exchange_rates,
    fetch_latest_exchange_rates,
)


def _render_title() -> None:
    """渲染页面标题。"""
    streamlit.title(":rainbow[汇率换算工具]")


def _display_latest_exchange_rates(
    current_date: date, exchange_rates: Dict[str, float]
) -> None:
    """
    显示最新的汇率数据。

    Args:
        current_date (date): 汇率数据的日期。
        exchange_rates (Dict[str, float]): 货币代码到汇率的映射字典。
    """
    streamlit.subheader(f"最新汇率数据 - {current_date.strftime('%Y-%m-%d')}")
    for currency, rate in exchange_rates.items():
        streamlit.write(f"1 USD = {rate:.2f} {currency}")


def _render_currency_converter(exchange_rates: Dict[str, float]) -> None:
    """
    渲染货币换算工具并处理转换逻辑。

    Args:
        exchange_rates (Dict[str, float]): 货币代码到汇率的映射字典。
    """
    streamlit.subheader("货币换算")

    # 输入字段
    amount = streamlit.number_input("输入金额", value=1.0, min_value=0.0)
    currency_options = list(exchange_rates.keys())
    from_currency = streamlit.selectbox("从哪种货币", options=currency_options)
    to_currency = streamlit.selectbox("转换为哪种货币", options=currency_options)

    # 执行转换并显示结果
    converted_amount = convert_currency(amount, from_currency, to_currency, exchange_rates)
    streamlit.success(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")


def exchange_rate_dashboard() -> None:
    """
    主函数，用于显示汇率换算仪表盘。
    该函数负责协调数据获取、UI渲染和货币转换功能。
    """
    _render_title()

    # 1. 数据获取阶段
    # 获取最新汇率数据
    current_date, latest_exchange_rates = fetch_latest_exchange_rates()
    # 获取历史汇率数据
    historical_exchange_rates_df = fetch_historical_exchange_rates()

    # 2. UI展示阶段
    # 显示最新汇率
    _display_latest_exchange_rates(current_date, latest_exchange_rates)
    # 添加分隔线
    streamlit.markdown("---")
    # 显示历史汇率图表
    create_historical_exchange_rate_chart(historical_exchange_rates_df)
    # 添加分隔线
    streamlit.markdown("---")
    # 渲染货币换算工具
    _render_currency_converter(latest_exchange_rates)


if __name__ == "__main__":
    # 配置Streamlit页面
    streamlit.set_page_config(
        page_title="汇率换算",  # 页面标题
        page_icon="💱",  # 页面图标
        layout="wide",  # 页面布局为宽屏
        initial_sidebar_state="collapsed",  # 初始侧边栏状态为折叠
    )
    # 运行主仪表盘函数
    exchange_rate_dashboard()
