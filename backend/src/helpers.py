# database.py
from sqlalchemy.orm import Session
from src.models import Trader, Message
from datetime import date, datetime

class TraderService:
    
    @staticmethod
    def get_or_create_trader(db: Session, phone_number: str):
        """Get existing trader or create new one"""
        # Clean phone number: remove 'whatsapp:' prefix
        clean_phone = phone_number.replace("whatsapp:", "")
        
        trader = db.query(Trader).filter(Trader.phone_number == clean_phone).first()
        
        if not trader:
            # New trader — create them
            trader = Trader(
                phone_number=clean_phone,
                created_at=datetime.now(),
                streak_count=0
            )
            db.add(trader)
            db.commit()
            db.refresh(trader)
            print(f"✅ Created new trader: {clean_phone}")
        else:
            print(f"✅ Found existing trader: {clean_phone}")
        
        return trader
    
    @staticmethod
    def log_message(db: Session, trader_id: int, body: str, direction: str):
        """Store message in database"""
        message = Message(
            trader_id=trader_id,
            body=body,
            direction=direction  # 'inbound' for received, 'outbound' for sent
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_streak(db: Session, trader_id: int):
        """Get trader's current streak"""
        trader = db.query(Trader).filter(Trader.id == trader_id).first()
        return trader.streak_count if trader else 0
    
    @staticmethod
    def update_streak(db: Session, trader_id: int):
        """Increment streak if new day"""
        trader = db.query(Trader).filter(Trader.id == trader_id).first()
        
        if trader:
            today = date.today()
            last_log_date = trader.last_message_at.date() if trader.last_message_at else None
            
            if last_log_date != today:
                trader.streak_count += 1
                trader.last_message_at = datetime.now()
                db.commit()
                print(f"🔥 Updated streak to {trader.streak_count}")