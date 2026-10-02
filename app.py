import streamlit as st
import pandas as pd
import json
import os

# 予約データを保存するファイル名
DATA_FILE = "reservations.json"

# データ読み込み関数
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# データ保存関数
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# タイトル表示
st.title("🎸 延岡工業高校 軽音楽同好会")
st.subheader("音楽室 練習予約システム")

# 予約データの読み込み
reservations = load_data()

# --- 予約フォーム ---
st.markdown("---")
st.header("📝 新規予約")

with st.form("booking_form", clear_on_submit=True):
    date = st.date_input("予約日")
    time_slot = st.selectbox(
        "時間枠",
        [
            "昼休み (12:45~13:15)",
            "放課後① (16:00~17:00)",
            "放課後② (17:00~18:00)",
            "放課後③ (18:00~19:00)"
        ]
    )
    band_name = st.text_input("バンド名（代表者名）", placeholder="例: ザ・ノベオカズ（3年 松﨑）")
    
    submitted = st.form_submit_button("予約を確定する")

if submitted:
    if not band_name.strip():
        st.error("⚠️ バンド名を入力してください。")
    else:
        date_str = str(date)
        # 同じ日・同じ時間枠の重複チェック
        is_duplicate = any(r["date"] == date_str and r["time_slot"] == time_slot for r in reservations)
        
        if is_duplicate:
            st.error("⚠️ 指定された時間枠はすでに予約されています。別の枠を選んでください。")
        else:
            reservations.append({
                "date": date_str,
                "time_slot": time_slot,
                "band_name": band_name
            })
            save_data(reservations)
            st.success("✅ 予約が完了しました！")
            st.rerun()

# --- 予約一覧表示 ---
st.markdown("---")
st.header("📅 現在の予約状況")

if reservations:
    df = pd.DataFrame(reservations)
    df.columns = ["日付", "時間枠", "バンド名"]
    # 日付順に並び替え
    df = df.sort_values(by="日付")
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("現在、予約はありません。")