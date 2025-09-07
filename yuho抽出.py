import os, pandas as pd, requests, zipfile, io
from datetime import datetime, timedelta

API_KEY = os.getenv("EDINET_API_KEY")
BASE_URL = "https://api.edinet-fsa.go.jp/api/v2"
OUTPUT_DIR = os.path.join(os.getcwd(), "yuho")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_xbrl(doc_id):
    url = f"{BASE_URL}/documents/{doc_id}"
    params = {"type": 1, "Subscription-Key": API_KEY}
    res = requests.get(url, params=params, timeout=60)
    if res.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(res.content)) as z:
            z.extractall(os.path.join(OUTPUT_DIR, doc_id))
        print(f"✅ {doc_id} 保存完了")

def main():
    activist_df = pd.read_excel(os.path.join("docs", "アクティビスト銘柄一覧.xlsx"))
    target_codes = set(str(c).zfill(5) for c in activist_df["証券コード"].dropna())
    today = datetime.now().date()
    for i in range(30):  # 過去30日分
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"{BASE_URL}/documents.json"
        res = requests.get(url, params={"date": date_str, "type": 2, "Subscription-Key": API_KEY})
        for doc in res.json().get("results", []):
            if doc.get("ordinanceCode") == "010" and doc.get("edinetCode") in target_codes:
                download_xbrl(doc["docID"])

if __name__ == "__main__":
    main()
