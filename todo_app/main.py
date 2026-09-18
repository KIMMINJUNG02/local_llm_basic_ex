# fastAPI 메인 코드 파일
from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn # fast api 내장 웹서버
import os

from database import engine, SessionLocal, Base
import models # table 생성
# models에 정의한 모든 클래스, 연결한 DB엔진에 테이블로 생성
Base.metadata.create_all(bind=engine) # 데이터 베이스 생성

# FastAPI() 객체 생성
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # 마지막에 무조건 닫음
        db.close()

abs_path = os.path.dirname(os.path.realpath(__file__))
print(abs_path)
# html 템플릿 폴더를 지정하여 jinja템플릿 객체 생성
# templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory=f"{abs_path}/templates")

# static 폴더(정적파일 폴더)를 app에 연결
# app.mount("/static", StaticFiles(directory=f"static"), name="static")
app.mount("/static", StaticFiles(directory=f"{abs_path}/static"), name="static")


@app.get("/")
# 테이블 조회
async def home(request: Request, db_ss: Session = Depends(get_db)):
    todo = 0
    todo_list = db_ss.query(models.Todo)
    print(todo_list)

    todo_list = db_ss.query(models.Todo).order_by(models.Todo.id.desc()).all() # 테이블 전체 조회
    for todo in todo_list:
        print(f"id: {todo.id}, Todo: {todo.task}")
        
    return templates.TemplateResponse(
        request = request,
        name = "index.html",
        context={"todos": todo_list}
    )

# todo data DB table에 저장
@app.post("/add")
def add(request: Request, task: str = Form(...), db_ss: Session = Depends(get_db)):
    # task 데이터 받고
    print(task)
    # db table에 저장
    todo = models.Todo(task=task) # task 데이터를 받고, todo 클래스 통해서, 테이블과 연결된 객체생성
    db_ss.add(todo) # todo 테이블에 task 추가
    db_ss.commit() # 테이블에 반영
    # home으로 redirect
    return RedirectResponse(url=app.url_path_for("home"),  # 함수이름을 문자열로 주기 -> home함수로 redirect
                            status_code=status.HTTP_303_SEE_OTHER)

# todo 수정(조회, 수정)
@app.get("/edit/{todo_id}")
def edit(request: Request, todo_id: int, db_ss: Session = Depends(get_db)):
    # todo_id 조회
    todo = db_ss.query(models.Todo).filter(models.Todo.id == todo_id).first()
    print(todo.task)

    if todo is None:
        return HTTPException(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)
    # edit 폼에 렌더링 -> 리턴
    return templates.TemplateResponse(
        request=request,
        name="edit.html",
        context={"todo": todo}
    )
    
# todo 수정 내용 반영하기
@app.post("/edit/{todo_id}")
def update(request: Request, todo_id: int, task: str = Form(...), completed: bool = Form(...), db_ss: Session = Depends(get_db)):
    # todo_id 조회
    todo = db_ss.query(models.Todo).filter(models.Todo.id == todo_id).first()
    print(todo.task)

    if todo is None:
        return HTTPException(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)
    
    # 수정 내용 반영
    todo.task = task
    todo.completed = completed
    db_ss.commit() # 테이블에 반영

    # home으로 redirect
    return RedirectResponse(url=app.url_path_for("home"),  # 함수이름을 문자열로 주기 -> home함수로 redirect
                            status_code=status.HTTP_303_SEE_OTHER)  


# todo 삭제
@app.get("/delete/{todo_id}")
def delete(request: Request, todo_id: int, db_ss: Session = Depends(get_db)):
    # todo_id 조회
    todo = db_ss.query(models.Todo).filter(models.Todo.id == todo_id).first()
    print(todo.task)

    if todo is None:
        return HTTPException(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)
    
    # 삭제
    db_ss.delete(todo)
    db_ss.commit() # 테이블에 반영

    # home으로 redirect
    return RedirectResponse(url=app.url_path_for("home"),  # home으로 돌아가기
                            status_code=status.HTTP_303_SEE_OTHER)

# uv run main.py
if __name__ == "__main__":
    uvicorn.run('main:app', reload=True) # fastapi 객체 식별자
    # reload=True : 개발자 모드 -> 이거 없이할 땐 uv run fastapi dev