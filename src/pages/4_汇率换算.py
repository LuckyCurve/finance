"""
This Streamlit application provides a currency exchange rate lookup and conversion tool.
It displays the latest exchange rates and allows users to convert amounts between currencies.
"""

import streamlit
from datetime import date

from adaptor.inbound.show_data import get_exchange_rate_details
from adaptor.outbound.currency import get_exchange_rate
from db.entity import CurrencyType


def display_exchange_rates() -> None:
    """
    Displays the latest exchange rates in a user-friendly format.
    """
    # Get today's date and exchange rates
    current_date, exchange_rates = get_exchange_rate(date.today())

    # Display the exchange rates
    streamlit.subheader(f"最新汇率数据 - {current_date.strftime('%Y-%m-%d')}")
    for currency, rate in exchange_rates.items():
        streamlit.write(f"1 USD = {float(rate):.2f} {currency}")

    # Display historical exchange rate chart
    streamlit.subheader("历史汇率变化")
    exchange_rate_df = get_exchange_rate_details()
    streamlit.line_chart(exchange_rate_df, x="日期", y="汇率", color="货币类型")


def currency_converter() -> None:
    """
    Provides a currency conversion tool for users to convert amounts between currencies.
    """
    streamlit.subheader("货币换算")

    # Get today's exchange rates
    current_date, exchange_rates = get_exchange_rate(date.today())

    # Input fields for conversion
    amount = streamlit.number_input("输入金额", value=1.0, min_value=0.0)
    from_currency = streamlit.selectbox("从哪种货币", options=list(exchange_rates.keys()))
    to_currency = streamlit.selectbox("转换为哪种货币", options=list(exchange_rates.keys()))

    # Perform conversion
    if from_currency == to_currency:
        converted_amount = amount
    elif from_currency == "USD":
        converted_amount = amount * float(exchange_rates[to_currency])
    else:
        # Convert from_currency to USD first, then to to_currency
        amount_in_usd = amount / float(exchange_rates[from_currency])
        converted_amount = amount_in_usd * float(exchange_rates[to_currency])

    # Display result
    streamlit.success(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")


def exchange_rate_dashboard() -> None:
    """Main function to display the exchange rate dashboard."""
    streamlit.title(":rainbow[汇率换算工具]")

    display_exchange_rates()
    streamlit.markdown("---")
    currency_converter()


if __name__ == "__main__":
    streamlit.set_page_config(
        page_title="汇率换算",
        page_icon="💱",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    exchange_rate_dashboard()
