import os
import pandas as pd
import requests, zipfile, io
from datetime import datetime, timedelta
os.makedirs("yuho", exist_ok=True)

# ===============================
# 設定
# ===============================
API_KEY = os.getenv("EDINET_API_KEY")  # ←自分のAPIキーを入れてください
BASE_URL = "https://api.edinet-fsa.go.jp/api/v2"
OUTPUT_DIR = r"yuho"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===== 対象様式コード（有報/半期/四半期） =====
YUHO_ORD_FORM = {
    ("010", "030000"), # 有価証券報告書
    ("010", "100000"), # 半期報告書
}

def is_target_report(doc: dict, edinet_codes: set) -> bool:
    """EDINETコード＋様式コードで対象書類か判定"""
    ord_code = str(doc.get("ordinanceCode") or "").zfill(3)
    form_code = str(doc.get("formCode") or "").zfill(6)
    edinet_code = doc.get("edinetCode")
    return edinet_code in edinet_codes and (ord_code, form_code) in YUHO_ORD_FORM

def get_documents_list(date_str):
    """日付を指定して提出書類一覧を取得"""
    url = f"{BASE_URL}/documents.json"
    params = {"date": date_str, "type": 2, "Subscription-Key": API_KEY}
    res = requests.get(url, params=params, timeout=30)
    if res.status_code != 200:
        print(f"❌ 書類一覧取得失敗: {date_str}, HTTP {res.status_code}")
        return []
    return res.json().get("results", [])

def download_xbrl(doc_id):
    """docID を指定してZIPを保存＆解凍"""
    try:
        url = f"{BASE_URL}/documents/{doc_id}"
        params = {"type": 1, "Subscription-Key": API_KEY}
        res = requests.get(url, params=params, timeout=60)
        res.raise_for_status()

        save_path = os.path.join(OUTPUT_DIR, f"{doc_id}.zip")
        with open(save_path, "wb") as f:
            f.write(res.content)

        with zipfile.ZipFile(io.BytesIO(res.content)) as z:
            z.extractall(os.path.join(OUTPUT_DIR, doc_id))

        print(f"✅ {doc_id}.zip 保存＆解凍完了")
    except Exception as e:
        print(f"❌ {doc_id} ダウンロード失敗: {e}")

def main():
    # 1. アクティビスト銘柄一覧（証券コードに末尾0を追加して5桁化）
    activist_df = pd.read_excel(r"docs/アクティビスト銘柄一覧.xlsx")
    target_sec_codes = set(str(c).zfill(4) + "0" for c in activist_df["証券コード"].dropna().unique())

    # 2. EdinetcodeDlInfo.csv を読み込む（先頭1行スキップ）
    code_df = pd.read_csv(
        r"siryou\EdinetcodeDlInfo.csv",
        encoding="cp932",
        skiprows=1
    )

    # 3. 列名で指定（CSV側はすでに5桁）
    edinet_col = code_df["ＥＤＩＮＥＴコード"]
    sec_col = code_df["証券コード"].astype(str).str.strip()

    # 4. マッチング
    edinet_codes = set(edinet_col[sec_col.isin(target_sec_codes)].tolist())
    print(f"🎯 対象EDINETコード: {len(edinet_codes)}件")

    # 5. 直近1年間の提出書類を探索
    today = datetime.now().date()
    days = 365
    for i in range(days):
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        docs = get_documents_list(date_str)
        for doc in docs:
            if is_target_report(doc, edinet_codes):
                doc_id = doc["docID"]
                desc = doc.get("docDescription") or ""
                print(f"📌 Hit: {doc_id}, {desc}")
                download_xbrl(doc_id)

if __name__ == "__main__":
    main()