"""
该Streamlit应用程序提供股票买入和现金平账功能。
用户可以通过表单输入股票交易信息或进行现金余额调整。
"""

import datetime

import streamlit as st

from db.entity import CurrencyType
from service.transaction_management import (
    process_currency_adjustment,
    process_stock_purchase,
)


def _render_title() -> None:
    """渲染页面标题。"""
    st.title("✍️ 股票买入和现金平账")


def _render_stock_purchase_form() -> None:
    """渲染股票买入表单并处理提交。"""
    with st.form("买入股票"):
        st.subheader("买入股票")
        symbol = st.text_input("股票代码")
        trans_date = st.date_input("交易日期", datetime.date.today())
        shares = st.number_input("买入数量", min_value=0.0, step=1.0)
        price = st.number_input("买入价格", min_value=0.0)

        if st.form_submit_button("确认买入"):
            success, message = process_stock_purchase(symbol, trans_date, shares, price)
            if success:
                st.success(message)
            else:
                st.error(message)


def _render_currency_adjustment_form() -> None:
    """渲染现金平账表单并处理提交。"""
    with st.form("现金平账"):
        st.subheader("现金平账")
        currency_options = [e.value for e in CurrencyType]
        currency_type_str = st.selectbox("币种", options=currency_options)
        final_amount = st.number_input("调整后总额", min_value=0.0)

        if st.form_submit_button("确认平账"):
            selected_currency_type = CurrencyType(currency_type_str)
            success, message = process_currency_adjustment(
                final_amount, selected_currency_type
            )
            if success:
                st.success(message)
            else:
                st.error(message)


def main() -> None:
    """
    主函数，用于显示股票买入和现金平账页面。
    该函数负责协调UI渲染和业务逻辑调用。
    """
    _render_title()
    _render_stock_purchase_form()
    _render_currency_adjustment_form()


if __name__ == "__main__":
    # 配置Streamlit页面
    st.set_page_config(
        page_title="股票买入和现金平账",  # 页面标题
        page_icon="✍️",  # 页面图标
        layout="centered",  # 页面布局为居中
        initial_sidebar_state="collapsed",  # 初始侧边栏状态为折叠
    )
    # 运行主函数
    main()
