import os

import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini
from agno.team import Team
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools

st.title("AI Investment Agent 📈🤖")
st.caption(
    "This app allows you to compare the performance of two stocks and generate detailed reports."
)

api_key = os.environ["GEMINI_API_KEY"]
main_model = "gemini-2.5-pro"
fetch_model = "gemini-2.5-flash"

assistant = Agent(
    model=Gemini(id=main_model, api_key=api_key),
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

web_agent = Agent(
    name="Web Search Agent",
    role="Handle web search requests and general research",
    model=Gemini(id=fetch_model, api_key=api_key),
    tools=[GoogleSearchTools()],
    instructions="Always include sources",
    add_datetime_to_instructions=True,
)

finance_agent = Agent(
    name="Finance Agent",
    role="Handle financial data requests and market analysis",
    model=Gemini(id=main_model, api_key=api_key),
    tools=[
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
        )
    ],
    instructions=[
        "Use tables to display stock prices, fundamentals (P/E, Market Cap), and recommendations.",
        "Clearly state the company name and ticker symbol.",
        "Focus on delivering actionable financial insights.",
    ],
    add_datetime_to_instructions=True,
)

reasoning_finance_team = Team(
    name="Reasoning Finance Team",
    mode="coordinate",
    model=Gemini(id=main_model, api_key=api_key),
    members=[web_agent, finance_agent],
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        "Collaborate to provide comprehensive financial and investment insights",
        "Consider both fundamental analysis and market sentiment",
        "Use tables and charts to display data clearly and professionally",
        "Present findings in a structured, easy-to-follow format",
        "Only output the final consolidated analysis, not individual agent responses",
        "Analyze stocks using Graham's value investing theory",
        "始终使用中文输出",
    ],
    markdown=True,
    show_members_responses=True,
    enable_agentic_context=True,
    add_datetime_to_instructions=True,
    success_criteria="The team has provided a complete financial analysis with data, visualizations, risk assessment, and actionable investment recommendations supported by quantitative analysis and market research.",
)

stock = st.text_input("Enter first stock symbol (e.g. AAPL)")

if stock:
    with st.spinner(f"Analyzing {stock}..."):
        query = f"Analyze the stock - {stock} and make a detailed report for an investment trying to invest in this stock"
        response = assistant.run(query, stream=False)
        st.markdown(response.content)
        st.download_button(
            label="下载分析报告",
            data=response.content.encode("utf-8"),
            file_name=f"{stock}_analysis_report.md",
            mime="text/markdown",
        )
        st.balloons()
