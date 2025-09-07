import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="アクティビスト銘柄", layout="wide")
st.title("📊 アクティビスト銘柄 資産判定（最新・報告義務発生日順）")

# GitHub Pages 上の Excel ファイル（日本語名をエンコードしてアクセス）
file_name = "アクティビスト銘柄_資産判定.xlsx"
url_base = "https://harubon1027-pixel.github.io/activist-results/"
URL = url_base + urllib.parse.quote(file_name)

st.write(f"データ取得先: {URL}")

try:
    df = pd.read_excel(URL)

    # 🔹 報告義務発生日を日付型に変換
    if "報告義務発生日" in df.columns:
        df["報告義務発生日"] = pd.to_datetime(df["報告義務発生日"], errors="coerce")

        # 🔹 降順に並べ替え（最新の日付が先頭）
        df = df.sort_values("報告義務発生日", ascending=False)

    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"データ取得に失敗しました: {e}")
