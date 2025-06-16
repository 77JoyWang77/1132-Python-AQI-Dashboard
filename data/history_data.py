import os
import sqlite3
import pandas as pd
from tqdm import tqdm

folder_path = "data/history_data"

all_data = []
for file in tqdm(sorted(os.listdir(folder_path)), desc="讀取 CSV 檔"):
    if file.endswith(".csv"):
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        needed_cols = [
            'siteid', 'sitename', 'monitordate', 'aqi',
            'so2subindex', 'cosubindex', 'o3subindex', 'pm10subindex',
            'no2subindex', 'o38subindex', 'pm25subindex'
        ]
        df = df[[col for col in needed_cols if col in df.columns]]
        all_data.append(df)

merged_df = pd.concat(all_data, ignore_index=True)

# 處理日期欄位，加入 year、month、day
merged_df["monitordate"] = pd.to_datetime(merged_df["monitordate"], errors="coerce")
merged_df = merged_df.dropna(subset=["monitordate"])
merged_df["year"] = merged_df["monitordate"].dt.year.astype(str)
merged_df["month"] = merged_df["monitordate"].dt.month.astype(str)
merged_df["day"] = merged_df["monitordate"].dt.day.astype(str)

# 加 mainpollutant 欄位
subindex_cols = [
    'so2subindex', 'cosubindex', 'o3subindex', 'pm10subindex',
    'no2subindex', 'o38subindex', 'pm25subindex'
]
def find_main_pollutant(row):
    aqi = row['aqi']
    for col in subindex_cols:
        if pd.notna(row.get(col)) and row.get(col) == aqi:
            return col.replace('subindex', '')
    return '-1'
merged_df['mainpollutant'] = merged_df.apply(find_main_pollutant, axis=1)

# 儲存
db_path = "data/aqi_history.db"
conn = sqlite3.connect(db_path)
merged_df.to_sql("aqi", conn, if_exists="replace", index=False)
conn.close()

print(f"✅ 已經把 year、month、day 也寫進資料庫囉（資料筆數：{len(merged_df)}）")
