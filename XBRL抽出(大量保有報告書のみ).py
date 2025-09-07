import requests, os, zipfile
from datetime import datetime, timedelta

API_KEY = os.getenv("EDINET_API_KEY")  # Secretsから取得
BASE_URL = "https://api.edinet-fsa.go.jp/api/v2"
OUTPUT_DIR = os.path.join("xbrl_reports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_documents_list(date_str):
    url = f"{BASE_URL}/documents.json"
    params = {"date": date_str, "type": 2, "Subscription-Key": API_KEY}
    res = requests.get(url, params=params, timeout=30)
    return res.json().get("results", []) if res.status_code == 200 else []

def download_xbrl(doc_id):
    url = f"{BASE_URL}/documents/{doc_id}"
    params = {"type": 5, "Subscription-Key": API_KEY}
    res = requests.get(url, params=params, timeout=60)
    if res.status_code == 200:
        save_path = os.path.join(OUTPUT_DIR, f"{doc_id}.zip")
        with open(save_path, "wb") as f:
            f.write(res.content)
        print(f"✅ {doc_id}.zip 保存完了")
        return save_path

def main():
    today = datetime.now().date()
    for i in range(3):  # 最新3日分だけテスト（慣れたら期間延長可）
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        docs = get_documents_list(date_str)
        for doc in docs:
            if doc.get("formCode") == "010000" and "大量保有報告書" in doc.get("docDescription", ""):
                download_xbrl(doc["docID"])

if __name__ == "__main__":
    main()
