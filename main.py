import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 주식 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 커스텀 CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Noto+Sans+KR:wght@300;400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 배경 */
.stApp {
    background: #0a0e1a;
    color: #e0e6f0;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: #0f1526;
    border-right: 1px solid #1e2d4a;
}

section[data-testid="stSidebar"] .stMarkdown h2 {
    color: #4fc3f7;
    font-size: 1rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

/* 헤더 */
.main-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.2rem;
    font-weight: 600;
    background: linear-gradient(135deg, #4fc3f7 0%, #81d4fa 50%, #b3e5fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}

.sub-header {
    color: #546e8a;
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    margin-bottom: 2rem;
}

/* 메트릭 카드 */
.metric-card {
    background: linear-gradient(145deg, #111827, #1a2540);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s;
}
.metric-card:hover {
    border-color: #4fc3f7;
}
.metric-label {
    font-size: 0.72rem;
    color: #5a7a9a;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 600;
    color: #e0f0ff;
}
.metric-value.positive { color: #4dd0a0; }
.metric-value.negative { color: #f06292; }

/* 섹션 타이틀 */
.section-title {
    font-size: 0.78rem;
    color: #4fc3f7;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    border-left: 3px solid #4fc3f7;
    padding-left: 0.8rem;
    margin: 1.5rem 0 1rem 0;
    font-family: 'IBM Plex Mono', monospace;
}

/* 테이블 스타일 */
.dataframe {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    background: #111827 !important;
}

/* 버튼 */
.stButton > button {
    background: linear-gradient(135deg, #1565c0, #0d47a1);
    color: #e3f2fd;
    border: 1px solid #1e88e5;
    border-radius: 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    letter-spacing: 0.05em;
    padding: 0.5rem 1.5rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1976d2, #1565c0);
    border-color: #4fc3f7;
    transform: translateY(-1px);
}

/* 구분선 */
hr {
    border-color: #1e2d4a !important;
    margin: 1.5rem 0;
}

/* select box */
.stSelectbox label, .stMultiSelect label, .stSlider label {
    color: #7a9bbf !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.05em;
}

/* 탭 */
.stTabs [data-baseweb="tab-list"] {
    background: #0f1526;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: #546e8a;
    border-radius: 7px;
    padding: 0.4rem 1rem;
}
.stTabs [aria-selected="true"] {
    background: #1a2d4a !important;
    color: #4fc3f7 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 주식 종목 정의
# ─────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자":    "005930.KS",
    "SK하이닉스":  "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "현대차":      "005380.KS",
    "POSCO홀딩스": "005490.KS",
    "카카오":      "035720.KS",
    "네이버":      "035420.KS",
    "셀트리온":    "068270.KS",
    "기아":        "000270.KS",
    "KB금융":      "105560.KS",
}

US_STOCKS = {
    "Apple":      "AAPL",
    "NVIDIA":     "NVDA",
    "Microsoft":  "MSFT",
    "Amazon":     "AMZN",
    "Alphabet":   "GOOGL",
    "Meta":       "META",
    "Tesla":      "TSLA",
    "Berkshire":  "BRK-B",
    "JPMorgan":   "JPM",
    "Broadcom":   "AVGO",
}

INDICES = {
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
}

# ─────────────────────────────────────────────
# 헬퍼 함수
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_data(tickers: list, start: str, end: str) -> pd.DataFrame:
    try:
        raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            close = raw["Close"]
        else:
            close = raw[["Close"]] if "Close" in raw.columns else raw
        return close.dropna(how="all")
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_info(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).fast_info
        return {
            "market_cap": getattr(info, "market_cap", None),
            "last_price": getattr(info, "last_price", None),
        }
    except:
        return {}

def calc_returns(df: pd.DataFrame) -> pd.DataFrame:
    """누적 수익률(%) 계산"""
    return (df / df.iloc[0] - 1) * 100

def calc_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """각 종목별 핵심 지표 계산"""
    ret = df.pct_change().dropna()
    rows = []
    for col in df.columns:
        s = df[col].dropna()
        r = ret[col].dropna()
        total_ret = (s.iloc[-1] / s.iloc[0] - 1) * 100
        ann_vol = r.std() * np.sqrt(252) * 100
        sharpe = (r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else 0
        max_dd = ((s / s.cummax()) - 1).min() * 100
        rows.append({
            "종목": col,
            "현재가": f"{s.iloc[-1]:,.2f}",
            "총수익률(%)": round(total_ret, 2),
            "연간변동성(%)": round(ann_vol, 2),
            "샤프지수": round(sharpe, 2),
            "최대낙폭(%)": round(max_dd, 2),
        })
    return pd.DataFrame(rows).set_index("종목")

# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p style="font-family:IBM Plex Mono;font-size:1.1rem;color:#4fc3f7;font-weight:600;">📊 설정</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("## 📅 기간 선택")
    period_map = {
        "1개월": 30, "3개월": 90, "6개월": 180,
        "1년": 365, "2년": 730, "3년": 1095,
    }
    period_label = st.select_slider("", options=list(period_map.keys()), value="1년")
    days = period_map[period_label]
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)

    st.markdown("---")
    st.markdown("## 🇰🇷 한국 주식")
    kr_selected = st.multiselect(
        "종목 선택",
        options=list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "현대차"],
    )

    st.markdown("## 🇺🇸 미국 주식")
    us_selected = st.multiselect(
        "종목 선택",
        options=list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Microsoft"],
    )

    st.markdown("---")
    st.markdown("## 📈 지수 포함")
    idx_selected = st.multiselect(
        "지수 선택",
        options=list(INDICES.keys()),
        default=["KOSPI", "S&P 500"],
    )

    fetch_btn = st.button("🔄  데이터 불러오기", use_container_width=True)

# ─────────────────────────────────────────────
# 메인 헤더
# ─────────────────────────────────────────────
st.markdown('<div class="main-header">글로벌 주식 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">한국 · 미국 주요 종목 수익률 & 차트 비교 분석</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 데이터 로드
# ─────────────────────────────────────────────
all_label_ticker = {}
for n in kr_selected:
    all_label_ticker[n] = KR_STOCKS[n]
for n in us_selected:
    all_label_ticker[n] = US_STOCKS[n]
for n in idx_selected:
    all_label_ticker[n] = INDICES[n]

if not all_label_ticker:
    st.info("왼쪽 사이드바에서 종목을 선택한 뒤 **데이터 불러오기** 버튼을 누르세요.")
    st.stop()

tickers = list(all_label_ticker.values())
labels  = list(all_label_ticker.keys())

with st.spinner("데이터를 불러오는 중..."):
    raw_df = fetch_data(tickers, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

if raw_df.empty:
    st.error("데이터를 가져오지 못했습니다. 종목 코드 또는 네트워크를 확인하세요.")
    st.stop()

# 컬럼명을 사람이 읽기 쉬운 이름으로 변환
ticker_to_label = {v: k for k, v in all_label_ticker.items()}
raw_df.columns = [ticker_to_label.get(c, c) for c in raw_df.columns]
raw_df = raw_df[[c for c in labels if c in raw_df.columns]]

# ─────────────────────────────────────────────
# 상단 KPI 카드
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">최근 수익률 요약</div>', unsafe_allow_html=True)

kpi_cols = st.columns(min(len(raw_df.columns), 6))
for i, col in enumerate(raw_df.columns[:6]):
    s = raw_df[col].dropna()
    if len(s) < 2:
        continue
    ret_pct = (s.iloc[-1] / s.iloc[0] - 1) * 100
    cls = "positive" if ret_pct >= 0 else "negative"
    arrow = "▲" if ret_pct >= 0 else "▼"
    with kpi_cols[i % 6]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{col}</div>
            <div class="metric-value {cls}">{arrow} {abs(ret_pct):.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 탭
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 누적 수익률", "🕯 캔들 차트", "📊 성과 비교", "📋 데이터 테이블"])

# ── TAB 1: 누적 수익률 ──────────────────────
with tab1:
    st.markdown('<div class="section-title">누적 수익률 비교 (%)</div>', unsafe_allow_html=True)
    ret_df = calc_returns(raw_df)

    fig = go.Figure()
    palette = px.colors.qualitative.Set2 + px.colors.qualitative.Pastel
    for i, col in enumerate(ret_df.columns):
        color = palette[i % len(palette)]
        is_idx = col in idx_selected
        fig.add_trace(go.Scatter(
            x=ret_df.index, y=ret_df[col],
            name=col,
            mode="lines",
            line=dict(
                width=2.5 if not is_idx else 1.5,
                dash="dot" if is_idx else "solid",
                color=color,
            ),
            hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m-%d}}<br>수익률: %{{y:.2f}}%<extra></extra>",
        ))

    fig.add_hline(y=0, line_dash="dash", line_color="#2a3a5a", line_width=1)
    fig.update_layout(
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0f1526",
        font=dict(family="IBM Plex Mono, Noto Sans KR", color="#8ab0cc", size=11),
        legend=dict(bgcolor="#111827", bordercolor="#1e2d4a", borderwidth=1, font=dict(size=10)),
        xaxis=dict(gridcolor="#141e30", showgrid=True, zeroline=False),
        yaxis=dict(gridcolor="#141e30", showgrid=True, zeroline=False, ticksuffix="%"),
        hovermode="x unified",
        height=480,
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    # 수익률 히트맵 (월별)
    if len(raw_df.columns) > 0:
        st.markdown('<div class="section-title">월별 수익률 히트맵</div>', unsafe_allow_html=True)
        monthly = raw_df.resample("ME").last().pct_change() * 100
        monthly.index = monthly.index.strftime("%Y-%m")
        monthly = monthly.dropna()
        if not monthly.empty:
            fig_hm = go.Figure(go.Heatmap(
                z=monthly.T.values,
                x=monthly.index,
                y=monthly.columns.tolist(),
                colorscale=[[0, "#c62828"], [0.5, "#1a2540"], [1, "#1b5e20"]],
                zmid=0,
                text=monthly.T.round(1).astype(str).values,
                texttemplate="%{text}%",
                textfont=dict(size=9, family="IBM Plex Mono"),
                hovertemplate="<b>%{y}</b><br>%{x}<br>%{z:.2f}%<extra></extra>",
            ))
            fig_hm.update_layout(
                paper_bgcolor="#0a0e1a",
                plot_bgcolor="#0f1526",
                font=dict(color="#8ab0cc", size=10),
                height=max(200, len(monthly.columns) * 38 + 60),
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(tickangle=-45),
            )
            st.plotly_chart(fig_hm, use_container_width=True)

# ── TAB 2: 캔들 차트 ────────────────────────
with tab2:
    st.markdown('<div class="section-title">캔들스틱 차트</div>', unsafe_allow_html=True)
    candle_target = st.selectbox("종목 선택", options=list(all_label_ticker.keys()))
    candle_ticker = all_label_ticker[candle_target]

    @st.cache_data(ttl=300)
    def fetch_ohlcv(ticker, start, end):
        df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna()

    ohlcv = fetch_ohlcv(candle_ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

    if not ohlcv.empty and all(c in ohlcv.columns for c in ["Open","High","Low","Close"]):
        fig_c = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            row_heights=[0.75, 0.25], vertical_spacing=0.03,
        )
        fig_c.add_trace(go.Candlestick(
            x=ohlcv.index,
            open=ohlcv["Open"], high=ohlcv["High"],
            low=ohlcv["Low"],  close=ohlcv["Close"],
            name=candle_target,
            increasing_line_color="#4dd0a0", decreasing_line_color="#f06292",
            increasing_fillcolor="#4dd0a0", decreasing_fillcolor="#f06292",
        ), row=1, col=1)

        # 이동평균선
        for w, color in [(20, "#ffd54f"), (60, "#80cbc4"), (120, "#ef9a9a")]:
            if len(ohlcv) >= w:
                fig_c.add_trace(go.Scatter(
                    x=ohlcv.index, y=ohlcv["Close"].rolling(w).mean(),
                    name=f"MA{w}", line=dict(color=color, width=1.2, dash="dot"),
                    hovertemplate=f"MA{w}: %{{y:,.2f}}<extra></extra>",
                ), row=1, col=1)

        # 거래량
        if "Volume" in ohlcv.columns:
            vol_colors = ["#4dd0a0" if c >= o else "#f06292"
                          for c, o in zip(ohlcv["Close"], ohlcv["Open"])]
            fig_c.add_trace(go.Bar(
                x=ohlcv.index, y=ohlcv["Volume"],
                name="거래량", marker_color=vol_colors, opacity=0.7,
            ), row=2, col=1)

        fig_c.update_layout(
            paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1526",
            font=dict(family="IBM Plex Mono", color="#8ab0cc", size=10),
            legend=dict(bgcolor="#111827", bordercolor="#1e2d4a", borderwidth=1, font=dict(size=10)),
            xaxis=dict(gridcolor="#141e30", rangeslider_visible=False),
            xaxis2=dict(gridcolor="#141e30"),
            yaxis=dict(gridcolor="#141e30"),
            yaxis2=dict(gridcolor="#141e30"),
            height=560,
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig_c, use_container_width=True)
    else:
        st.warning("캔들 데이터를 불러오지 못했습니다.")

# ── TAB 3: 성과 비교 ────────────────────────
with tab3:
    st.markdown('<div class="section-title">리스크-수익률 산점도</div>', unsafe_allow_html=True)
    metrics_df = calc_metrics(raw_df)

    fig_s = go.Figure()
    for i, name in enumerate(metrics_df.index):
        color = palette[i % len(palette)]
        is_kr = name in kr_selected
        is_idx = name in idx_selected
        marker_symbol = "circle" if is_kr else ("diamond" if is_idx else "square")
        fig_s.add_trace(go.Scatter(
            x=[metrics_df.loc[name, "연간변동성(%)"]],
            y=[metrics_df.loc[name, "총수익률(%)"]],
            mode="markers+text",
            name=name,
            text=[name],
            textposition="top center",
            textfont=dict(size=9, color=color),
            marker=dict(size=14, color=color, symbol=marker_symbol,
                        line=dict(width=1, color="#1a2540")),
            hovertemplate=(
                f"<b>{name}</b><br>"
                "변동성: %{x:.1f}%<br>"
                "총수익률: %{y:.1f}%<extra></extra>"
            ),
        ))

    fig_s.add_hline(y=0, line_dash="dash", line_color="#2a3a5a", line_width=1)
    fig_s.update_layout(
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1526",
        font=dict(family="IBM Plex Mono", color="#8ab0cc", size=10),
        xaxis=dict(title="연간 변동성 (%)", gridcolor="#141e30"),
        yaxis=dict(title="총 수익률 (%)", gridcolor="#141e30", ticksuffix="%"),
        showlegend=False, height=460,
        margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_s, use_container_width=True)

    # 수익률 막대차트
    st.markdown('<div class="section-title">총수익률 비교 막대</div>', unsafe_allow_html=True)
    sorted_m = metrics_df.sort_values("총수익률(%)", ascending=True)
    bar_colors = ["#4dd0a0" if v >= 0 else "#f06292" for v in sorted_m["총수익률(%)"]]
    fig_b = go.Figure(go.Bar(
        x=sorted_m["총수익률(%)"], y=sorted_m.index,
        orientation="h", marker_color=bar_colors,
        text=sorted_m["총수익률(%)"].apply(lambda x: f"{x:+.1f}%"),
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=10),
    ))
    fig_b.update_layout(
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1526",
        font=dict(family="IBM Plex Mono", color="#8ab0cc", size=10),
        xaxis=dict(gridcolor="#141e30", ticksuffix="%"),
        yaxis=dict(gridcolor="#141e30"),
        height=max(300, len(sorted_m) * 38 + 80),
        margin=dict(l=10, r=80, t=10, b=10),
    )
    st.plotly_chart(fig_b, use_container_width=True)

# ── TAB 4: 데이터 테이블 ────────────────────
with tab4:
    st.markdown('<div class="section-title">핵심 지표 요약</div>', unsafe_allow_html=True)
    metrics_df_show = calc_metrics(raw_df).reset_index()

    def color_ret(val):
        if isinstance(val, (int, float)):
            return "color: #4dd0a0" if val >= 0 else "color: #f06292"
        return ""

    styled = metrics_df_show.style\
        .applymap(color_ret, subset=["총수익률(%)", "샤프지수", "최대낙폭(%)"])\
        .set_properties(**{"background-color": "#111827", "color": "#cfd8dc", "border-color": "#1e2d4a"})\
        .format({"총수익률(%)": "{:+.2f}%", "연간변동성(%)": "{:.2f}%", "샤프지수": "{:.2f}", "최대낙폭(%)": "{:.2f}%"})

    st.dataframe(styled, use_container_width=True, height=400)

    st.markdown('<div class="section-title">일별 종가 원본 데이터</div>', unsafe_allow_html=True)
    st.dataframe(
        raw_df.style.set_properties(**{"background-color": "#111827", "color": "#cfd8dc"}),
        use_container_width=True, height=400,
    )

    csv = raw_df.reset_index().to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥  CSV 다운로드",
        data=csv,
        file_name=f"stock_data_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

# ─────────────────────────────────────────────
# 푸터
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#2a3a5a;font-size:0.75rem;font-family:IBM Plex Mono;">'
    '데이터 출처: Yahoo Finance (yfinance) &nbsp;|&nbsp; 본 대시보드는 투자 권유가 아닙니다.'
    '</p>',
    unsafe_allow_html=True,
)
