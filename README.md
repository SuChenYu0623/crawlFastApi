# crawlFastApi

**crawlFastApi** 是一個以 FastAPI 打造的爬蟲與多媒體推論後端，  
提供 *排程觸發*、*資料收集/儲存*、*資料查詢* 與 *圖片描述 (Image Caption)* 等 RESTful API。  
專案同時整合 **MongoDB** 進行持久化儲存，並可選擇在 GPU (CUDA) 環境下部署 **BLIP**-系模型，快速完成圖片文字化工作流程。

---

## 特色

| 功能 | 說明 |
| :-- | :-- |
| 排程任務 (task 類) | 透過 APScheduler 定期呼叫爬蟲或收斂 URL 任務。 |
| 資料儲存 (save 類) | 接收爬蟲回傳內容，去重／更新後寫入 MongoDB。 |
| 資料查詢 (data 類) | 依條件或批次拉取已存資料，支援分頁與總筆數查詢。 |
| 影像描述 (imagecaption 類) | 上傳 .jpg 直接回傳 BLIP 文字描述，可切換自訓模型。 |
| 日誌 (log 類) | API 介面已留位，方便後續擴充。 |

---

## 快速開始

> 以下指令以 **Ubuntu 22.04 + Python 3.10** 為例，其他環境請自行調整。

### 指令
```
# 1. git clone
git clone <ssh.git>
cd crawlFastApi

# 2. 啟用虛擬環境
python3 -m venv venv
source venv/bin/activate

# 3. 安裝套件 (必要)
pip install -r requirements.txt

# 4. 安裝套件 (如須使用佈署模型才需要)
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
pip install -r requirement_blip.txt

# 5. run (預設 http://127.0.0.1:8000)
uvicorn main:app --reload
```

---

## 專案結構

```
crawlFastApi/
│
├─ configs/                # ← 設定檔 (YAML/ENV) 等
├─ models/                 # ← 預訓練 / 自訓模型、權重
├─ transform/              # ← 前處理 / 後處理工具
|
├─ main.py              # 入口：建立 FastAPI 實例、掛載 Router
├─ dataModels.py        # Pydantic Schema
├─ .gitignore
├─ .pylintrc
├─ requirements.txt
├─ requirements_blip.txt
└─ README.md
```

---

## 路由總覽

### 1. task 類（爬蟲排程）

| Method | Path                      | 說明                     |
| ------ | ------------------------- | ------------------------ |
| POST   | `/v1/task/loopUrlTask/`   | 驗證 LoopUrlTask 格式    |
| POST   | `/v2/task/loopUrlTask/`   | v2 版，新增欄位驗證      |
| POST   | `/v1/task/collectUrlsTask/` | 驗證 CollectUrlsTask     |

### 2. save 類（資料寫入）

| Method | Path                   | payload | 說明                     |
| ------ | ---------------------- | ------- |------------------------ |
| POST   | `/v1/save/newsItems/`  | byteData | 批次寫入新聞正文資料     |
| POST   | `/v1/save/newsUrls/`   | byteData | 批次寫入新聞連結與狀態   |

### 3. log 類（預留）

| Method | Path    | 說明       |
| ------ | ------- | ---------- |
| POST   | `/log/` | 新增日誌   |
| GET    | `/log/` | 讀取全部日誌 |

### 4. data 類（資料讀取）

| Method | Path                           | 參數  | 功能                             |
| ------ | ------------------------------ | ----- | -------------------------------- |
| GET    | `/v1/data/newsItems/all`       | size  | 取出所有新聞項（筆資料）         |
| GET    | `/v1/data/newsItems/all_length`| —     | 取得新聞項總筆數                 |
| GET    | `/v1/data/newsUrls/all`        | —     | 取出全部 URL，依 postTime 排序   |
| GET    | `/v1/data/newsUrls/`           | size  | 取出未爬取之 URL（筆資料）       |
| GET    | `/v1/data/newsUrls/all_length` | —     | 取得 URL 總筆數                  |

### 5. imagecaption 類（模型推論）

| Method | Path                            | payload | 說明                           |
| ------ | ------------------------------- | --- | ------------------------------ |
| POST   | `/v1/imagecaption/upload/`      | file | 上傳 .jpg，回傳圖片描述 (Caption) |


## 授權
MIT，詳見 LICENSE。
