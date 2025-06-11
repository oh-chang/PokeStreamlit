import streamlit as st
import pandas as pd

# 데이터 로드
df = pd.read_csv("Pokemon_translated.csv")

# 공백 제거 및 컬럼명 정리
df.columns = df.columns.str.strip()

st.set_page_config(page_title="스탯 기반 포켓몬 추천기", layout="wide")
st.title("🧬 스탯 기반 포켓몬 추천기")

st.markdown("원하는 능력치와 조건을 설정하면, 해당 조건을 만족하는 포켓몬을 추천해드립니다.")

# --- 전설 여부 & 이름 검색 ---
col0, col1 = st.columns([1, 3])
with col0:
    only_legendary = st.checkbox("전설 포켓몬만 보기")
with col1:
    name_search = st.text_input("이름 검색 (한글 또는 영어)", "")

# --- 스탯 슬라이더 ---
col1, col2, col3 = st.columns(3)
with col1:
    min_hp = st.slider("최소 HP", 0, 255, 50)
    min_attack = st.slider("최소 Attack", 0, 190, 50)
with col2:
    min_defense = st.slider("최소 Defense", 0, 230, 50)
    min_spatk = st.slider("최소 Sp. Atk", 0, 194, 50)
with col3:
    min_spdef = st.slider("최소 Sp. Def", 0, 230, 50)
    min_speed = st.slider("최소 Speed", 0, 180, 50)

# 조건 딕셔너리
conditions = {
    "HP": min_hp,
    "Attack": min_attack,
    "Defense": min_defense,
    "Sp. Atk": min_spatk,
    "Sp. Def": min_spdef,
    "Speed": min_speed
}

# --- 필터링 ---
filtered = df.copy()

# 전설 포켓몬 필터
if only_legendary:
    filtered = filtered[filtered["Legendary"] == True]

# 이름 검색
if name_search.strip():
    name_search_lower = name_search.lower()
    filtered = filtered[
        filtered["Name"].str.lower().str.contains(name_search_lower) |
        filtered["Name_KOR"].str.contains(name_search)
    ]

# --- 조건 모두 만족한 포켓몬만 추출 (메인 추천 리스트) ---
fully_matched = filtered[
    (filtered["HP"] >= min_hp) &
    (filtered["Attack"] >= min_attack) &
    (filtered["Defense"] >= min_defense) &
    (filtered["Sp. Atk"] >= min_spatk) &
    (filtered["Sp. Def"] >= min_spdef) &
    (filtered["Speed"] >= min_speed)
]

st.markdown(f"### ✅ 조건을 **모두 만족**하는 포켓몬: {len(fully_matched)}마리")
st.dataframe(
    fully_matched[[
        "Name_KOR", "Name", "Type 1", "Type 2",
        "HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed", "Legendary","Total"
    ]].sort_values(by="Total", ascending=False).reset_index(drop=True)
)

# --- 조건 만족률 분석 ---
def calculate_match_score(row):
    satisfied = 0
    for stat, threshold in conditions.items():
        if row[stat] >= threshold:
            satisfied += 1
    return satisfied / len(conditions)

filtered["조건_만족률"] = filtered.apply(calculate_match_score, axis=1)

# 만족률 높은 순으로 정렬
top_match = (
    filtered.sort_values(by="조건_만족률", ascending=False)
    [["Name_KOR", "Name", "조건_만족률", "HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed", "Legendary"]]
    .reset_index(drop=True)
    .head(10)
)

st.markdown("### 🏆 조건 만족률 TOP 10 포켓몬")
st.dataframe(top_match.style.format({"조건_만족률": "{:.0%}"}))
