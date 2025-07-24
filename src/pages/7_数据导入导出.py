import streamlit as st
from sqlalchemy.orm import Session
import db
from service.transaction_io_service import TransactionIOService
from db.entity import Transaction

st.set_page_config(page_title="数据导入导出", layout="wide")

st.title("数据导入导出")

if st.button("导出所有交易数据"):
    with Session(db.engine) as session:
        transactions = session.query(Transaction).all()
        json_data = TransactionIOService.export_transactions(transactions)
        st.download_button(
            label="下载JSON文件",
            data=json_data,
            file_name="transactions.json",
            mime="application/json",
        )

uploaded_file = st.file_uploader("上传JSON文件进行导入", type=["json"])

if uploaded_file is not None:
    with Session(db.engine) as session:
        try:
            json_input = uploaded_file.getvalue().decode("utf-8")
            transactions = TransactionIOService.import_transactions(json_input)

            session.add_all(transactions)
            session.commit()
            st.success("数据导入成功！")
        except Exception as e:
            session.rollback()
            st.error(f"数据导入失败: {e}")
