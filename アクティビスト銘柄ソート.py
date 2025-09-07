import pandas as pd, os

file_path = os.path.join("xbrl_reports", "大量保有報告書_解析結果.xlsx")
data = pd.read_excel(file_path)

activist_funds = ["村上", "レノ", "C&I", "オアシス", "バリューアクト", "エリオット"]
activist_data = data[data["提出者名"].str.contains("|".join(activist_funds), na=False)]
activist_data = activist_data.sort_values(by="報告義務発生日", ascending=False)

os.makedirs("docs", exist_ok=True)
activist_data.to_excel(os.path.join("docs", "アクティビスト銘柄一覧.xlsx"), index=False)
