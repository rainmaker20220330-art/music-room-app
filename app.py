import streamlit as st
import pandas as pd
import requests
import re
from dateutil import parser

# ★ご自身のGASウェブアプリのURLを貼り付けてください
GAS_URL = "https://script.google.com/macros/s/AKfycbzdkNSII2kmRSrhFoekyrL-_zuc7Ed8DhnrTqpJvCDN3TNSWMIwHukAeGuxPgrNkp6L/exec"

# スプレッドシートからデータ取得＆どんな表記の日付も「YYYY-MM-DD」に確定変換する
def load_data():
    try:
        response = requests.get(GAS_URL)
        if response.status_code == 200:
            data = response.json()
            cleaned_data = []
            
            for r in data:
                date_val = r.get("date")
                if not date_val:
                    continue
                
                # 1. カッコとその中身（例: (Japan Standard Time)）を除去
                val_str = str(date_val).strip()
                cleaned_str = re.sub(r'\(.*?\)', '', val_str).strip()
                
                # 2. どんな形式（英語/斜線区切りなど）でも YYYY-MM-DD に強制変換
                try:
                    dt = parser.parse(cleaned_str)
                    formatted_date = dt.strftime("%Y-%m-%d")
                except:
                    formatted_date = cleaned_str

                cleaned_data.append({
                    "date": formatted_date,
                    "time_slot": str(r.get("time_slot", "")).strip(),
                    "band_name": str(r.get("band_name", "")).strip()
                })
            return cleaned_data
        else:
            return []
    except Exception as e:
        st.error("データの読み込みに失敗しました。")
        return []

# スプレッドシートへ保存
def save_data(new_reservation):
    try:
        response = requests.post(GAS_URL, json=new_reservation)
        return response.status_code == 200
    except Exception as e:
        st.error("データの保存に失敗しました。")
        return False

st.title("🎸 延岡工業高校 軽音楽同好会")
st.subheader("音楽室 練習予約システム")

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
        # 重複チェック（統一された YYYY-MM-DD の形式で比較）
        is_duplicate = any(r["date"] == date_str and r["time_slot"] == time_slot for r in reservations)
        
        if is_duplicate:
            st.error("⚠️ 指定された時間枠はすでに予約されています。別の枠を選んでください。")
        else:
            new_data = {
                "date": date_str,
                "time_slot": time_slot,
                "band_name": band_name
            }
            if save_data(new_data):
                st.success("✅ 予約が完了しました！")
                st.rerun()
            else:
                st.error("❌ 予約の保存に失敗しました。もう一度お試しください。")

# --- 予約状況表示 ---
st.markdown("---")
st.header("📅 現在の予約状況")

if reservations:
    df = pd.DataFrame(reservations)
    if not df.empty and "date" in df.columns:
        df = df[["date", "time_slot", "band_name"]]
        df.columns = ["日付", "時間枠", "バンド名"]
        df = df.sort_values(by="日付")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("現在、予約はありません。")
else:
    st.info("現在、予約はありません。")