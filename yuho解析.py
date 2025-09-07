import os, pandas as pd

def main():
    # 適当な処理を追加、本番ではXBRL解析を実装
    df = pd.DataFrame([{"会社名": "テスト株式会社", "証券コード": "1234", "時価総額": 1000000000}])
    os.makedirs("docs", exist_ok=True)
    save_path = os.path.join("docs", "アクティビスト銘柄_資産判定.xlsx")
    df.to_excel(save_path, index=False)
    print(f"✅ 完了: {save_path}")

if __name__ == "__main__":
    main()
