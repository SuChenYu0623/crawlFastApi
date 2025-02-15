from pydantic import BaseModel
from typing import List
from datetime import datetime

# 定義排程的資料模型
class LoopUrlTask(BaseModel):
    workType: str
    press: str
    urls: List[str]

class TasUrl(BaseModel):
    newsId: str
    url: str
    title: str
    press: str
    crawled: bool
    postTime: datetime
    createdAt: datetime
    updatedAt: datetime


class LoopUrlTaskV2(BaseModel):
    workType: str
    taskUrls: List[TasUrl]


class CollectUrlsTask(BaseModel):
    workType: str
    # press: str

# 定義接收 data 的資料模型
class NewsDataModel(BaseModel):
    newsId: str
    url: str
    title: str
    press: str
    summary: str
    images_with_desc: List[dict]
    postTime: datetime

class NewsDataModelResponse(NewsDataModel):
    updatedAt: str

class NewsUrlDataModel(BaseModel):
    newsId: str
    url: str
    title: str
    press: str
    postTime: datetime
    class Config:
        # 設置 datetime 的 JSON 編碼方式
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NewsUrlDataModelResponse(NewsUrlDataModel):
    crawled: bool
    postTime: datetime
    updatedAt: datetime
    createdAt: datetime

# 定義接收 log 的資料模型
class LogModel(BaseModel):
    timestamp: str  # ISO 格式的時間
    level: str      # 日誌級別，例如 "INFO", "ERROR"
    message: str
    press: str