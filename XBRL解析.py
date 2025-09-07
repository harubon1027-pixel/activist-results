import os, zipfile, pandas as pd, xml.etree.ElementTree as ET, yfinance as yf

TAG_MAP = {
    "証券コード": ["SecurityCodeDEI"],
    "会社名": ["CompanyNameCoverPage"],
    "現金": ["CashAndDeposits", "CashAndCashEquivalents"],
    "不動産": ["Land", "BuildingsAndStructuresNet"],
    "株式": ["InvestmentSecurities", "Securities"],
    "純資産": ["NetAssets"],
}

def extract_xbrl_from_zip(zip_path):
    values = {k: None for k in TAG_MAP}
    with zipfile.ZipFile(zip_path, 'r') as z:
        xbrl_files = [f for f in z.namelist() if f.endswith(".xbrl")]
        for xf in xbrl_files:
            with z.open(xf) as f:
                root = ET.parse(f).getroot()
                for elem in root.iter():
                    tag = elem.tag.split("}")[-1]
                    for key, candidates in TAG_MAP.items():
                        if tag in candidates and elem.text:
                            values[key] = elem.text.strip()
    return values

def main():
    yuho_dir = os.path.join(os.getcwd(), "yuho")
    os.makedirs(yuho_dir, exist_ok=True)
    results = []
    for file in os.listdir(yuho_dir):
        if file.endswith(".zip"):
            values = extract_xbrl_from_zip(os.path.join(yuho_dir, file))
            results.append(values)
    df = pd.DataFrame(results)
    df.to_excel(os.path.join("docs", "XBRL解析結果.xlsx"), index=False)

if __name__ == "__main__":
    main()
