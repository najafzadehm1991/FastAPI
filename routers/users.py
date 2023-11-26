import sys

from starlette.responses import HTMLResponse

sys.path.append("..")

from starlette import  status
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Depends, Request, Form
import models
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user, get_user_exception, verify_password, get_password_hash

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="./templates")

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Users).all()

@router.get("/user/")
async def read_all(user_id, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user_model is not None:
        return user_model
    else:
        return "Invalid user_id"


@router.get("/edit-password", response_class=HTMLResponse)
async def edit_user_view(request : Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("edit-user-password.html", {"request":request, "user":user})


@router.post("/edit-password")
async def edit_password(request: Request, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    user_model = db.query(models.Users).filter(models.Users.id == user["id"]).first()

    if user_model is None:
        raise get_user_exception()

    form_data = await request.form()
    data = dict(form_data)
    print(data)

    check_password = verify_password(data["old_password"], user_model.hashed_password)
    if not check_password:
        msg = "your old password is incorrect"
        return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user, "msg": msg})


    if data["new_password"] != data["verify_new_password"]:
        msg = "new password and its verify is not match!"
        return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user, "msg":msg})

    hashed_password = get_password_hash(data["new_password"])
    user_model.hashed_password = hashed_password
    db.add(user_model)
    db.commit()
    msg= "password is changed successfully"
    return templates.TemplateResponse("edit-user-password.html", {"request":request, "user": user, "msg":msg})


@router.delete("/user/")
async def delete_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    user_model = db.query(models.Users).filter(models.Users.id == user.get("id")).first()

    if user_model is None:
        raise get_user_exception()

    db.delete(user_model)
    db.commit()
    return "user deleted!"

@router.get("/{user_id}")
async def read_all(user_id, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user_model is not None:
        return user_model
    else:
        return "Invalid user_id"