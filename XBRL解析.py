import os, zipfile, pandas as pd, xml.etree.ElementTree as ET

TAG_MAP = {
    "証券コード": ["SecurityCodeDEI"],
    "提出者名": ["FilerNameInJapanese"],
    "会社名": ["CompanyNameCoverPage"]
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
    input_dir = "xbrl_reports"
    output_dir = "docs"
    os.makedirs(output_dir, exist_ok=True)

    results = []
    for file in os.listdir(input_dir):
        if file.endswith(".zip"):
            values = extract_xbrl_from_zip(os.path.join(input_dir, file))
            results.append(values)

    df = pd.DataFrame(results)
    save_path = os.path.join(output_dir, "大量保有報告書_解析結果.xlsx")
    df.to_excel(save_path, index=False)
    print(f"✅ 保存完了: {save_path}")

if __name__ == "__main__":
    main()
