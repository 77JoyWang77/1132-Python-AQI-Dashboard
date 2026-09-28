# 台灣空氣品質視覺化平台（Taiwan AQI Dashboard）

整合環境部即時 AQI 與近九年歷史資料，以 14 種互動圖表探索台灣空氣品質的時間、地區與污染物變化。

> 國立中央大學「程式設計-Python」期末個人專案（113-2）

## 功能

- **即時資料**：串接環境部開放資料 API，顯示近 24 小時與近 30 日各測站 AQI
- **歷史分析**：2016/09–2025/05 共 105 個月的歷史資料，存於 SQLite
- **14 種互動圖表**（Plotly Dash），依問題選圖型：

| 類型 | 圖表 |
|---|---|
| 地圖 | 即時 AQI 地圖、24 小時動態地圖 |
| 時間趨勢 | 年度 / 月份變化、每日折線、AQI 日曆熱力圖 |
| 地區比較 | 各測站比較 |
| 污染物 | 污染物分布、主污染物統計、AQI 等級與主污染物圓餅圖 |

- **觀察**：冬季污染較高，PM2.5 與臭氧為主要污染物

## 系統架構

```
環境部 API（即時）＋ 歷史 CSV → pandas 清理 → SQLite
        → Flask 主站 + 14 個 Plotly Dash 子應用
```

| 路徑 | 內容 |
|---|---|
| `app.py` | Flask 主站，掛載所有 Dash 圖表 |
| `dash_apps/` | 各圖表的 Dash 子應用 |
| `function/` | 抓取近 24 小時 / 30 日資料的排程程式（原設計為 Azure Functions） |
| `data/` | 歷史資料（CSV、SQLite） |
| `templates/`、`static/` | 網頁模板與靜態資源 |

## 執行方式

需求：Python 3.11。需先到[環境部環境資料開放平臺](https://data.moenv.gov.tw/)申請 API key。

```bash
pip install -r requirements.txt
export MOENV_API_KEY=你的key      # Windows PowerShell: $env:MOENV_API_KEY="你的key"
python app.py                     # http://localhost:5000
```

## 部署

原本以 GitHub Actions 自動部署到 Azure Web App。因 Azure 訂閱已停用，部署流程改為手動觸發（`.github/workflows/`）。

## 限制

- 即時資料的自動排程更新因雲端方案限制未完成。
