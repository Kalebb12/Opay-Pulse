from sqlalchemy import Column, Integer, String, DateTime, create_engine, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime
import os


load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Trader model
class Trader(Base):
    __tablename__ = "traders"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    last_log_date = Column(DateTime, nullable=True)
    streak_count = Column(Integer, default=0)
    credit_score = Column(Integer, nullable=True)

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, nullable=False, index=True)
    type = Column(String(10))  # 'income' or 'expense'
    amount = Column(Numeric(12, 2))
    category = Column(String(50))  # 'sales', 'stock', 'transport', etc
    description = Column(String(200), nullable=True)
    logged_at = Column(DateTime, default=datetime.now, index=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()