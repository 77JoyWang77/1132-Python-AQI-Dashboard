import requests
import pandas as pd
import time
import os

api_url = "https://data.moenv.gov.tw/api/v2"
dataset = "AQX_P_488"
format_type = "json"
limit = 40
api_key = "316432ca-af2d-4778-8dd5-ff38d2660893"
output_path = "data/aqi24.csv"

def fetch_with_retry(url, retries=3, sleep_sec=5):
    for i in range(retries):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                return resp
            else:
                print(f"HTTP {resp.status_code}: {url}")
        except Exception as e:
            print(f"嘗試第 {i+1} 次失敗: {e}")
        time.sleep(sleep_sec)
    print(f"最終失敗：{url}")
    return None

def fetch_aqi_24():
    print("開始抓取即時AQI 24小時資料...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    url_all = f"{api_url}/{dataset}?format={format_type}&limit=100&api_key={api_key}"
    resp = fetch_with_retry(url_all)
    if resp is None:
        print("❌ 取得測站清單失敗")
        return
    records = resp.json()["records"]
    site_names = sorted(list(set([r["sitename"] for r in records])))

    all_data = []
    for idx, site in enumerate(site_names, 1):
        print(f"[{idx}/{len(site_names)}] 抓取 {site} 資料")
        url = f"{api_url}/{dataset}?format={format_type}&limit={limit}&api_key={api_key}&filters=SiteName,EQ,{site}"
        resp = fetch_with_retry(url)
        if resp is not None:
            try:
                data = resp.json()["records"]
                all_data.extend(data)
            except Exception as e:
                print(f"{site} 解析失敗: {e}")
        time.sleep(1)

    if not all_data:
        print("❌ 沒有抓到任何資料")
        return

    df = pd.DataFrame(all_data)
    if "datacreationdate" not in df.columns or "sitename" not in df.columns:
        print("資料欄位錯誤")
        return
    df.drop_duplicates(subset=["datacreationdate", "sitename"], keep="last", inplace=True)
    df["datacreationdate"] = pd.to_datetime(df["datacreationdate"], errors="coerce")
    df = df.dropna(subset=["datacreationdate"])
    df_24 = (
        df.sort_values(["sitename", "datacreationdate"], ascending=[True, False])
          .groupby("sitename")
          .head(24)
          .reset_index(drop=True)
    )
    df_24.to_csv(output_path, index=False, encoding="utf-8")
    print(f"✅ 寫入 {output_path} 完成 ({len(df_24)} 筆, {len(site_names)} 站, 最新時間 {df_24['datacreationdate'].max()})")

if __name__ == "__main__":
    fetch_aqi_24()
