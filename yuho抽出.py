import os, pandas as pd

def main():
    df = pd.read_excel(os.path.join("docs", "アクティビスト銘柄一覧.xlsx"))
    print("✅ Yuho抽出用の証券コードリスト読み込み完了")
    # 実装省略（本来はEDINETから有報ZipをDL）
    # ダミーファイル出力
    os.makedirs("yuho", exist_ok=True)
    open(os.path.join("yuho", "dummy.txt"), "w").write("yuho data")

if __name__ == "__main__":
    main()
