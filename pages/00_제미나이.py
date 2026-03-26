import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="한-미 주식 비교 분석기", layout="wide")

st.title("📈 한-미 주요 주식 및 지수 비교")
st.sidebar.header("설정")

# 1. 종목 설정 (Key값이 정확해야 합니다)
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

# 2. 에러 방지용 안전장치
# ticker_dict의 키 목록을 가져옵니다.
all_options = list(ticker_dict.keys())

# 기본 선택값 설정 (리스트 내에 실제 존재하는 이름인지 확인 후 필터링)
desired_defaults = ["KOSPI 지수", "S&P 500", "삼성전자", "엔비디아"]
actual_defaults = [name for name in desired_defaults if name in all_options]

selected_names = st.sidebar.multiselect(
    "비교할 종목을 선택하세요", 
    options=all_options, 
    default=actual_defaults
)

# 3. 기간 선택
days = st.sidebar.slider("분석 기간 (일)", 30, 730, 365)
start_date = datetime.now() - timedelta(days=days)
end_date = datetime.now()

# 데이터 로드 함수
@st.cache_data
def load_data(tickers, start, end):
    if not tickers:
        return pd.DataFrame()
    # yfinance로 종가(Close) 데이터 다운로드
    data = yf.download(tickers, start=start, end=end)['Close']
    return data

if selected_names:
    with st.spinner('데이터를 불러오는 중입니다...'):
        selected_tickers = [ticker_dict[name] for name in selected_names]
        df = load_data(selected_tickers, start_date, end_date)
        
        if not df.empty:
            # 단일 종목 선택 시 Series를 DataFrame으로 변환
            if len(selected_names) == 1:
                df = df.to_frame()
                df.columns = selected_names
            else:
                # 티커(AAPL) 대신 사용자가 읽기 쉬운 이름(애플)으로 컬럼명 변경
                inv_dict = {v: k for k, v in ticker_dict.items()}
                df.columns = [inv_dict.get(col, col) for col in df.columns]

            # 4. 수익률 계산 (정규화: 시작 가격을 100으로 기준)
            df_norm = (df / df.iloc[0]) * 100

            # 상단 메인 지표(Metric) 표시
            cols = st.columns(len(selected_names))
            for i, name in enumerate(selected_names):
                if name in df.columns:
                    last_val = df[name].iloc[-1]
                    prev_val = df[name].iloc[0]
                    change = (last_val - prev_val) / prev_val * 100
                    cols[i].metric(name, f"{last_val:,.0f}", f"{change:.2f}%")

            # 5. 수익률 비교 차트 (Plotly)
            st.subheader(f"지난 {days}일간의 수익률 추이 (시작일 = 100)")
            fig = go.Figure()
            for col in df_norm.columns:
                fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm[col], name=col, mode='lines'))
            
            fig.update_layout(
                hovermode="x unified",
                xaxis_title="날짜",
                yaxis_title="정규화된 지수",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

            # 6. 원본 데이터 테이블
            with st.expander("데이터 상세보기"):
                st.dataframe(df.style.format("{:,.2f}"))
        else:
            st.error("데이터를 불러오지 못했습니다. 티커를 확인해 주세요.")
else:
    st.info("왼쪽 사이드바에서 종목을 선택해 주세요.")
