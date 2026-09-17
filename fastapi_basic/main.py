from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from typing import Optional


# FastAPI 객체 생성
app = FastAPI()

# http://localhost:8000/  --->  접속 시 호출되는 함수
# http://127.0.0.1:8000/
@app.get("/")
async def root():
    # 비즈니스 로직
    data =  "db에서 데이터 읽어오기"
    return {"message": data}

# DTO : 데이터 전송 객체
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[HttpUrl] = None

# http://localhost:8000/items/
@app.get("/items/")
def read_item():
    item_id = 1
    q = "사과"
    return {"item_id": item_id, "q": q}

# http://localhost:8000/items/300?q=수박
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    # 비즈니스 로직
    print(f"item_id: {item_id}, q: {q}")
    return {"item_id": item_id, "q": q}



@app.post("/user_info/")
def create_user(user: UserCreate):
    # 비즈니스 로직
    print(f"user_id: {user.user_id}")
    print(f"user_id: {user.email}")
    return user

@app.post("/user_info/{user_id}")
# def create_user(user_id: int, q: str | None = None):
def create_user(user_id, q):
    # 비즈니스 로직
    print(f"user_id: {user_id}, q: {q}")
    return {"user_id": user_id, "q": q}