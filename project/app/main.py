from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from pathlib import Path
import os, uvicorn, subprocess, asyncio
import pandas as pd

DATABASE_URL = "sqlite:///./app/users.db"
REQUEST_DATABASE_URL = "sqlite:///./app/requests.db"

engine = create_engine(DATABASE_URL)
request_engine = create_engine(REQUEST_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
RequestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=request_engine)

Base = declarative_base()

app = FastAPI()

def get_expected_columns() -> list:
    file_path = os.path.join("app", "DATA", "X_train.csv")
    try:
        df = pd.read_csv(file_path)
        return df.columns.tolist()
    except Exception as e:
        print(f"Error reading the reference file: {e}")
        return []

# Путь к корневой директории проекта
project_root = Path(__file__).parent.parent

app.mount("/style", StaticFiles(directory=project_root / "public" / "style"), name="style")
app.mount("/script", StaticFiles(directory=project_root / "public" / "script"), name="script")
app.mount("/images", StaticFiles(directory=project_root / "public" / "style" /"images"), name="images")
app.mount("/files", StaticFiles(directory=project_root / "app" / "Files"), name="files")
app.mount("/ML", StaticFiles(directory=project_root / "app" / "ML"), name="ML")

# Для Live Server

# origins = [
#     "http://127.0.0.1:5500",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

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
    project_name = Column(String, index=True)
    created_at = Column(DateTime, default=get_corrected_time)
    onboard_number = Column(String)
    linkname = Column(String, index=True)

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


# Маршруты для рендеринга HTML страниц
@app.get("/", response_class=FileResponse)
async def read_main():
    return FileResponse(project_root / "public" / "main.html")

# Маршрут для favicon.svg
@app.get("/favicon.svg", include_in_schema=False)
async def favicon():
    return FileResponse(project_root / "public" / "style" / "images" / "s7-airlines-white.svg")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(project_root / "public" / "style" / "images" / "s7-airlines-white.svg")

@app.get("/admin", response_class=FileResponse)
async def read_admin():
    return FileResponse(project_root / "public" / "admin.html")

@app.get("/projects", response_class=FileResponse)
async def read_projects():
    return FileResponse(project_root / "public" / "Projects.html")

@app.get("/request", response_class=FileResponse)
async def read_request():
    return FileResponse(project_root / "public" / "request.html")

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
async def upload_file(Username: str = Form(...), onboardNumber: str = Form(...), projectName: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_request_db)):   

    # Проверка структуры загружаемого файла
    uploaded_df = pd.read_csv(file.file)
    expected_columns = get_expected_columns()
    if list(uploaded_df.columns) != expected_columns:
        raise HTTPException(status_code=400, detail="Invalid file structure. The columns do not match the expected format.")
    
    # Перематываем файл обратно в начало
    file.file.seek(0)
    
    user_folder = os.path.join("app", "Files", Username)
    os.makedirs(user_folder, exist_ok=True)

    file_path = os.path.join(user_folder, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    linkname = os.path.splitext(file.filename)[0]  # Убираем расширение .csv
    output_dir = user_folder  # Сохранение новых файлов в ту же директорию, где хранится file_path
    aircraft = onboardNumber
    py_path = os.path.join(project_root, 'app', 'ML', 'example_import.py')

    # Проверка путей
    if not os.path.exists(py_path):
        raise HTTPException(status_code=500, detail=f"Script file not found: {py_path}")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail=f"Uploaded file not found: {file_path}")
    
    # Получение текущего времени
    created_at = get_corrected_time()
    created_at_str = (datetime.utcnow() + timedelta(hours=3)).strftime("%d-%m-%Y-%H-%M-%S")

    result = subprocess.run(["python", str(py_path), str(file_path), str(output_dir), str(aircraft), str(linkname),str(created_at_str)], capture_output=True, text=True)

    if result.returncode != 0:
        return {"status": "error", "message": result.stderr}

    new_request = Request(username=Username, project_name=projectName, onboard_number=onboardNumber, linkname=linkname, created_at=created_at)
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # Удаление загруженного файла
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {file_path}, {e}")

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
        
        created_at_str = request.created_at.strftime("%d-%m-%Y-%H-%M-%S")
        filename_base = request.linkname
        aircraft = request.onboard_number

        # Новые пути к файлам с учетом формата имени
        csv_file1 = os.path.join(user_folder, f"{filename_base}-{aircraft}-{created_at_str}-pos1.csv")
        csv_file2 = os.path.join(user_folder, f"{filename_base}-{aircraft}-{created_at_str}-pos2.csv")
        
        # Remove the file if it exists
        if os.path.exists(csv_file1):
            os.remove(csv_file1)
        if os.path.exists(csv_file2):
            os.remove(csv_file2)
        
        request_db.delete(request)

    user_folder = os.path.join("./app/Files", user.username)
    # Remove the directory if it exists
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
    
    user_folder = os.path.join("./app/Files", request.username)
    created_at_str = request.created_at.strftime("%d-%m-%Y-%H-%M-%S")
    filename_base = request.linkname
    aircraft = request.onboard_number

    # Новые пути к файлам с учетом формата имени
    csv_file1 = os.path.join(user_folder, f"{filename_base}-{aircraft}-{created_at_str}-pos1.csv")
    csv_file2 = os.path.join(user_folder, f"{filename_base}-{aircraft}-{created_at_str}-pos2.csv")
    
    # Remove the file if it exists
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

#Эндпоинт для получения путей к CSV файлам
@app.get("/requests/{request_id}/csv-files")
async def get_request_csv_files(request_id: int, db: Session = Depends(get_request_db)):
    # Находим реквест по ID
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Находим пользователя по имени в реквесте
    username = request.username

    # Получаем время создания и формируем строку
    created_at_str = request.created_at.strftime("%d-%m-%Y-%H-%M-%S")

    aircraft = request.onboard_number

    # Создаем пути к файлам
    user_folder = os.path.join('files', username)
    filename_base = request.linkname

    
    # Новые пути к файлам с учетом формата имени
    csv_file1 = os.path.join(user_folder, f"{filename_base}-{aircraft}-{created_at_str}-pos1.csv")
    csv_file2 = os.path.join(user_folder, f"{filename_base}-{aircraft}-{created_at_str}-pos2.csv")

    # Путь на сервере
    csv_file1_path = project_root / 'app' / csv_file1
    csv_file2_path = project_root / 'app' / csv_file2

    # Логирование путей для отладки
    print(f"Checking file paths:\n{csv_file1_path}\n{csv_file2_path}")

    if not csv_file1_path.exists() or not csv_file2_path.exists():
        raise HTTPException(status_code=404, detail="One or both files do not exist")

    return {"csv_file1": f"/{csv_file1}", "csv_file2": f"/{csv_file2}"}

async def main():
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    try:
        await server.serve()
    except asyncio.CancelledError:
        print("Server was cancelled")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Application interrupted")
    except asyncio.CancelledError:
        print("Application was cancelled during shutdown")

