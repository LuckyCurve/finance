import streamlit as st
from sqlalchemy.orm import Session

from db import engine
from db.entity import Config

st.set_page_config(page_title="设置", page_icon="⚙️")

st.title("⚙️ 设置")

st.write("---")

if st.button("清除所有配置和缓存"):
    try:
        # 删除 config 表所有数据
        with Session(engine) as session:
            session.query(Config).delete()
            session.commit()

        # 清空 streamlit 的缓存
        st.cache_data.clear()
        st.cache_resource.clear()

        st.success("已成功清除所有配置和缓存！")
    except Exception as e:
        st.error(f"清除失败：{e}")
