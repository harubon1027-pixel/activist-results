import requests
import os
from datetime import datetime, timedelta
os.makedirs("xbrl_reports", exist_ok=True)

API_KEY = os.getenv("EDINET_API_KEY")  # ←必ず置き換え
BASE_URL = "https://api.edinet-fsa.go.jp/api/v2"
OUTPUT_DIR = "xbrl_reports"

# 保存フォルダ作成
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_documents_list(date_str):
    """指定日付の提出書類一覧を取得"""
    url = f"{BASE_URL}/documents.json"
    params = {"date": date_str, "type": 2, "Subscription-Key": API_KEY}
    res = requests.get(url, params=params, timeout=30)

    if res.status_code != 200:
        print(f"❌ 書類一覧取得失敗: {date_str}, HTTP {res.status_code}")
        return []

    return res.json().get("results", [])

def download_xbrl(doc_id):
    """指定docIDのXBRL一式(zip)をダウンロード"""
    url = f"{BASE_URL}/documents/{doc_id}"
    params = {"type": 5, "Subscription-Key": API_KEY}
    res = requests.get(url, params=params, timeout=60)

    if res.status_code != 200:
        print(f"❌ XBRL取得失敗: {doc_id}, HTTP {res.status_code}")
        return None

    save_path = os.path.join(OUTPUT_DIR, f"{doc_id}.zip")
    with open(save_path, "wb") as f:
        f.write(res.content)
    print(f"✅ {doc_id}.zip 保存完了")
    return save_path

def main():
    # ✅ ここで期間を設定（例：2022/07/01～2025/02/01）
    start_date = datetime.strptime("2023/07/01", "%Y/%m/%d").date()
    end_date   = datetime.strptime("2024/12/01", "%Y/%m/%d").date()

    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        print(f"📅 {date_str} を処理中...")

        docs = get_documents_list(date_str)
        if docs:
            for doc in docs:
                doc_id = doc.get("docID")
                form_code = doc.get("formCode")
                desc = doc.get("docDescription") or ""

                if not doc_id or not form_code:
                    continue

                # 大量保有報告書のみ抽出
                if form_code in ["010000"] and "大量保有報告書" in desc and all(x not in desc for x in ["変更", "訂正", "内部統制"]):
                    print(f"📌 Hit: {doc_id}, {desc} (formCode={form_code})")
                    download_xbrl(doc_id)

        current += timedelta(days=1)

if __name__ == "__main__":
    main()