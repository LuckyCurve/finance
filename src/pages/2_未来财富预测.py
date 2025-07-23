"""
该Streamlit应用程序提供未来财富预测功能，
通过蒙特卡洛模拟展示不同投资策略下的财富增长趋势。
"""

from typing import List, Tuple

import pandas as pd
import streamlit

from db.entity import CurrencyType
from service.future_wealth_data import (
    calculate_initial_investment,
    fetch_and_filter_ticker_data,
    perform_monte_carlo_simulation,
)


def _render_title() -> None:
    """渲染页面标题。"""
    streamlit.title(":rainbow[未来财富预测]")


def _get_user_inputs(
    all_ticker_names: List[str],
) -> Tuple[List[str], int, int, float, float]:
    """
    获取用户输入，包括非股票资产过滤、投资时间、每月投资金额、平均回报率和标准差。

    Args:
        all_ticker_names (List[str]): 所有股票名称列表。

    Returns:
        Tuple[List[str], int, int, float, float]:
            - filtered_ticker_names: 用户选择的要包含在计算中的股票名称列表。
            - years: 用户选择的投资时间（年）。
            - monthly_contribution: 用户选择的每月投资金额。
            - mean_return: 用户选择的每月平均回报率。
            - std_return: 用户选择的每月回报率的标准差。
    """
    # 允许用户过滤掉非股票资产，选择不参与模拟的股票
    filter_out_names = streamlit.segmented_control(
        "过滤出非股票资产", all_ticker_names, selection_mode="multi"
    )
    # 计算实际参与模拟的股票名称
    filtered_ticker_names = list(set(all_ticker_names) - set(filter_out_names))

    # 获取用户输入的投资时间（年）
    years = streamlit.slider("投资时间", 0, 50)
    # 获取用户输入的每月投资金额
    monthly_contribution = streamlit.slider("每月投资金额", 0, 50000, step=100)
    # 添加高级选项以配置蒙特卡洛模拟参数
    with streamlit.expander("高级选项"):
        # 默认值基于年化8%回报率和18%标准差
        mean_return = streamlit.slider("年度平均回报率", -0.2, 0.2, 0.08, 0.01, "%.2f")
        std_return = streamlit.slider("年度回报率标准差", 0.0, 0.4, 0.18, 0.01, "%.2f")

    return filtered_ticker_names, years, monthly_contribution, mean_return, std_return


def _display_initial_investment(initial_value: float) -> None:
    """
    显示初始投资金额。

    Args:
        initial_value (float): 初始投资金额。
    """
    streamlit.write(f"初始资金: {initial_value:.2f} {CurrencyType.USD.value}")


def _display_simulation_chart(simulation_df: pd.DataFrame) -> None:
    """
    显示蒙特卡洛模拟结果的折线图。

    Args:
        simulation_df (pd.DataFrame): 蒙特卡洛模拟结果的DataFrame。
    """
    streamlit.line_chart(simulation_df, x="i", y="wealth", color="position")


def future_wealth_prediction() -> None:
    """
    主函数，用于显示未来财富预测仪表盘。
    该函数负责协调数据获取、用户输入、模拟计算和UI渲染。
    """
    _render_title()

    # 1. 数据获取阶段
    # 获取所有股票名称和原始股票数据
    all_ticker_names, ticker_data = fetch_and_filter_ticker_data()

    # 2. 用户输入阶段
    # 获取用户关于过滤、投资时间、每月投资金额的输入
    (
        filtered_ticker_names,
        years,
        monthly_contribution,
        mean_return,
        std_return,
    ) = _get_user_inputs(all_ticker_names)

    # 3. 数据计算阶段
    # 根据用户过滤后的股票计算初始投资金额
    initial_value = calculate_initial_investment(ticker_data, filtered_ticker_names)
    # 执行蒙特卡洛模拟
    simulation_df = perform_monte_carlo_simulation(
        initial_value, years, monthly_contribution, mean_return, std_return
    )

    # 4. UI展示阶段
    # 显示初始投资金额
    _display_initial_investment(initial_value)
    # 显示模拟结果图表
    _display_simulation_chart(simulation_df)


if __name__ == "__main__":
    # 配置Streamlit页面
    streamlit.set_page_config(
        page_title="未来财富预测",  # 页面标题
        page_icon="💰",  # 页面图标
        layout="wide",  # 页面布局为宽屏
        initial_sidebar_state="collapsed",  # 初始侧边栏状态为折叠
    )
    # 运行主预测函数
    future_wealth_prediction()
