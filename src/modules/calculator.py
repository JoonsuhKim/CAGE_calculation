import pandas as pd

# CAGE 계산기
def calculate_cage(row, kor_mpc, kor_gdp_total, kor_size, usa_dist):
    result = 0
    result += (((row['market_size'] * 1e9 / row['population']) / kor_mpc) - 1) * 70
    result += (((row['GDP_capita'] * row['population']) / kor_gdp_total) - 1) * 80
    result += ((row['physical_dist'] / usa_dist) - 1) * (-110)
    result += ((row['true_size'] / kor_size) - 1) * (-20)
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
