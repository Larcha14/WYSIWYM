from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from pathlib import Path
import os, uvicorn

DATABASE_URL = "sqlite:///./app/users.db"
REQUEST_DATABASE_URL = "sqlite:///./app/requests.db"

engine = create_engine(DATABASE_URL)
request_engine = create_engine(REQUEST_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
RequestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=request_engine)

Base = declarative_base()

app = FastAPI()

origins = [
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

def get_corrected_time():
    return datetime.utcnow() + timedelta(hours=3)

class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    project_name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=get_corrected_time)
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
    user_dir = os.path.join("./app/Files", user.username)
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
    # Проверка уникальности projectName
    existing_project = db.query(Request).filter(Request.project_name == projectName).first()
    if existing_project:
        raise HTTPException(status_code=400, detail="project name already exists")
    
    # Проверка уникальности имени файла
    existing_file = db.query(Request).filter(Request.linkname == file.filename).first()
    if existing_file:
        raise HTTPException(status_code=400, detail="filename already exists")
    
    user_folder = os.path.join("./app/Files", Username)
    
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
        user_folder = os.path.join("./app/Files", request.username)
        file_path = os.path.join(user_folder, request.linkname)

        filename_base = request.linkname
        csv_file1 = os.path.join(user_folder, f"{filename_base.replace('.csv', '')}-pos1.csv")
        csv_file2 = os.path.join(user_folder, f"{filename_base.replace('.csv', '')}-pos2.csv")
        
        # Remove the file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)

        if os.path.exists(csv_file1):
            os.remove(csv_file1)
        if os.path.exists(csv_file2):
            os.remove(csv_file2)
        
        request_db.delete(request)


    user_folder = os.path.join("./app/Files", user.username)
    # Remove the direction if it exists
    if os.path.exists(user_folder):
        os.rmdir(user_folder)

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
    user_folder = os.path.join("./app/Files", request.username)
    file_path = os.path.join(user_folder, request.linkname)

    filename_base = request.linkname
    csv_file1 = os.path.join(user_folder, f"{filename_base.replace('.csv', '')}-pos1.csv")
    csv_file2 = os.path.join(user_folder, f"{filename_base.replace('.csv', '')}-pos2.csv")
    
    # Remove the file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    if os.path.exists(csv_file1):
        os.remove(csv_file1)
    if os.path.exists(csv_file2):
        os.remove(csv_file2)

    db.delete(request)
    db.commit()
    return {"message": "Request deleted successfully"}


@app.get("/requests/{username}")
async def read_user_requests(username: str, db: Session = Depends(get_request_db)):
    requests = db.query(Request).filter(Request.username == username).all()
    return requests


# Эндпоинт для получения путей к CSV файлам
@app.get("/requests/{request_id}/csv-files")
async def get_request_csv_files(request_id: int, db: Session = Depends(get_request_db)):
    # Находим реквест по ID
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Находим пользователя по имени в реквесте
    username = request.username

    # Создаем пути к файлам
    user_folder = os.path.join('./app/Files', username)
    filename_base = request.linkname
    csv_file1 = os.path.join(user_folder, f"{filename_base.replace('.csv', '')}-pos1.csv")
    csv_file2 = os.path.join(user_folder, f"{filename_base.replace('.csv', '')}-pos2.csv")
    if not os.path.exists(csv_file1) or not os.path.exists(csv_file2):
        raise HTTPException(status_code=404, detail="error one or both files are not exist")

    return {"csv_file1": csv_file1, "csv_file2": csv_file2}



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


