import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="PFC SYSTEM ver04", layout="wide")

# --- 定数定義 ---

# 【NEW】単品データベース (1単位あたりのPFC)
SINGLE_FOOD_DB = {
    "白米 (100g)": {"kcal": 156.0, "p": 2.5, "f": 0.3},
    "納豆 (1パック50g)": {"kcal": 90.0, "p": 7.4, "f": 5.0},
    "卵 (Mサイズ1個)": {"kcal": 76.0, "p": 6.2, "f": 5.2},
    "皮付き鶏もも肉 (100g)": {"kcal": 200.0, "p": 16.2, "f": 14.0},
    "鶏むね肉 皮なし (100g)": {"kcal": 108.0, "p": 22.3, "f": 1.5},
    "銀鮭 (1切 80g)": {"kcal": 109.0, "p": 17.8, "f": 4.0},
    "絹豆腐 (150g)": {"kcal": 77.0, "p": 7.2, "f": 3.8},
    "木綿豆腐 (150g)": {"kcal": 110.0, "p": 10.0, "f": 7.4},
    "カレー職人チキン (1人前)": {"kcal": 101.0, "p": 3.7, "f": 4.1},
    "丸美屋麻婆豆腐 (1人前)": {"kcal": 62.0, "p": 2.7, "f": 2.8},
    "ブロッコリー (100g)": {"kcal": 33.0, "p": 4.3, "f": 0.5},
    "トマト缶 (100g)": {"kcal": 30.0, "p": 1.3, "f": 0.1},
    "ソイプロテイン (1杯分)": {"kcal": 106.3, "p": 21.0, "f": 0.6},
    "ホエイプロテイン (1杯分)": {"kcal": 136, "p": 21.2, "f": 1.5},
    "ツナ缶 水煮 (1缶)": {"kcal": 53.0, "p": 11.6, "f": 0.7},
    "かつお缶フレーク (1缶)": {"kcal": 193.0, "p": 10.5, "f": 16.7}
}

FOOD_DB = {
    "朝食": {
        "ソイプロテイン (Verifist)": {"kcal": 106.3, "p": 21.0, "f": 0.6},
        "納豆定食 (米300g+納豆1+汁)": {"kcal": 608.0, "p": 17.9, "f": 7.4},
        "卵かけご飯 (米300g+卵1)": {"kcal": 560.0, "p": 13.5, "f": 7.5},
        "カスタム作成": None, # 単品組み合わせ用に追加
        "手動入力": None
    },
    "昼食": {
        "カレー職人チキン (米300g)": {"kcal": 571.0, "p": 11.2, "f": 5.3},
        "納豆カレー職人 (米300g+納豆2)": {"kcal": 751.0, "p": 26.0, "f": 14.3},
        "カスタム作成": None,
        "手動入力": None
    },
    "夕食": {
        "丸美屋麻婆豆腐定食 (米300g+豆腐450g)": {"kcal": 900.0, "p": 42.0, "f": 32.0},
        "銀鮭定食 (米300g+鮭1+納豆1)": {"kcal": 818.0, "p": 41.3, "f": 16.3},
        "鶏肉焼き定食": {"kcal": 750.0, "p": 45.0, "f": 12.0},
        "鶏肉のトマト煮定食": {"kcal": 680.0, "p": 40.0, "f": 10.0},
        "カスタム作成": None,
        "手動入力": None
    },
    "トレ後": {
        "ホエイプロテイン (ウマテイン)": {"kcal": 136.0, "p": 21.2, "f": 1.5},
        "なし": {"kcal": 0.0, "p": 0.0, "f": 0.0},
        "カスタム作成": None,
        "手動入力": None
    }
}

# 特殊メニュー（時間ベースのMETs計算用）
SPECIAL_TRAINING_DB = {
    "山澤腹筋 (4分スーパーセット)": {"base_mets": 8.0, "duration_min": 4},
    "山澤腕トレ (5分ダンベル)": {"base_mets": 5.0, "duration_min": 5},
    "山澤肩トレ (7分ダンベル)": {"base_mets": 6.0, "duration_min": 7}
}

TRAINING_DB = {
    "ブルガリアンスクワット (高強度)": 0.04,
    "ダンベル・スクイーズ・プレス": 0.03,
    "ベンチプレス": 0.03,
    "デッドリフト": 0.05,
    "懸垂": 0.04
}

# --- サイドバー設定 ---
st.sidebar.header("USER PROFILE")
gender = st.sidebar.radio("生物学的性別", ["男性", "女性"], index=0)
weight = st.sidebar.number_input("現在の体重 (kg)", value=73.3, step=0.1)
height = st.sidebar.number_input("身長 (cm)", value=177.7, step=0.1)
age = st.sidebar.number_input("年齢", value=23, step=1)
steps = st.sidebar.number_input("本日の歩数", value=5000, step=500)
study_hours = st.sidebar.number_input("研究・勉強時間 (h)", value=8.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.header("AIM")
target_kcal = st.sidebar.number_input("目標カロリー (kcal)", value=2100)
target_p = st.sidebar.number_input("目標タンパク質 (g)", value=120)

# 基礎計算
if gender == "男性":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161
step_kcal = weight * steps * 0.0005
study_kcal = weight * study_hours * 0.5 * 1.05

# --- メイン：食事入力 ---
st.title("ANALYSIS of PFC")

def get_meal_stats(category):
    st.subheader(f"🍴 {category}")
    selection = st.selectbox(f"{category}メニューを選択", list(FOOD_DB[category].keys()), key=f"sel_{category}")
    
    # プリセット選択時
    if selection not in ["カスタム作成", "手動入力"]:
        preset = FOOD_DB[category][selection]
        st.info(f"NUTRITION： {preset['kcal']} kcal | P: {preset['p']}g | F: {preset['f']}g")
        return preset["kcal"], preset["p"], preset["f"]
        
    # 【NEW】カスタム作成（単品組み合わせ）選択時
    elif selection == "カスタム作成":
        st.markdown("**:blue[▼ 食材を組み合わせて計算]**")
        selected_items = st.multiselect("食材を追加", list(SINGLE_FOOD_DB.keys()), key=f"multi_{category}")
        
        k, p, f = 0.0, 0.0, 0.0
        
        if selected_items:
            for item in selected_items:
                col1, col2 = st.columns([3, 1])
                # 食材名を表示
                col1.write(f"・{item}")
                # 数量（倍率）を入力。例：米200gなら「2.0」、納豆2パックなら「2.0」
                qty = col2.number_input("数量 (倍)", min_value=0.0, value=1.0, step=0.5, key=f"qty_{category}_{item}")
                
                k += SINGLE_FOOD_DB[item]["kcal"] * qty
                p += SINGLE_FOOD_DB[item]["p"] * qty
                f += SINGLE_FOOD_DB[item]["f"] * qty
            
            st.success(f"【合計】 {k:.1f} kcal | P: {p:.1f}g | F: {f:.1f}g")
        return k, p, f
        
    # 手動入力時
    else:
        c1, c2, c3 = st.columns(3)
        k = c1.number_input("kcal", min_value=0.0, key=f"{category}_k")
        p = c2.number_input("P(g)", min_value=0.0, key=f"{category}_p")
        f = c3.number_input("F(g)", min_value=0.0, key=f"{category}_f")
        return k, p, f

b_k, b_p, b_f = get_meal_stats("朝食")
l_k, l_p, l_f = get_meal_stats("昼食")
d_k, d_p, d_f = get_meal_stats("夕食")
s_k, s_p, s_f = get_meal_stats("トレ後")

st.markdown("---")
st.header("ACTIVITY")

special_menu = st.multiselect("山澤メニュー", list(SPECIAL_TRAINING_DB.keys()))
special_kcal = 0
for sm in special_menu:
    st.write(f"**{sm}**")
    col1, col2 = st.columns(2)
    sets = col1.number_input(f"セット数", min_value=1, value=1, key=f"sets_{sm}")
    
    if "腹筋" in sm:
        st.caption("上体おこし/クランチ/プランクジャック/レッグレイズ/ツイスト...等(各20s/休10s)")
        sm_kcal = (SPECIAL_TRAINING_DB[sm]["base_mets"] * weight * (SPECIAL_TRAINING_DB[sm]["duration_min"]/60) * 1.05) * sets
    else:
        db_weight = col2.number_input(f"ダンベル重量(kg)", value=5.0, step=1.0, key=f"db_{sm}")
        intensity_factor = db_weight / 5.0 
        sm_kcal = (SPECIAL_TRAINING_DB[sm]["base_mets"] * intensity_factor * weight * (SPECIAL_TRAINING_DB[sm]["duration_min"]/60) * 1.05) * sets
    
    st.metric("推定燃焼", f"{sm_kcal:.1f} kcal")
    special_kcal += sm_kcal

selected_trainings = st.multiselect("通常種目メニュー", list(TRAINING_DB.keys()) + ["その他"])
normal_kcal = 0
for t in selected_trainings:
    col1, col2, col3, col4 = st.columns(4)
    w = col1.number_input(f"重量(kg) [{t}]", value=0.0, key=f"w_{t}")
    r = col2.number_input(f"レップ数 [{t}]", value=10, key=f"r_{t}")
    s = col3.number_input(f"セット数 [{t}]", value=3, key=f"s_{t}")
    factor = TRAINING_DB.get(t, 0.03)
    burn = w * r * s * factor
    col4.metric("燃焼", f"{burn:.1f} kcal")
    normal_kcal += burn

# --- 最終計算 ---
total_intake = b_k + l_k + d_k + s_k
total_p = b_p + l_p + d_p + s_p
total_f = b_f + l_f + d_f + s_f
tef_kcal = total_intake * 0.1
total_burn = bmr + step_kcal + study_kcal + special_kcal + normal_kcal + tef_kcal
net_calories = total_intake - total_burn

# --- リザルト表示 ---
st.markdown("---")
st.header("📊TOTAL RESULT")
r1, r2, r3 = st.columns(3)
r1.metric("総摂取", f"{total_intake:.1f} kcal", f"目標比 {total_intake - target_kcal:.1f}", delta_color="inverse")
r2.metric("総タンパク質", f"{total_p:.1f} g", f"目標比 {total_p - target_p:.1f} g")
r3.metric("正味総消費", f"{total_burn:.0f} kcal", f"純粋収支 {net_calories:.0f}")

if net_calories < 0:
    st.success(f"MODE脂肪燃焼: {-net_calories:.0f} kcalのマイナスです。脂肪の燃焼が期待できます。")
else:
    st.warning(f"MODE増量:{net_calories:.0f} kcalのプラスです。バルクアップが進行中。")
