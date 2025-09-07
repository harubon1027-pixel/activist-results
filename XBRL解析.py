import os
import glob
import zipfile
import pandas as pd
import re
import os
os.makedirs("xbrl_reports", exist_ok=True)
os.makedirs("docs", exist_ok=True)

BASE_DIR = r"xbrl_reports"
OUTPUT_EXCEL = os.path.join("docs", "大量保有報告書_解析結果.xlsx")

def to_halfwidth_num(s: str) -> str:
    if s is None: return ""
    trans = str.maketrans("０１２３４５６７８９，．－", "0123456789,.-")
    return str(s).translate(trans)

def parse_number(val):
    if val is None: return None
    s = to_halfwidth_num(str(val)).replace(",", "").strip()
    if s in ("", "－", "-", "—"): return None
    try:
        return float(s)
    except:
        return None

UNIT_MULTIPLIER = {"円":1, "千円":1_000, "万円":10_000, "百万円":1_000_000}

def normalize_currency(value, unit_label):
    if value is None: return None
    mul = UNIT_MULTIPLIER.get((unit_label or "").strip(), 1)
    return value * mul

def extract_value(df, patterns, numeric=False):
    mask = df["項目名"].astype(str).str.contains("|".join(patterns), na=False)
    if not mask.any(): return None, None
    row = df.loc[mask].iloc[0]
    val = parse_number(row["値"]) if numeric else str(row["値"])
    unit = row["単位"] if "単位" in row else None
    return val, unit

def extract_sec_code(df):
    mask = df["項目名"].astype(str).str.contains("証券コード", na=False)
    for v in df.loc[mask, "値"].astype(str):
        hv = to_halfwidth_num(v)
        m = re.search(r"\b(\d{4})\b", hv)
        if m: return m.group(1)
    return None

records = []

for zip_path in glob.glob(os.path.join(BASE_DIR, "*.zip")):
    # ファイル名に「変更」「訂正」が含まれる場合はスキップ
    fname = os.path.basename(zip_path)
    if "変更" in fname or "訂正" in fname:
        continue

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            csv_paths = [p for p in z.namelist() if p.startswith("XBRL_TO_CSV/") and p.endswith(".csv")]
            if not csv_paths:
                print(f"⚠️ CSVなし: {fname}")
                continue

            for csv_in_zip in csv_paths:
                with z.open(csv_in_zip) as f:
                    try:
                        df = pd.read_csv(f, encoding="utf-16", sep=None, engine="python")
                    except UnicodeError:
                        df = pd.read_csv(f, encoding="cp932", sep=None, engine="python")

                # 提出者名
                filer_jp, _ = extract_value(df, ["提出者名（日本語表記）"])
                filer_en, _ = extract_value(df, ["提出者名（英語表記）"])
                filer = filer_jp or filer_en

                # 証券コード（4桁）
                sec_code = extract_sec_code(df)

                # 報告義務発生日
                acquire_val, _ = extract_value(df, ["報告義務発生日"])
                acquire_date = acquire_val

                # 株数
                shares_val, _ = extract_value(df, ["保有株券等の数（総数）", "株券等の数（総数）"], numeric=True)

                # 取得資金合計（円換算）
                funds_val, unit = extract_value(df, ["取得資金合計", "株券等取得資金の合計額"], numeric=True)
                funds_yen = normalize_currency(funds_val, unit)

                # 取得単価
                unit_price = None
                if shares_val and funds_yen and shares_val != 0:
                    unit_price = funds_yen / shares_val

                # 報告書に記載されている保有割合
                ratio_val, _ = extract_value(df, ["株券等保有割合$"], numeric=True)
                ratio_pct = None
                if ratio_val is not None:
                    ratio_pct = ratio_val * 100  # ×100して百分率化

                # 発行済株式総数を抽出
                outstanding_val, _ = extract_value(df, ["発行済株式総数"], numeric=True)


                # ← この append を必ず for csv_in_zip の中に置く！
                records.append({
                    "zipファイル": fname,
                    "csvファイル": os.path.basename(csv_in_zip),
                    "提出者名": filer,
                    "証券コード": sec_code,
                    "報告義務発生日": acquire_date,
                    "保有株券等の数": shares_val,
                    "取得資金合計（円換算）": funds_yen,
                    "取得単価（円/株）": unit_price,
                    "保有割合（報告書記載値％）": ratio_pct
                })

    except Exception as e:
        print(f"❌ ZIP展開失敗: {fname}, {e}")

# Excel出力
df_out = pd.DataFrame(records)
df_out.to_excel(OUTPUT_EXCEL, index=False)
print(f"✅ 大量保有報告書の解析完了: {OUTPUT_EXCEL}")

print("✅ DataFrame shape:", df.shape)
print("✅ 保存先:", OUTPUT_EXCEL)
print("✅ ファイル存在:", os.path.exists(OUTPUT_EXCEL))

