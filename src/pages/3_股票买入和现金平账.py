import datetime

import streamlit as st

from db.entity import CurrencyType
from service.adjust import adjust_currency
from service.transaction import buy_stock


def main():
    st.title("✍️ 股票买入和现金平账")

    # 买入股票表单
    with st.form("买入股票"):
        st.subheader("买入股票")
        symbol = st.text_input("股票代码")
        trans_date = st.date_input("交易日期", datetime.date.today())
        shares = st.number_input("买入数量", min_value=0.0, step=1.0)
        price = st.number_input("买入价格", min_value=0.0)

        if st.form_submit_button("确认买入"):
            if not symbol.strip():
                st.error("股票代码不能为空")
            elif shares <= 0 or price <= 0:
                st.error("买入数量和价格必须大于零")
            else:
                try:
                    buy_stock(symbol, trans_date, shares, price)
                    st.success("股票买入记录已添加")
                except Exception as e:
                    st.error(f"操作失败: {str(e)}")

    # 现金平账表单
    with st.form("现金平账"):
        st.subheader("现金平账")
        currency_type = st.selectbox("币种", options=[e.value for e in CurrencyType])
        final_amount = st.number_input("调整后总额", min_value=0.0)

        if st.form_submit_button("确认平账"):
            try:
                adjust_currency(final_amount, CurrencyType(currency_type))
                st.success("现金平账操作已完成")
            except Exception as e:
                st.error(f"操作失败: {str(e)}")


if __name__ == "__main__":
    main()
