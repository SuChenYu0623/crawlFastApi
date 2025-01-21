from pymongo import MongoClient

# 連接到 MongoDB
client = MongoClient("mongodb://localhost:27017/")

# 選擇資料庫與集合
db = client["crawl_database"]
collection = db["crawl_items"]
# collection.create_index("newsId", unique=True)


# # 插入文件
data = {
    "newsId": "animals-death-monso",
    "title": "What Ants and Orcas Can Teach Us About Death",
    "summary": "A philosopher journeys into the world of comparative thanatology, which explores how animals of all kinds respond to death and dying.",
    "images_with_desc": [
        {
            "src": "https://static01.nyt.com/images/2024/10/29/multimedia/28SCI-CONVERSATION-ANIMALDEATH-bpfm/28SCI-CONVERSATION-ANIMALDEATH-bpfm-articleLarge.jpg?quality=75&auto=webp&disable=upscale",
            "alt": "A portrait of Susana Monsó who sits with her hands resting on a desk with a keyboard, coasters, books and notebooks and a vase of flowers on it.",
            "desc": "Susana Monsó, a philosopher of animal minds at the National Distance Education University in Madrid. “I’ve always been interested in those capacities that are understood to be uniquely human,” she said. “Death was a natural topic to pick up.”Credit...Gianfranco Tripodo for The New York Times"
        }
    ],
    "url": "https://www.nytimes.com/2024/10/29/science/animals-death-monso.html",
    "press": "nytimes"
}
# collection.insert_one(data)
collection.update_one({"newsId": data["newsId"]}, {"$set": data}, upsert=True)

# 查詢文件
result = collection.find_one({"newsId": "animals-death-monso"})
print(result)