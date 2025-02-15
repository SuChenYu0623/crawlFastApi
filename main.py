from fastapi import FastAPI, HTTPException, Body, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import List, Any
from datetime import datetime
import json
import httpx
from models import LoopUrlTask, TasUrl, LoopUrlTaskV2, CollectUrlsTask, NewsDataModel, NewsDataModelResponse, NewsUrlDataModel, NewsUrlDataModelResponse, LogModel


# 建立 FastAPI 應用程式
app = FastAPI()

# 設置 CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000", "http://127.0.0.1:3000", "http://localhost:3000"],  # 允許的源，["*"] 表示所有
    allow_credentials=True,  # 是否允許攜帶憑據，如 Cookies 或 Authorization headers
    allow_methods=["*"],  # 允許的 HTTP 方法，["*"] 表示所有
    allow_headers=["*"],  # 允許的 HTTP 請求頭，["*"] 表示所有
)

# === mongo db ====
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util
client = MongoClient("mongodb://localhost:27017/")
db = client["crawl_database"]
collection = db["crawl_items"]
collectUrls_collection = db["crawl_urls"]


# === main ===

# 模擬儲存的資料結構
stored_data = []  # 用來存放接收到的 data
stored_logs = []  # 用來存放接收到的 log

@app.api_route("/", methods=["GET", "POST"])
def home(request: Request):
    print('home page')
    return {"message": "This is home page."}

@app.post("/v1/task/loopUrlTask/", status_code=201)
def recieve_loopurl_task(byteData: Any = Body(...)):
    # 先暫時沒有實質作用，先檢查格式就好
    # (後續應該是存 log)
    try:
        task = json.loads(byteData.decode("utf-8"))
        LoopUrlTask.model_validate(task)
        return {"message": "loopUrlTask successfully."}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid task format: {e}")

@app.post("/v2/task/loopUrlTask/", status_code=201)
async def recieve_loopurl_task(byteData: Any = Body(...)):
    try:
        task = json.loads(byteData.decode("utf-8"))
        LoopUrlTaskV2.model_validate(task)

        return {"message": "loopUrlTask v2 successfully."}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid task format: {e}")

@app.post("/v1/task/collectUrlsTask/", status_code=201)
def recieve_collectUrls_task(byteData: Any = Body(...)):
    # 先暫時沒有實質作用，先檢查格式就好
    # (後續應該是存 log)
    try:
        task = json.loads(byteData.decode("utf-8"))
        CollectUrlsTask.model_validate(task)
        return {"message": "collectUrlsTask successfully."}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid task format: {e}")

@app.post("/v1/save/newsItems/", status_code=201)
def save_newsItems(byteData: Any = Body(...)):
    datas = json.loads(byteData.decode("utf-8"))

    for data in datas:
        try:
            dict_data = NewsDataModel.model_validate(data)
            collection.update_one(
                {"newsId": dict_data.newsId},
                {
                    "$set": {**dict_data.model_dump(), "updatedAt": datetime.utcnow()},  # 更新或插入資料，並設置更新時間
                    "$setOnInsert": {
                        "createdAt": datetime.utcnow(),
                        "downloaded": False,
                        "processed": False
                    }   # 如果是插入，設置創建時間
                },
                upsert=True
            )

            collectUrls_collection.update_one(
                {"newsId": data["newsId"]},
                {
                    "$set": { "updatedAt": datetime.utcnow(), "crawled": True },  # 更新或插入資料，並設置更新時間
                },
                upsert=True
            )
        except Exception as e:
            return {"message": "Datas saved failed.", "wrong_data": data}

    return {"message": "Datas saved successfully.", "datas": datas}

@app.post("/v1/save/newsUrls/", status_code=201)
def save_newsUrls(byteData: Any = Body(...)):
    datas = json.loads(byteData.decode("utf-8"))

    sucess_cnt = 0
    print('datas len:', len(datas))
    for data in datas:
        try:
            dict_data = NewsUrlDataModel.model_validate(data)
            collectUrls_collection.update_one(
                {"newsId": dict_data.newsId},
                {
                    "$set": {**dict_data.model_dump(), "updatedAt": datetime.utcnow()},  # 更新或插入資料，並設置更新時間
                    "$setOnInsert": {
                        "crawled": False,
                        "createdAt": datetime.utcnow()
                    }   # 如果是插入，設置創建時間
                },
                upsert=True
            )
            sucess_cnt += 1
        except ValidationError as e:
            print('sucess write:', sucess_cnt)
            return {"message": "Datas saved failed.", "wrong_data": data, "e": e}
    print('sucess write:', sucess_cnt)
    return {"message": "Datas saved successfully.", "datas": datas}


@app.post("/log/", status_code=201)
def save_log(log: LogModel):
    # 將日誌儲存
    stored_logs.append(log.model_dump())
    return {"message": "Log saved successfully.", "log": log}

@app.get("/log/", response_model=List[LogModel])
def get_all_logs():
    return stored_logs

def serialize_newsItems_document(doc):
    doc["updatedAt"] = str(doc["updatedAt"])  # 將 ObjectId 轉為字符串
    return doc

@app.get("/v1/data/newsItems/all", response_model=List[NewsDataModelResponse])
def get_data_newsItems_all():
    all_data = collection.find()
    serialized_data = [serialize_newsItems_document(doc) for doc in all_data]
    return serialized_data

@app.get("/v1/data/newsItems/all_length", response_model=int)
def get_data_newsItems_all_length():
    total = collection.count_documents({})
    print(type(total))
    return total

@app.get("/v1/data/newsUrls/all", response_model=List[NewsUrlDataModelResponse])
def get_data_newsUrls_all():
    all_data = collectUrls_collection.find().sort("postTime", 1)
    return all_data

@app.get("/v1/data/newsUrls/", response_model=List[NewsUrlDataModelResponse])
def get_data_newsUrls(size: int = Query(5, ge=1, le=100)):
    query = {"crawled": False}  # 篩選未爬取的資料
    specified_datas = collectUrls_collection.find(query).sort("postTime", 1).limit(size)
    return specified_datas

@app.get("/v1/data/newsUrls/all_length", response_model=int)
def get_data_newsUrls_all_length():
    total = collectUrls_collection.count_documents({})
    print(type(total))
    return total

