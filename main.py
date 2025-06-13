from fastapi import FastAPI, HTTPException, Body, Request, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import List, Any
from datetime import datetime
import json
import httpx
from dataModels import LoopUrlTask, TasUrl, LoopUrlTaskV2, CollectUrlsTask, NewsDataModel, NewsDataModelResponse, NewsUrlDataModel, NewsUrlDataModelResponse, LogModel
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import io

# custom
from PIL import Image
import torch
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode
from models.blip import blip_decoder
from transformers import BlipProcessor, BlipForConditionalGeneration

class PredictBase():
    def __init__(self):
        # 使用模型
        pass

    # TODO 載入模型
    def load_model(self):
        ...

    # TODO 預測
    def predict(self, image_path):
        ...


class PredictModel(PredictBase):
    """
    自己訓練的模型
    模型架構與 BLIP 一致 (當前只有 VLM 部份)
    """
    def __init__(self, pretrained_path: str):
        # pretrained_path = 'saveModels/BlipV1.0.pth'
        self.image_size = 224
        self.model = self.load_model(pretrained_path=pretrained_path)
        pass
    
    # TODO load image
    # def load_image(self, raw_image: str, image_size: int, device: str):
    def load_image(self, raw_image: Image.Image, image_size: int, device: str):
        # raw_image = Image.open(str(image_path)).convert('RGB')
        w, h = raw_image.size
        transform = transforms.Compose([
            transforms.Resize((image_size, image_size), interpolation=InterpolationMode.BICUBIC),
            transforms.ToTensor(),
            transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
        ])
        image = transform(raw_image).unsqueeze(0).to(device)
        return image
    
    # TODO load model
    def load_model(self, pretrained_path: str):
        model = blip_decoder(pretrained=pretrained_path, image_size=224, vit='base')
        return model

    def predict(self, im):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # model = blip_decoder(pretrained=pretrained_path, image_size=224, vit='base')
        self.model.eval()
        self.model = self.model.to(device)

        # im = self.load_image(image_path, self.image_size, device)
        im = self.load_image(im, self.image_size, device)
        with torch.no_grad():
            caption = self.model.generate(im, sample=False, num_beams=1, max_length=40, min_length=5)
            return caption[0]



# 建立 FastAPI 應用程式
app = FastAPI()

# 設置 CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000", "http://localhost:8000",
        "http://127.0.0.1:3000", "http://localhost:3000"
    ],  # 允許的源，["*"] 表示所有
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
pretrained_path = '/home/chris/Desktop/VLM/BlipV1/record/newsDatasetV2_50/model.pth'
predictModel = PredictModel(pretrained_path=pretrained_path)

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
        raise HTTPException(status_code=400,
                            detail=f"Invalid task format: {e}")


@app.post("/v2/task/loopUrlTask/", status_code=201)
async def recieve_loopurl_task(byteData: Any = Body(...)):
    print('task')
    try:
        task = json.loads(byteData.decode("utf-8"))
        LoopUrlTaskV2.model_validate(task)

        return {"message": "loopUrlTask v2 successfully."}
    except ValidationError as e:
        print(e)
        raise HTTPException(status_code=400,
                            detail=f"Invalid task format: {e}")
    except Exception as e:
        print(e)


@app.post("/v1/task/collectUrlsTask/", status_code=201)
def recieve_collectUrls_task(byteData: Any = Body(...)):
    # 先暫時沒有實質作用，先檢查格式就好
    # (後續應該是存 log)
    try:
        task = json.loads(byteData.decode("utf-8"))
        CollectUrlsTask.model_validate(task)
        return {"message": "collectUrlsTask successfully."}
    except ValidationError as e:
        raise HTTPException(status_code=400,
                            detail=f"Invalid task format: {e}")


@app.post("/v1/save/newsItems/", status_code=201)
def save_newsItems(byteData: Any = Body(...)):
    datas = json.loads(byteData.decode("utf-8"))

    for data in datas:
        try:
            dict_data = NewsDataModel.model_validate(data)
            collection.update_one(
                {"newsId": dict_data.newsId},
                {
                    "$set": {
                        **dict_data.model_dump(), "updatedAt":
                        datetime.utcnow()
                    },  # 更新或插入資料，並設置更新時間
                    "$setOnInsert": {
                        "createdAt": datetime.utcnow(),
                        "downloaded": False,
                        "processed": False
                    }  # 如果是插入，設置創建時間
                },
                upsert=True)

            collectUrls_collection.update_one(
                {"newsId": data["newsId"]},
                {
                    "$set": {
                        "updatedAt": datetime.utcnow(),
                        "crawled": True
                    },  # 更新或插入資料，並設置更新時間
                },
                upsert=True)
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
                    "$set": {
                        **dict_data.model_dump(), "updatedAt":
                        datetime.utcnow()
                    },  # 更新或插入資料，並設置更新時間
                    "$setOnInsert": {
                        "crawled": False,
                        "createdAt": datetime.utcnow()
                    }  # 如果是插入，設置創建時間
                },
                upsert=True)
            sucess_cnt += 1
        except ValidationError as e:
            print('sucess write:', sucess_cnt)
            return {
                "message": "Datas saved failed.",
                "wrong_data": data,
                "e": e
            }
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
def get_data_newsItems_all(size: int = Query(...)):
    if size:
        all_data = collection.find().limit(size)
    else:
        all_data = collection.find()
    serialized_data = [serialize_newsItems_document(doc) for doc in all_data]
    return serialized_data


@app.get("/v1/data/newsItems/all_length", response_model=int)
def get_data_newsItems_all_length():
    total = collection.count_documents({})
    print(type(total))
    return total


@app.get("/v1/data/newsUrls/all",
         response_model=List[NewsUrlDataModelResponse])
def get_data_newsUrls_all():
    all_data = collectUrls_collection.find().sort("postTime", 1)
    return all_data


@app.get("/v1/data/newsUrls/", response_model=List[NewsUrlDataModelResponse])
def get_data_newsUrls(size: int = Query(5, ge=1, le=100)):
    query = {"crawled": False}  # 篩選未爬取的資料
    if size:
        specified_datas = collectUrls_collection.find(query).sort(
            "postTime", 1).limit(size)
    else:
        specified_datas = collectUrls_collection.find(query).sort(
            "postTime", 1)
    return specified_datas


@app.get("/v1/data/newsUrls/all_length", response_model=int)
def get_data_newsUrls_all_length():
    total = collectUrls_collection.count_documents({})
    return total


@app.post("/v1/imagecaption/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.filename.endswith(".jpg"):
        return {"message": "只接受 JPG 檔案"}
    
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    # image 做預測
    caption = predictModel.predict(im=image)
    return {"message": caption}
