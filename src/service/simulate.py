from math import sqrt

import numpy as np
from pandas import DataFrame

# 进行预测


def monte_carlo_simulation(
    initial_wealth: float,
    years: int,
    month_contribution: float,
    mean_return: float,
    std_return: float,
) -> DataFrame:
    # 参数
    # 特别注意: 是投资回报率符合正态分布, 不是 (1 + 投资回报率) 符合正态分布
    mean_return = (1 + mean_return) ** (1 / 12) - 1
    std_return = std_return / sqrt(12)
    simulations = 100_000

    # 生成所有模拟的每月收益率 (simulations, months)
    r = np.random.normal(mean_return, std_return, size=(simulations, years * 12))

    # 初始化财富数组
    wealth = np.full(simulations, initial_wealth, dtype=np.float64)

    # 批量模拟每个月
    for m in range(years * 12):
        wealth = (wealth + month_contribution) * (1 + r[:, m])

    # 计算分位数
    percentiles = np.percentile(wealth, [5, 25, 50, 75, 95])
    wealth_distribution = [
        (years, "5%", round(float(percentiles[0]), 2)),
        (years, "25%", round(float(percentiles[1]), 2)),
        (years, "50%", round(float(percentiles[2]), 2)),
        (years, "75%", round(float(percentiles[3]), 2)),
        (years, "95%", round(float(percentiles[4]), 2)),
    ]

    wealth_distribution += [
        (0, position, round(float(initial_wealth), 2))
        for (_, position, _) in wealth_distribution
    ]
    wealth_distribution += [
        (0, "standard", round(float(initial_wealth), 2)),
        (
            years,
            "standard",
            round(float(initial_wealth + years * 12 * month_contribution), 2),
        ),
    ]

    return DataFrame(wealth_distribution, columns=["i", "position", "wealth"])
