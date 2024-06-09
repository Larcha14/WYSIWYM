from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
# from joblib import load
from model import AircraftModel
# Загружаем модель
# air = load('model.joblib')
air = AircraftModel()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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

Base.metadata.create_all(bind=engine)

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

@app.post("/register/")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(username=user.username, email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"username": new_user.username, "id": new_user.id, "email": new_user.email}

@app.post("/login/")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"username": db_user.username, "id": db_user.id, "email": db_user.email}

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        predictions = air.predict(df)
        return {"filename": file.filename, "predictions": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Добавляем обработчик для /predict/
@app.post("/predict/")
async def predict(data: dict):
    try:
        df = pd.DataFrame([data])
        predictions = air.predict(df)
        return {"predictions": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

{'VQ-BGU': {'MAE': 1.8614627312154242,  'RMSE': 2.8050581042400884,
  'MAPE': 0.05974535788183595,
  'R2 Score': 0.8866836292333645},
 'VQ-BDU': {'MAE': 2.82195605805605,
  'RMSE': 3.494201399513671,
  'MAPE': 0.1170515730208239,
  'R2 Score': 0.8619503766413484}}