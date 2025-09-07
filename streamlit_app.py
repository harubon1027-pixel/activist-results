import streamlit as st
import pandas as pd

st.set_page_config(page_title="アクティビスト銘柄", layout="wide")
st.title("📊 アクティビスト銘柄 資産判定（最新）")

URL = "https://harubon1027-pixel.github.io/activist-results/アクティビスト銘柄_資産判定.xlsx"

try:
    df = pd.read_excel(URL)
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"データ取得に失敗しました: {e}")
