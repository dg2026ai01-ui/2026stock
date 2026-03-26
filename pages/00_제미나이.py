import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="한-미 주식 비교 분석기", layout="wide")

st.title("📈 한-미 주요 주식 및 지수 비교")
st.sidebar.header("설정")

# 1. 종목 선택 (티커 설정)
# 한국 주식은 끝에 .KS(코스피) 또는 .KQ(코스닥)를 붙여야 합니다.
ticker_dict = {
    "KOSPI 지수": "^KS11",
    "KOSDAQ 지수": "^KQ11",
    "S&P 500": "^GSPC",
    "나스닥 종합": "^IXIC",
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "에코프로": "086520.KQ",
    "애플(Apple)": "AAPL",
    "테슬라(Tesla)": "TSLA",
    "엔비디아(NVIDIA)": "NVDA",
    "마이크로소프트": "MSFT"
}

selected_names = st.sidebar.multiselect(
    "비교할 종목을 선택하세요", 
    options=list(ticker_dict.keys()), 
    default=["KOSPI 지수", "S&P 500", "삼성전자", "엔비디아"]
)

# 2. 기간 선택
days = st.sidebar.slider("분석 기간 (일)", 30, 730, 365)
start_date = datetime.now() - timedelta(days=days)
end_date = datetime.now()

# 데이터 로드 함수
@st.cache_data
def load_data(tickers, start, end):
    data = yf.download(tickers, start=start, end=end)['Close']
    return data

if selected_names:
    selected_tickers = [ticker_dict[name] for name in selected_names]
    df = load_data(selected_tickers, start_date, end_date)
    
    if len(selected_names) == 1:
        df = df.to_frame()
        df.columns = selected_names
    else:
        # 티커명을 다시 한글 이름으로 변경
        inv_dict = {v: k for k, v in ticker_dict.items()}
        df.columns = [inv_dict[col] for col in df.columns]

    # 3. 수익률 계산 (정규화: 시작가격을 100으로 기준)
    # 비교를 위해 모든 주식의 시작점을 0% 또는 100으로 맞춥니다.
    df_norm = (df / df.iloc[0]) * 100

    # 메인 화면 지표(Metric) 표시
    cols = st.columns(len(selected_names))
    for i, name in enumerate(selected_names):
        last_val = df[name].iloc[-1]
        prev_val = df[name].iloc[0]
        change = (last_val - prev_val) / prev_val * 100
        cols[i].metric(name, f"{last_val:,.0f}", f"{change:.2f}%")

    # 4. 차트 그리기 (Plotly 사용)
    st.subheader(f"지난 {days}일간의 수익률 비교 (시작 지점 = 100)")
    fig = go.Figure()
    for col in df_norm.columns:
        fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm[col], name=col, mode='lines'))
    
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="날짜",
        yaxis_title="정규화된 가격",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 5. 데이터 테이블 표시
    with st.expander("상세 데이터 보기"):
        st.dataframe(df.tail())
else:
    st.warning("비교할 종목을 하나 이상 선택해 주세요.")
