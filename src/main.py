import os
import signal
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from modules import BubbleNode, calculate_cage, plot_bubble_chart

# Streamlit UI: 연도 + 산업 선택
st.title("World Wide Industry Consumption Bubble Chart")
year = st.selectbox("Select Year", ['2023', '2022', '2021', '2020', '2019'], key='year_select')
industry = st.selectbox("Select Industry", ['electronics', 'apparel', 'automotive'], key='industry_select')

# 경로 설정
base_path = f"data/{year}"
industry_path = f"{base_path}/{industry}.csv"
general_path = f"{base_path}/general.csv"
general_info_path = "data/General_info.csv"

# 파일 존재 확인
missing_files = [p for p in [industry_path, general_path, general_info_path] if not os.path.exists(p)]
if missing_files:
    st.write("No Data Found for the selected combination.")
    st.stop()

# 데이터 로딩
industry_df = pd.read_csv(industry_path)
general_df = pd.read_csv(general_path)
general_info_df = pd.read_csv(general_info_path)

# 데이터 전처리
for col in ['output', 'value_added']:
    if industry_df[col].dtype == 'object':
        industry_df[col] = industry_df[col].replace(',', '', regex=True).astype(float)

# 병합 및 변수계산
merged = pd.merge(industry_df, general_df, on='country_code', how='inner')
merged = pd.merge(merged, general_info_df, on='country_code', how='left')

merged['x_axis'] = merged['GDP_capita']
merged['y_axis'] = merged['market_size'] * 1e9 / merged['population']
merged['CLS'] = merged['market_size']

kor_row = merged[merged['country_code'] == 'KOR'].iloc[0]
usa_row = merged[merged['country_code'] == 'USA'].iloc[0]

KOR_market_per_capita = kor_row['market_size'] * 1e9 / kor_row['population']
KOR_gdp_total = kor_row['GDP_capita'] * kor_row['population']
KOR_true_size = kor_row['true_size']
USA_physical_dist = usa_row['physical_dist']

# 링크드리스트 구성
head = None
prev = None
for _, row in merged.iterrows():
    cage_score = calculate_cage(row, KOR_market_per_capita, KOR_gdp_total, KOR_true_size, USA_physical_dist)
    node = BubbleNode(row['country_code'], row['x_axis'], row['y_axis'], row['CLS'], cage_score/10)
    if prev:
        prev.next = node
    else:
        head = node
    prev = node

# 시각화
mode = st.selectbox("Parameter Index", ['CLS', 'CAGE'], key="mode_select")
color = 'skyblue' if mode == 'CLS' else 'orange'
fig = plot_bubble_chart(head, size_attr=mode, title=f"Market Attractiveness of {industry.capitalize()} by {mode}", color=color, industry=industry)
st.pyplot(fig)

# 종료 버튼
if st.button("Exit", key="exit_button"):
    st.warning("Process Terminated...")
    os.kill(os.getpid(), signal.SIGINT)