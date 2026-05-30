from sqlalchemy import Column, Integer, String, DateTime, create_engine
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
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    last_message_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    streak_count = Column(Integer, default=0)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, nullable=False, index=True)
    body = Column(String(500))
    direction = Column(String(10))  # 'inbound' or 'outbound'
    created_at = Column(DateTime, default=datetime.now)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()