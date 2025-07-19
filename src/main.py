import streamlit

import db
from db.common import Base
from service.sync import sync

if __name__ == "__main__":
    streamlit.set_page_config(
        page_title="我的财富看板",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="collapsed",  # 关键设置：默认收起侧边栏
    )
    streamlit.balloons()

    with streamlit.spinner("数据同步中...", show_time=True):
        Base.metadata.create_all(db.engine)
        sync()

    streamlit.header("Lucky Curve 的财富管理系统")

    streamlit.page_link(
        "pages/1_当前财富看板.py",
        label="当前财富看板",
        icon="💳",
    )
    streamlit.page_link("pages/2_未来财富预测.py", label="未来财富预测", icon="🛠️")
    streamlit.page_link(
        "pages/3_股票买入和现金平账.py",
        label="股票买入和现金平账",
        icon="✍️",
    )
