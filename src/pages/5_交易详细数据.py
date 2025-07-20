import streamlit

from adaptor.inbound.show_data import (
    get_currency_transaction_details,
    get_ticker_transaction_details,
)


def transaction_details() -> None:
    """
    Main function to display the transaction details page.
    """
    streamlit.title(":rainbow[交易详细数据]")

    streamlit.caption("股票交易详细数据")
    ticker_details = get_ticker_transaction_details()
    streamlit.table(ticker_details)

    streamlit.caption("现金交易详细数据")
    currency_details = get_currency_transaction_details()
    streamlit.table(currency_details)


if __name__ == "__main__":
    streamlit.set_page_config(
        page_title="交易详细数据",
        page_icon="📜",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    transaction_details()
