import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="アクティビスト銘柄", layout="wide")
st.title("📊 アクティビスト銘柄 資産判定（最新）")

# GitHub Pages 上の Excel ファイル（日本語名をエンコードしてアクセス）
file_name = "アクティビスト銘柄_資産判定.xlsx"
url_base = "https://harubon1027-pixel.github.io/activist-results/"
URL = url_base + urllib.parse.quote(file_name)

st.write(f"データ取得先: {URL}")

try:
    df = pd.read_excel(URL)
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"データ取得に失敗しました: {e}")
