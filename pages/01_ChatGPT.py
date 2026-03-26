import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="주식 비교 앱", layout="wide")

st.title("📊 한국 🇰🇷 vs 미국 🇺🇸 주식 비교")

# 주요 종목 리스트
korea_stocks = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS"
}

us_stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN"
}

# 선택 UI
col1, col2 = st.columns(2)

with col1:
    selected_korea = st.multiselect(
        "🇰🇷 한국 주식 선택",
        list(korea_stocks.keys())
    )

with col2:
    selected_us = st.multiselect(
        "🇺🇸 미국 주식 선택",
        list(us_stocks.keys())
    )

period = st.selectbox(
    "기간 선택",
    ["1mo", "3mo", "6mo", "1y", "3y", "5y"]
)

# 선택된 종목 합치기
selected_symbols = []

for stock in selected_korea:
    selected_symbols.append((stock, korea_stocks[stock]))

for stock in selected_us:
    selected_symbols.append((stock, us_stocks[stock]))

if len(selected_symbols) == 0:
    st.warning("종목을 선택해주세요!")
    st.stop()

# 데이터 가져오기
@st.cache_data
def load_data(symbols, period):
    data = {}
    for name, symbol in symbols:
        df = yf.download(symbol, period=period)
        data[name] = df
    return data

data = load_data(selected_symbols, period)

# 수익률 계산
returns = {}

for name, df in data.items():
    if not df.empty:
        start_price = df["Close"].iloc[0]
        end_price = df["Close"].iloc[-1]
        returns[name] = (end_price / start_price - 1) * 100

# 수익률 표시
st.subheader("📈 수익률 비교 (%)")

returns_df = pd.DataFrame.from_dict(returns, orient='index', columns=['Return (%)'])
st.dataframe(returns_df.style.format("{:.2f}%"))

# 차트
st.subheader("📊 가격 비교 차트")

fig = go.Figure()

for name, df in data.items():
    if not df.empty:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Close"],
            mode='lines',
            name=name
        ))

fig.update_layout(
    height=600,
    xaxis_title="날짜",
    yaxis_title="가격",
    legend_title="종목"
)

st.plotly_chart(fig, use_container_width=True)
