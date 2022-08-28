from pprint import pprint
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World11111222222"}


fake_items_db = [{"item_name": "Foo"},
                 {"item_name": "Bar"},
                 {"item_name": "Baz"}]


# 1. query param
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    print(f'skip: {skip}')
    print(f'limit: {limit}')
    return fake_items_db[skip: skip + limit]


# 2. path param
@app.get("/items/{item_id}")
async def read_item(item_id):
    print(f'item_id: {item_id}')
    return {"item_id": item_id}


# 3. path, query, request body 모두 테스트
class MyBody(BaseModel):
    name: str
    description: Union[str, None] = None  # Union 여러 타입을 허용할 수 있을 때 사용
    price: float
    tax: Union[float, None] = None


@app.post("/body/{request_num}")
async def test_body(request_num: str, my_body: MyBody, q: Union[str, None] = None):
    # return my_body
    # return request_num + my_body.dict()['name']
    result = {"req_id": request_num, **my_body.dict()}
    if q:
        result.update({"q": q})
    return result


# 4. pymongo insert_one()
client = MongoClient(host='localhost', port=27017, username='root', password='root')

db = client['test-db']
collection = db['event']


class ReqEvent(BaseModel):
    event: dict


class ResEvent(BaseModel):
    event: dict


@app.post("/insert_one", response_model=ResEvent)
async def insert_one(event_one: ReqEvent):
    collection.insert_one(event_one.dict())
    return event_one


# 5. pymongo find_one()
from bson.objectid import ObjectId


class ResBody(BaseModel):
    _id: ObjectId
    event: dict


@app.get("/find_one", response_model=ResBody, response_model_exclude_unset=True)
async def find_one(doc_id: Union[str, None] = None):
    bson_id = ObjectId(doc_id)
    find_json = collection.find_one({"_id": bson_id})
    pprint(find_json)

    return find_json


# 6. pymongo find()
@app.get("/find_all", response_model=list[ResBody])
async def find_all():
    find_json = collection.find()
    pprint(type(find_json))  # <class 'pymongo.cursor.Cursor'>

    # Cursor to list 1
    result = []
    for i in find_json:
        result.append(i)

    # Cursor to list 2
    result = list(collection.find())

    return result


# 7. insert_many()
@app.post("/insert_many")
async def insert_many(event_many: list[ReqEvent]):
    # print(type(event_many))
    # for i in event_many:
    #     pprint(i.dict())
    #     print(type(i.dict()))
    insert_result = collection.insert_many([event.dict() for event in event_many])
    # print(insert_result.inserted_ids)
    # print(type(insert_result.inserted_ids))
    # for i in insert_result.inserted_ids:
    #     print(type(i))
    #     print(i.__str__())
    result = [i.__str__() for i in insert_result.inserted_ids]
    return result
