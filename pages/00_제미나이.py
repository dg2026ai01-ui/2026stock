# 1. 종목 선택 (티커 설정) - 문자열 오타 확인!
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

# 안전하게 기본값을 설정하는 법 (에러 방지)
all_options = list(ticker_dict.keys())
initial_selections = [name for name in ["KOSPI 지수", "S&P 500", "삼성전자", "엔비디아"] if name in all_options]

selected_names = st.sidebar.multiselect(
    "비교할 종목을 선택하세요", 
    options=all_options, 
    default=initial_selections # 존재하지 않는 값은 자동으로 걸러짐
)
