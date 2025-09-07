import pandas as pd, os

file_path = os.path.join("docs", "大量保有報告書_解析結果.xlsx")
data = pd.read_excel(file_path)

activist_funds = ["村上", "レノ", "C&I", "オアシス", "バリューアクト", "エリオット"]
activist_data = data[data["提出者名"].str.contains("|".join(activist_funds), na=False)]
activist_data = activist_data.sort_values(by="証券コード", ascending=True)

os.makedirs("docs", exist_ok=True)
save_path = os.path.join("docs", "アクティビスト銘柄一覧.xlsx")
activist_data.to_excel(save_path, index=False)
print(f"✅ 保存完了: {save_path}")
