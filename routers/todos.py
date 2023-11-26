import os
import sys
sys.path.append("..")
from typing import Optional
from starlette import  status
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse, Response, HTMLResponse
from .auth import get_current_user, get_user_exception

from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)
models.Base.metadata.create_all(bind=engine)



templates = Jinja2Templates(directory="./templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def real_all_by_user(request: Request, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):

    # user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()

    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user": user})

@router.get("/add-todo/", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})

@router.post("/add-todo/")
async def create_todo(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    form_data = await request.form()
    data = dict(form_data)
    todo_model = models.Todos(**data, **{"complete": False, "owner_id": user.get("id")})

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)


    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()

    if todo is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})

@router.post("/edit-todo/{todo_id}")
async def edit_todo(request:Request,todo_id = int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    todo = (db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first())
    form_data = await request.form()
    data = dict(form_data)

    for key, value in data.items():
        setattr(todo, key, value)

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/delete/{todo_id}")
async def delete_todo(request:Request, todo_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)

    todo = (db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first())

    if todo is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    db.delete(todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def delete_todo(request:Request, todo_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)

    todo = (db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first())

    if todo is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


    todo.complete = not todo.complete

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


# class Todo(BaseModel):
#     title: str
#     description: Optional[str] = None
#     priority: int = Field(gt=0, lt=6, description="The priority must between 1 - 5")
#     complete: bool
#
# @router.get("/test")
# async def test(request:Request):
#     return templates.TemplateResponse("home.html", {"request":request})
#
#
# @router.get("/")
# async def get_all(db: Session = Depends(get_db)):
#     return db.query(models.Todos).all()
#
# @router.post("/")
# async def create_todos(todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#
#     if user is None:
#         raise get_user_exception()
#     owner = {"owner_id":user["id"]}
#     todo_model = models.Todos(**todo.__dict__, **owner)
#
#
#
#     db.add(todo_model)
#     db.commit()
#
#     return JSONResponse(status_code=201, content="todo is created")
#
# '''todo_model = models.Todos()
#     todo_model.title = todo.title
#     todo_model.description = todo.description
#     todo_model.priority = todo.priority
#     todo_model.complete = todo.complete'''
#
#
# @router.get("/user/")
# async def get_user_todo(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()
#
#
# @router.get("/{todo_id}")
# async def get_todo(todo_id:int, db: Session = Depends(get_db)):
#     todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
#     if todo_model is not None:
#         return todo_model
#     raise http_exception()
#
#
# @router.put("/{todo_id}")
# async def edit(todo_id: int, todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(
#         models.Todos.owner_id == user["id"]).first()
#
#     if todo_model is None:
#         raise http_exception()
#
#     todo_dict = dict(todo.__dict__)
#     for key, value in todo_dict.items():
#         setattr(todo_model, key, value)
#
#     db.add(todo_model)
#     db.commit()
#
#     return JSONResponse(status_code=200, content="todo is updated")
#
#
# @router.delete("/{todo_id}")
# async def delete(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id)\
#         .filter(models.Todos.owner_id == user["id"]).first()
#
#     if todo_model:
#         db.delete(todo_model)
#         db.commit()
#         return Response(status_code=204)
#     raise http_exception()
#
#
# def http_exception():
#     return HTTPException(status_code=404, detail="Todo not found")