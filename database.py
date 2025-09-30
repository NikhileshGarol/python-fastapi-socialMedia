from models import Post, User, Vote
from base import Base
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Create database connection string
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Import models so SQLAlchemy registers them
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# def check_connection():
#     try:
#         with engine.connect() as conn:
#             conn.execute(text("SELECT 1"))
#             print("✅ Connected to MySQL successfully!")
#     except Exception as e:
#         print(f"❌ Connection error: {e}")

# if __name__ == "__main__":
#     check_connection()
