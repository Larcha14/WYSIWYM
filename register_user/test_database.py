from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import User ,DATABASE_URL
 

DATABASE_URL = DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_database():
    db = SessionLocal()
    try:
        #
        users = db.query(User).all()
        if users:
            print("Список пользователей в базе данных:")
            for user in users:
                print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
        else:
            print("База данных пуста.")
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
