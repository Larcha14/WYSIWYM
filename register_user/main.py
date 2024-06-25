from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os, uvicorn

DATABASE_URL = "sqlite:///./users.db"
REQUEST_DATABASE_URL = "sqlite:///./requests.db"

engine = create_engine(DATABASE_URL)
request_engine = create_engine(REQUEST_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
RequestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=request_engine)

Base = declarative_base()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    project_name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    onboard_number = Column(String)
    linkname = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=request_engine)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_request_db():
    db = RequestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register/")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    
    # Check if the username or email already exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = db.query(User).filter(User.username == user.username).first()


    new_user = User(username=user.username, email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create user directory
    user_dir = os.path.join("Files", user.username)
    os.makedirs(user_dir, exist_ok=True)

    return {"username": new_user.username, "id": new_user.id, "email": new_user.email}

@app.post("/login/")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"username": db_user.username, "id": db_user.id, "email": db_user.email}

@app.post("/upload")
async def upload_file(Username: str = Form(...), onboardNumber: str = Form(...), projectName: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_request_db)): # onboardNumber: str = Form(...), projectName: str = Form(...),
    user_folder = os.path.join("Files", Username)
    
    file_path = os.path.join(user_folder, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    linkname = file.filename

    new_request = Request(username=Username, project_name=projectName, onboard_number=onboardNumber, linkname=linkname)
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return JSONResponse(status_code=200, content={"message": "File uploaded successfully!"})

@app.get("/users/")
async def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.get("/requests/")
async def read_requests(db: Session = Depends(get_request_db)):
    requests = db.query(Request).all()
    return requests


@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), request_db: Session = Depends(get_request_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Get and delete all requests of the user
    user_requests = request_db.query(Request).filter(Request.username == user.username).all()
    for request in user_requests:
        user_folder = os.path.join("Files", request.username)
        file_path = os.path.join(user_folder, request.linkname)
        
        # Remove the file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        
        request_db.delete(request)
    request_db.commit()
    
    db.delete(user)
    db.commit()
    return {"message": "User and all related requests deleted successfully"}


@app.delete("/requests/{request_id}")
async def delete_request(request_id: int, db: Session = Depends(get_request_db)):
    request = db.query(Request).filter(Request.id == request_id).first()
    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    
    
    # Construct the file path
    user_folder = os.path.join("Files", request.username)
    file_path = os.path.join(user_folder, request.linkname)
    
    # Remove the file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(request)
    db.commit()
    return {"message": "Request deleted successfully"}


@app.get("/requests/{username}")
async def read_user_requests(username: str, db: Session = Depends(get_request_db)):
    requests = db.query(Request).filter(Request.username == username).all()
    return requests


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

# // База данных - запросы (str)

# // Имя пользователя
# // Project-name (Заданное пользователем)
# // Date + time creation
# // on-board number
# // Linkname (file.filename + time_sec)


# // 1) Создать БД с инфой о запросах (СДЕЛАНО)
# // 2) Drag'n Drop - создание папки username, сохранение tmp файла там + инфа о запросах в БД(СДЕЛАНО)
# // 3) Обязательное имя для проекта - ЧТОБЫ НАЖАТЬ UPLOAD (СДЕЛАНО)
# // 4) Обработчик DD, чтобы загружал только CSV  (СДЕЛАНО)
# // 5) Подумать над логикой удаления TMP, если была не нажата кнопка Upload/Окно закрылось (СДЕЛАНО)


# // 6) Сымитировать обработку ML

