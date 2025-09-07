import requests
import os
from datetime import datetime, timedelta

# ===============================
# 設定
# ===============================
API_KEY = "b3179bcab14b4053a5928dce030612f3"  # ← ローカルと同じく直書き
BASE_URL = "https://api.edinet-fsa.go.jp/api/v2"
OUTPUT_DIR = "xbrl_reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 取得日数を設定（例: 365 = 1年分）
DAYS = 365  

def get_documents_list(date_str):
    """日付を指定して提出書類一覧を取得"""
    url = f"{BASE_URL}/documents.json"
    params = {"date": date_str, "type": 2, "Subscription-Key": API_KEY}
    res = requests.get(url, params=params, timeout=30)
    if res.status_code != 200:
        print(f"❌ {date_str} のリスト取得失敗: {res.status_code}")
        return []
    return res.json().get("results", [])

def download_xbrl(doc_id):
    """docID を指定してZIPを保存"""
    url = f"{BASE_URL}/documents/{doc_id}"
    params = {"type": 5, "Subscription-Key": API_KEY}
    res = requests.get(url, params=params, timeout=60)
    if res.status_code == 200:
        save_path = os.path.join(OUTPUT_DIR, f"{doc_id}.zip")
        with open(save_path, "wb") as f:
            f.write(res.content)
        print(f"✅ {doc_id}.zip 保存完了")
        return save_path
    else:
        print(f"❌ {doc_id} のzip取得失敗: {res.status_code}")

def main():
    today = datetime.now().date()
    for i in range(DAYS):  # 👈 直近1年分を処理
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        print(f"📅 {date_str} を処理中...")
        docs = get_documents_list(date_str)
        for doc in docs:
            if "大量保有報告書" in (doc.get("docDescription") or ""):
                download_xbrl(doc["docID"])

if __name__ == "__main__":
    main()
