import pandas as pd
import os
os.makedirs("docs", exist_ok=True)

# ファイル読み込み
file_path = "docs/大量保有報告書_解析結果.xlsx"
data = pd.read_excel(file_path, sheet_name="Sheet1")

# 主なアクティビストのリスト
activist_funds = [
    "アセット・バリュー・インベスターズ",
    "エフィッシモ キャピタル マネージメント",
    "シティインデックスイレブンス",
    "エリオット・インベストメント・マネージメント・エルピー",
    "Ｏａｓｉｓ　Ｍａｎａｇｅｍｅｎｔ　Ｃｏｍｐａｎｙ　Ｌｔｄ．",
    "シルチェスター・インターナショナル",
    "ストラテジックキャピタル",
    "3Dインベストメント",
    "ダルトン",
    "Nippon Active Value Fund",
    "日本バリューインベスターズ",
    "バリューアクト",
    "村上グループ",
    "リム・アドバイザーズ"
    "村上",
    "レノ", 
    "C&I", 
    "エスグラント",
    "野村絢",
    "センジン",
    "ＳＥＮＪＩＮ",
]

# 提出者名にアクティビストが含まれるものを抽出
activist_data = data[data["提出者名"].str.contains("|".join(activist_funds), na=False)]

# 結果を確認
print(activist_data)

# 必要ならソート（例：報告義務発生日で新しい順）
activist_data = activist_data.sort_values(by="報告義務発生日", ascending=False)

# ExcelやCSVに保存する場合
# ここを変更すれば出力先を変えられる
activist_data.to_excel(r"docs/アクティビスト銘柄一覧.xlsx", index=False)
