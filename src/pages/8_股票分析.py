import os

import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools

st.title("AI Investment Agent 📈🤖")
st.caption(
    "This app allows you to compare the performance of two stocks and generate detailed reports."
)


openai_api_key = os.getenv("GEMINI_API_KEY")

if openai_api_key:
    assistant = Agent(
        model=Gemini(id="gemini-2.5-pro", api_key=openai_api_key),
        tools=[
            ReasoningTools(add_instructions=True, add_few_shot=True),
            YFinanceTools(
                stock_price=True,
                company_info=True,
                income_statements=True,
                key_financial_ratios=True,
                analyst_recommendations=True,
                stock_fundamentals=True,
                company_news=True,
                technical_indicators=True,
                historical_prices=True,
            ),
        ],
        show_tool_calls=True,
        description="You are an investment analyst that researches stock prices, analyst recommendations, and stock fundamentals.",
        instructions=[
            "Format your response using markdown and use tables to display data where possible.",
            "Analyze stocks using Graham's value investing theory",
            "最终请使用中文进行回答",
            "请完整执行分析并提供最终结论，不要只显示思考过程",
        ],
    )

    stock = st.text_input("Enter first stock symbol (e.g. AAPL)")

    if stock:
        with st.spinner(f"Analyzing {stock}..."):
            query = f"Analyze the stock - {stock} and make a detailed report for an investment trying to invest in this stock"
            response = assistant.run(query, stream=False)
            st.markdown(response.content)
            st.balloons()
