from fastapi import FastAPI, Depends, HTTPException, Form, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext as PassContext
from app.database import engine, get_db
from app import models
from pathlib import Path
from fastapi.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

pwd_context = PassContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@app.get("/register", response_class=HTMLResponse)
def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/register")
def register_user(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed_pwd = get_password_hash(password)
    new_user = models.User(username=username, hashed_password=hashed_pwd)

    db.add(new_user)
    db.commit()

    return {"message": "Пользователь успешно создан. Теперь вы можете войти."}


@app.post("/login")
def login_user(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )

    return {"message": f"Добро пожаловать, {username}!"}


@app.get("/")
def read_root():
    return RedirectResponse(url="/home", status_code=303)


@app.get("/home", response_class=HTMLResponse)
def get_home_page(request: Request):

    worker = {
        "name": "Ali",
        "image_url": "https://via.placeholder.com/150"
    }

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "worker": worker
        }
    )