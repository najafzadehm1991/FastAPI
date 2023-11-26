# import sys
# sys.path.append("..")

from starlette.responses import RedirectResponse

from fastapi import Depends, HTTPException, status, APIRouter, Request, Response
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError

from fastapi.templating import Jinja2Templates

SECRET_KEY = "eb51cde125c491a1e282c108c878a362b95f232b269bd8685e39d0f98826fde8"
ALGORITHM = "HS256"


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="./templates")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="fake_path")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"description": "Not authorized"}}
)

class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_from(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str
    phone_number: Optional[str] = None

def get_password_hash(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def authentication_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta]= None):

    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})

    return jwt.encode(encode, SECRET_KEY, algorithm = ALGORITHM)


@router.post("/create/")
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    dict = create_user.__dict__
    password = dict["password"]
    hashed_password = get_password_hash(password)
    del dict["password"]
    dict["hashed_password"] = hashed_password
    user_model = models.Users(**dict)


    db.add(user_model)
    db.commit()

    return JSONResponse(status_code=201, content="user is created")

@router.post("/token")
async def loggin_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authentication_user(form_data.username, form_data.password, db)
    if not user:
        return False

    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)

    response.set_cookie(key="access_token", value=token, httponly=True)

    return True

async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        return None


@router.get("/", response_class=HTMLResponse)
async def aurthentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/", response_class=HTMLResponse)
async def login(request:Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_from()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await loggin_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("login.html",{"request":request, "msg": msg})
        return  response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request":request, "msg": msg})

@router.get("/logout")
async def logout(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_user(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    data = dict(form_data)

    validation1 = db.query(models.Users).filter(models.Users.username == data.get("username")).first()

    validation2 = db.query(models.Users).filter(models.Users.email == data.get("email")).first()

    if data["password"] != data["password2"] or validation1 is not None or validation2 is not None:
        msg = "Invalid registration request"
        return templates.TemplateResponse("register.html", {"request":request, "msg": msg})

    hashed_password = get_password_hash(data["password"])

    data["hashed_password"] = hashed_password
    data["first_name"] = data["firstname"]
    data["last_name"] = data["lastname"]
    data["is_active"] = True

    del data["password"]
    del data["password2"]
    del data["firstname"]
    del data["lastname"]


    user_model = models.Users(**data)

    db.add(user_model)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


#Exception
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return credentials_exception

def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return token_exception_response