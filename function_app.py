import logging
import azure.functions as func
import requests
import pandas as pd
import time
import os

app = func.FunctionApp()

@app.timer_trigger(schedule="0 0 * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False)
def aqi_fetcher_24(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('開始抓取即時AQI 24小時資料...')
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
                    logging.warning(f"HTTP {resp.status_code}: {url}")
            except Exception as e:
                logging.warning(f"嘗試第 {i+1} 次失敗: {e}")
            time.sleep(sleep_sec)
        logging.error(f"最終失敗：{url}")
        return None

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    url_all = f"{api_url}/{dataset}?format={format_type}&limit=100&api_key={api_key}"
    resp = fetch_with_retry(url_all)
    if resp is None:
        logging.error("❌ 取得測站清單失敗")
        return
    records = resp.json()["records"]
    site_names = sorted(list(set([r["sitename"] for r in records])))

    all_data = []
    for idx, site in enumerate(site_names, 1):
        logging.info(f"[{idx}/{len(site_names)}] 抓取 {site} 資料")
        url = f"{api_url}/{dataset}?format={format_type}&limit={limit}&api_key={api_key}&filters=SiteName,EQ,{site}"
        resp = fetch_with_retry(url)
        if resp is not None:
            try:
                data = resp.json()["records"]
                all_data.extend(data)
            except Exception as e:
                logging.warning(f"{site} 解析失敗: {e}")
        time.sleep(1)

    if not all_data:
        logging.error("❌ 沒有抓到任何資料")
        return

    df = pd.DataFrame(all_data)
    if "datacreationdate" not in df.columns or "sitename" not in df.columns:
        logging.error("資料欄位錯誤")
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
    logging.info(f"✅ 寫入 {output_path} 完成 ({len(df_24)} 筆, {len(site_names)} 站, 最新時間 {df_24['datacreationdate'].max()})")


@app.timer_trigger(schedule="0 0 * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False)
def aqi_fetcher_30(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info("開始抓取日AQI近30日資料...")
    api_url = "https://data.moenv.gov.tw/api/v2"
    dataset = "AQX_P_434"
    format_type = "json"
    limit = 50
    api_key = "316432ca-af2d-4778-8dd5-ff38d2660893"
    output_path = "data/aqi30.csv"

    def fetch_with_retry(url, retries=3, sleep_sec=5):
        for i in range(retries):
            try:
                resp = requests.get(url, timeout=30)
                if resp.status_code == 200:
                    return resp
            except Exception as e:
                logging.warning(f"嘗試第{i+1}次失敗: {e}")
            time.sleep(sleep_sec)
        logging.error(f"最終失敗：{url}")
        return None

    url_all = f"{api_url}/{dataset}?format={format_type}&limit=100&api_key={api_key}"
    resp = fetch_with_retry(url_all)
    if resp is None:
        logging.error("❌ 取得測站清單失敗")
        return
    records = resp.json()["records"]
    site_names = sorted(list(set([r["sitename"] for r in records])))

    all_data = []
    for idx, site in enumerate(site_names, 1):
        logging.info(f"[{idx}/{len(site_names)}] 抓取 {site} 資料")
        url = f"{api_url}/{dataset}?format={format_type}&limit={limit}&api_key={api_key}&filters=SiteName,EQ,{site}"
        resp = fetch_with_retry(url)
        if resp is not None:
            try:
                data = resp.json()["records"]
                all_data.extend(data)
            except Exception as e:
                logging.warning(f"{site} 解析失敗: {e}")
        time.sleep(1)
    if not all_data:
        logging.error("❌ 沒有抓到任何資料")
        return

    df = pd.DataFrame(all_data)
    if "monitordate" not in df.columns or "sitename" not in df.columns:
        logging.error("資料欄位錯誤")
        return
    df.drop_duplicates(subset=["monitordate", "sitename"], keep="last", inplace=True)
    df["monitordate"] = pd.to_datetime(df["monitordate"], errors="coerce")
    df = df.dropna(subset=["monitordate"])
    df_30 = (
        df.sort_values(["sitename", "monitordate"], ascending=[True, False])
          .groupby("sitename")
          .head(30)
          .reset_index(drop=True)
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_30.to_csv(output_path, index=False, encoding="utf-8")
    logging.info(f"✅ 寫入 {output_path} 完成 ({len(df_30)} 筆, {len(site_names)} 站, 最新時間 {df_30['monitordate'].max()})")