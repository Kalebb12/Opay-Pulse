from sqlalchemy import Column, Integer, String, DateTime, create_engine, Numeric, Boolean
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

class DashboardToken(Base):
    __tablename__ = "dashboard_tokens"

    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, nullable=False, index=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

class CreditSale(Base):
    __tablename__ = "credit_sales"
    
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, nullable=False, index=True)
    customer_name = Column(String(100), nullable=False)
    amount_owed = Column(Numeric(12, 2), nullable=False)
    amount_paid = Column(Numeric(12, 2), default=0)
    due_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="outstanding")
    # outstanding → partially_paid → paid → overdue
    notes = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()