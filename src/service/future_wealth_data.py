"""
该模块负责为“未来财富预测”页面提供所有必要的数据和模拟逻辑。
它封装了数据获取、过滤和蒙特卡洛模拟的逻辑，
确保展示层与数据层分离。
"""

from datetime import date, timedelta
from typing import List, Tuple

import pandas as pd

from db.entity import CurrencyType
from service.calculate import calculate_each_day_ticker_price
from service.simulate import monte_carlo_simulation


def fetch_and_filter_ticker_data() -> Tuple[List[str], float]:
    """
    获取并过滤股票数据，计算初始投资金额。

    Returns:
        Tuple[List[str], float]:
            - ticker_names: 过滤后的股票名称列表。
            - initial_value: 初始投资金额。
    """
    # 获取昨日的股票每日价格数据
    ticker_data = calculate_each_day_ticker_price(date.today() - timedelta(1))
    # 提取所有股票名称
    all_ticker_names = [name for (_, name) in ticker_data]

    # Streamlit的segmented_control用于过滤非股票资产
    # 这里不直接处理Streamlit组件，而是返回所有股票名称，由UI层处理过滤
    # 假设UI层会提供一个过滤后的列表
    # 为了保持数据层纯粹，这里只返回原始数据和计算初始值
    return all_ticker_names, ticker_data


def calculate_initial_investment(
    ticker_data: List[Tuple[float, str]], filtered_ticker_names: List[str]
) -> float:
    """
    根据过滤后的股票名称计算初始投资金额。

    Args:
        ticker_data (List[Tuple[float, str]]): 原始股票数据，包含价格和名称。
        filtered_ticker_names (List[str]): 用户选择的要包含在计算中的股票名称列表。

    Returns:
        float: 初始投资金额。
    """
    # 计算初始资金，只包含在过滤列表中的股票
    initial_value = sum(
        [price for (price, name) in ticker_data if name in filtered_ticker_names]
    )
    return initial_value


def perform_monte_carlo_simulation(
    initial_value: float, years: int, monthly_contribution: int
) -> pd.DataFrame:
    """
    执行蒙特卡洛模拟以预测未来财富。

    Args:
        initial_value (float): 初始投资金额。
        years (int): 投资年限。
        monthly_contribution (int): 每月投资金额。

    Returns:
        pd.DataFrame: 模拟结果的DataFrame，包含财富随时间的变化。
    """
    # 调用蒙特卡洛模拟服务
    simulation_result_df = monte_carlo_simulation(
        initial_value, years, monthly_contribution
    )
    return simulation_result_df
