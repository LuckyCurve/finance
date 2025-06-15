@echo off
cd C:\Users\LuckyCurve\code\finance
echo %cd%
uv run streamlit run ./src/main.py
echo 执行完毕
pause