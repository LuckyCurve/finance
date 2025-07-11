from datetime import date, timedelta

import streamlit

from db.entity import CurrencyType
from service.calculate import (
    calculate_each_day_ticker_price,
)
from service.simulate import monte_carlo_simulation


def future_wealth_prediction():
    streamlit.title(":rainbow[未来财富预测]")
    ticker_data = calculate_each_day_ticker_price(date.today() - timedelta(1))

    ticker_names = [name for (_, name) in ticker_data]
    filter = streamlit.segmented_control(
        "过滤出非股票资产", ticker_names, selection_mode="multi"
    )
    ticker_names = set(ticker_names) - set(filter)

    initial_value = sum(
        [price for (price, name) in ticker_data if name in ticker_names]
    )
    streamlit.write(f"初始资金: {initial_value:.2f} {CurrencyType.USD.value}")

    year = streamlit.slider("投资时间", 0, 50)
    month_contribute = streamlit.slider("每月投资金额", 0, 50000, step=100)

    pd = monte_carlo_simulation(initial_value, year, month_contribute)
    streamlit.line_chart(pd, x="i", y="wealth", color="position")


if __name__ == "__main__":
    future_wealth_prediction()
