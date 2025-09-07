import os
import zipfile
import pandas as pd
import xml.etree.ElementTree as ET
import yfinance as yf
import os
os.makedirs("yuho", exist_ok=True)
os.makedirs("docs", exist_ok=True)

# === マッピング辞書（代表値を優先） ===
TAG_MAP = {
    "現金": [
        "CashAndDeposits",
        "CashAndCashEquivalents",
        "CashAndCashEquivalentsSummaryOfBusinessResults",
    ],
    "不動産": [
        "Land",
        "BuildingsAndStructuresNet",
        "PropertyPlantAndEquipment",
    ],
    "株式": [
        "InvestmentSecurities",
        "Securities",
        "ShortTermInvestmentSecurities",
        "OtherSecurities",
    ],
    "純資産": [
        "NetAssets",
        "NetAssetsSummaryOfBusinessResults",
    ],
    "証券コード": ["SecurityCodeDEI"],
    "会社名": ["CompanyNameCoverPage"],
}

# === 株価関連 ===
def fetch_market_cap(ticker_code):
    """yfinanceで時価総額を取得"""
    if not ticker_code:
        return None
    try:
        t = yf.Ticker(f"{ticker_code}.T")
        mc = getattr(t.fast_info, "market_cap", None)
        if not mc and hasattr(t, "info"):
            mc = t.info.get("marketCap")
        return mc
    except Exception as e:
        print(f"⚠️ 時価総額取得失敗: {ticker_code} ({e})")
        return None

def fetch_stock_price(ticker_code):
    """yfinanceで現在株価を取得"""
    if not ticker_code:
        return None
    try:
        t = yf.Ticker(f"{ticker_code}.T")
        return getattr(t.fast_info, "last_price", None)
    except Exception as e:
        print(f"⚠️ 株価取得失敗: {ticker_code} ({e})")
        return None

# === XBRL解析 ===
def extract_xbrl_from_zip(zip_path):
    values = {"会社名": None, "証券コード": None, "現金": None, "不動産": None, "株式": None, "純資産": None}
    with zipfile.ZipFile(zip_path, 'r') as z:
        xbrl_files = [f for f in z.namelist() if f.endswith(".xbrl") and "-asr-" in f.lower()]
        if not xbrl_files:
            return values

        for xf in xbrl_files:
            with z.open(xf) as f:
                tree = ET.parse(f)
                root = tree.getroot()
                for elem in root.iter():
                    tag = elem.tag.split("}")[-1]
                    for key, candidates in TAG_MAP.items():
                        if tag in candidates and elem.text:
                            txt = elem.text.strip()
                            if key == "証券コード":
                                if txt.isdigit() and len(txt) == 5 and txt.endswith("0"):
                                    txt = txt[:-1]
                                values[key] = txt
                            elif key in ["現金", "不動産", "株式", "純資産"]:
                                if values[key] is None:
                                    try:
                                        values[key] = float(txt.replace(",", ""))
                                    except:
                                        values[key] = txt
                            elif key == "会社名":
                                if not values["会社名"]:
                                    values["会社名"] = txt
    return values

# === メイン処理 ===
def main():
    yuho_dir = r"yuho"
    results = []

    for file in os.listdir(yuho_dir):
        if file.endswith(".zip"):
            zip_path = os.path.join(yuho_dir, file)
            print(f"処理開始: {zip_path}")
            values = extract_xbrl_from_zip(zip_path)

            cash = values["現金"] or 0
            estate = values["不動産"] or 0
            stocks = values["株式"] or 0
            net_assets = values["純資産"] or 0
            ticker_code = values["証券コード"]
            company_name = values["会社名"]

            asset_sum = cash + estate + stocks
            market_cap = fetch_market_cap(ticker_code) if ticker_code else None
            ratio = asset_sum / market_cap * 100 if (market_cap and asset_sum) else None
            current_price = fetch_stock_price(ticker_code) if ticker_code else None

            results.append({
                "会社名": company_name,
                "証券コード": ticker_code,
                "現金": cash,
                "不動産": estate,
                "株式": stocks,
                "純資産": net_assets,
                "資産合計": asset_sum,
                "時価総額": market_cap,
                "倍率(資産÷時価総額×100)": round(ratio, 1) if ratio else None,
                "現在株価": current_price,
            })

    if not results:
        print("⚠️ どのファイルからも値を抽出できませんでした")
        return

    df = pd.DataFrame(results)

    # === アクティビスト銘柄一覧と結合 ===
    acquired_df = pd.read_excel(r"docs/アクティビスト銘柄一覧.xlsx")
    acquired_df = acquired_df[["証券コード", "取得単価（円/株）", "提出者名", "報告義務発生日"]]

    # 型を文字列に統一
    df["証券コード"] = df["証券コード"].astype(str)
    acquired_df["証券コード"] = acquired_df["証券コード"].astype(str)

    # 同じ証券コードに複数提出者がいる場合 → そのまま全て残す
    df = df.merge(acquired_df, on="証券コード", how="left")

    # 株価変動率を計算
    df["株価変動率(%)"] = (
        (df["現在株価"] - df["取得単価（円/株）"]) / df["取得単価（円/株）"] * 100
    ).round(1)

    # 円単位の整数に整形
    for col in ["現金", "不動産", "株式", "資産合計", "時価総額", "純資産"]:
        df[col] = df[col].apply(lambda x: None if pd.isna(x) else int(round(x)))

    # 列の並び替え
    df = df[[
        "会社名", 
        "証券コード", 
        "倍率(資産÷時価総額×100)", 
        "現在株価", 
        "取得単価（円/株）", 
        "株価変動率(%)",
        "提出者名", 
        "報告義務発生日", 
        "現金", 
        "不動産", 
        "株式", 
        "純資産", 
        "資産合計", 
        "時価総額", 
    ]]



    save_path = r"docs/アクティビスト銘柄_資産判定.xlsx"
    df.to_excel(save_path, index=False)

    print("=== 抽出結果プレビュー ===")
    print(df.head(20))
    print(f"✅ 完了: {save_path}")

if __name__ == "__main__":
    main()