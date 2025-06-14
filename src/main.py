import pandas as pd
import streamlit

import db
from db.common import Base
from service.calculate import calculate_ticker_daily_change
from service.sync import sync

Base.metadata.create_all(db.engine)
sync()

if __name__ == "__main__":
    streamlit.set_page_config(page_title="我的财富看板", layout="wide")
    streamlit.title("我的财富看板")

    col1, col2 = streamlit.columns(2)
    col1.metric(label="我的财富总值", value="70 $", delta="-1.2")
    col2.metric(label="股票部分变化", value="70 $", delta="1.2")

    ticker_daily_change = calculate_ticker_daily_change()
    df = pd.DataFrame(list(ticker_daily_change.items()), columns=["Date", "收益值"])
    df = df.sort_values("Date").set_index("Date")
    col1, col2 = streamlit.columns(2)
    col1.line_chart(df, x_label="日期", y_label="收益值")
    col2.line_chart(df, x_label="日期", y_label="收益值")


def date():
    pass
    # buy_stock("0700.HK", date(2025, 6, 11), 165, 303.03)
    # buy_stock("0700.HK", date(2025, 6, 11), 166, 343.8)
    # buy_stock("GOOGL", date(2025, 6, 11), 1.8184, 154.17)
    # buy_stock("IAU", date(2025, 6, 11), 4.5126, 55.48)
    # buy_stock("SPLG", date(2025, 6, 11), 30.5197, 64.02)
    # buy_stock("GGB", date(2025, 6, 11), 338.9833, 2.95)
    # buy_stock("BIDU", date(2025, 6, 11), 15.3333, 84.57)
    # buy_stock("QQQM", date(2025, 6, 11), 4.6773, 213.87)
    # buy_stock("SGOV", date(2025, 6, 11), 222.4285, 100.49)
    # buy_stock("PDD", date(2025, 6, 11), 0.8267, 121.38)
    # buy_currency(645576.25, CurrencyType.CNY, comment="微众银行")
    # buy_currency(51714.94, CurrencyType.CNY, comment="招商银行")
    # buy_currency(129715.35, CurrencyType.HKD, comment="汇丰香港")
