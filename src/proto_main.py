import os
import signal
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# cd desktop/2025/CAGE_calculation
# source venv/bin/activate
# /Users/joonsuh01/Desktop/2025/CAGE_calculation/venv/bin/python /Users/joonsuh01/Desktop/2025/CAGE_calculation/src/main.py
# streamlit run src/main.py

# 0. 링크드리스트 노드 정의 (CLS, CAGE 포함)
class BubbleNode: # 클래스를 정의
    # __init__은 생성자 메서드로, 이 클래스를 기반으로 객체를 만들 때 자동으로 실행되는 함수
    def __init__(self, ISO, x_axis, y_axis, CLS, CAGE=None): 
        self.ISO = ISO            # 국가 코드
        self.x_axis = x_axis      # per capita GDP
        self.y_axis = y_axis      # per capita apparel consumption
        self.CLS = CLS            # market size (CLS)
        self.CAGE = CAGE          # CAGE score (계산 예정)
        self.next = None          # 다음 노드 포인터

# Streamlit UI: 연도 + 산업 선택
st.title("World Wide Industry Consumption Bubble Chart")

# 연도 선택
year = st.selectbox("Select Year", ['2023', '2022', '2021', '2020', '2019'], key='year_select')
industry = st.selectbox("Select Industry", ['electronics', 'apparel', 'automotive'], key='industry_select')

# 경로 정의 (선택된 연도 & 산업 기반)
base_path = f"data/{year}"
industry_path = f"{base_path}/{industry}.csv"        # 예: data/2022/apparel.csv 또는 data/2021/automotive.csv
general_path = f"{base_path}/general.csv"
general_info_path = "data/General_info.csv"

# 파일 존재 여부 검사
missing_files = []
for path in [industry_path, general_path, general_info_path]:
    if not os.path.exists(path):
        missing_files.append(path)

# 조건에 따라 분기 처리 및 데이터 로딩
if missing_files:
    st.write("No Data Found for the selected combination.")
    st.stop()  # 여기서 프로세스 완전 중단 (아래 실행 X)
else:
    # 정상 데이터 로딩
    industry_df = pd.read_csv(industry_path)
    general_df = pd.read_csv(general_path)
    general_info_df = pd.read_csv(general_info_path)

for col in ['output', 'value_added']:
    if industry_df[col].dtype == 'object':
        industry_df[col] = industry_df[col].replace(',', '', regex=True).astype(float)

# 3. 데이터 병합
merged = pd.merge(industry_df, general_df, on='country_code', how='inner')
merged = pd.merge(merged, general_info_df, on='country_code', how='left')

# 4. 변수 계산
merged['x_axis'] = merged['GDP_capita']
merged['y_axis'] = merged['market_size'] * 1e9 / merged['population']
merged['CLS'] = merged['market_size']

# 기준값: merged 테이블에서 KOR, USA 정보 추출
kor_row = merged[merged['country_code'] == 'KOR'].iloc[0]
usa_row = merged[merged['country_code'] == 'USA'].iloc[0]

# 기준 변수 계산
KOR_market_per_capita = kor_row['market_size'] * 1e9 / kor_row['population']
KOR_gdp_total = kor_row['GDP_capita'] * kor_row['population']
KOR_true_size = kor_row['true_size']
USA_physical_dist = usa_row['physical_dist']

# CAGE 점수 계산 함수
def calculate_cage(row):
    result = 0

    result += (((row['market_size'] * 1e9 / row['population']) / KOR_market_per_capita) - 1) * 70
    result += (((row['GDP_capita'] * row['population']) / KOR_gdp_total) - 1) * 80
    result += ((row['physical_dist'] / USA_physical_dist) - 1) * (-110)
    result += ((row['true_size'] / KOR_true_size) - 1) * (-20)
    result += row['access_ocean'] * 50
    result += row['border'] * 80
    result += row['language'] * 200
    result += row['trading_bloc'] * 330
    result += row['colony'] * 900
    result += row['colonizer'] * 190
    result += row['polity'] * 300
    result += row['currency'] * 340

    if row['output'] > 0 and not pd.isna(row['output']):
        result += (row['value_added'] / row['output']) * 200

    return result

# 5. 링크드리스트 생성
head = None
prev = None

for _, row in merged.iterrows():
    cage_score = calculate_cage(row)

    node = BubbleNode(
        ISO=row['country_code'],
        x_axis=row['x_axis'],
        y_axis=row['y_axis'],
        CLS=row['CLS'],
        CAGE=cage_score/10
    )

    if prev is not None:
        prev.next = node
    else:
        head = node

    prev = node

def plot_bubble_chart(head, size_attr='CLS', title='Bubble Chart', color='skyblue', industry = 'apparel'):
    cur = head
    x_vals, y_vals, sizes, labels = [], [], [], []

    while cur:
        if cur.ISO == 'KOR':
            cur = cur.next
            continue
        x_vals.append(cur.x_axis / 1000)
        y_vals.append(cur.y_axis)
        size_value = getattr(cur, size_attr)
        if pd.isna(size_value) or size_value <= 0:
            sizes.append(1)  # 최소 크기
        else:
            sizes.append(size_value * 75)
        labels.append(cur.ISO)
        cur = cur.next

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(x_vals, y_vals, s=sizes, alpha=0.7, color=color, edgecolors='black')

    for i in range(len(labels)):
        ax.text(x_vals[i], y_vals[i], labels[i], fontsize=max(8, sizes[i] / 500), ha='center', va='center')

    ylim_dict = {
        'automotive': 3000,
        'electronics': 800,
    }    

    ax.set_xlim(0, 100)
    ax.set_ylim(0, ylim_dict.get(industry, 1500))  # 기본값 1500
    ax.set_xlabel("per capita GDP ($K)", fontsize=12)
    ax.set_ylabel(f"per capita {industry} consumption ($)", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(False)
    plt.tight_layout()
    return fig

mode = st.selectbox("Parameter Index", ['CLS', 'CAGE'], key="mode_select")
color = 'skyblue' if mode == 'CLS' else 'orange'
fig = plot_bubble_chart(head, size_attr=mode, title=f"Market Attractiveness of {industry.capitalize()} by {mode}", color=color, industry=industry)
st.pyplot(fig)

if st.button("Exit", key="exit_button"):
    st.warning("Process Terminated...")
    pid = os.getpid()
    os.kill(pid, signal.SIGINT)