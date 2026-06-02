import token

from fastapi import FastAPI, Request, Depends, Query, HTTPException, File, UploadFile
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.rest import Client
import os
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from src.csv_handler import handle_csv_upload
from src.models import get_db, Transaction
from src.helpers import TraderService
from src.schemas import TraderTransactionsResponse
from sqlalchemy.orm import Session 
from sqlalchemy import desc
from src.agent import run_agent
import shutil


load_dotenv()


app = FastAPI(title="Opay Pulse API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
 
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@app.get("/")
async def root():
    return {"message": "Welcome to the Opay Pulse API!"}


@app.post("/whatsapp")
async def handle_whatsapp(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    incoming_phone = form_data.get("From")
    incoming_message = form_data.get("Body", "").strip()
    media_url = form_data.get("MediaUrl0")
    media_type = form_data.get("MediaContentType0", "")
    from src.voice_handler import transcribe_voice_note

    trader = TraderService.get_or_create_trader(db, incoming_phone)

    reply = None
    try:
        if media_url:
            if "audio" in media_type:
                # Voice note → transcribe → agent
                print(f"🎤 Processing voice note from {incoming_phone}")
                try:
                    transcribed = await transcribe_voice_note(media_url)
                    print(f"✅ Transcription complete: {transcribed[:100] if transcribed else 'EMPTY'}")
                    if transcribed:
                        reply = run_agent(db, trader, transcribed)
                        print(f"✅ Agent reply generated: {reply[:100]}...")
                    else:
                        reply = "I couldn't understand that voice note. Please try again or type your message."
                except Exception as e:
                    import traceback
                    print(f"❌ Voice transcription error: {str(e)}")
                    print(traceback.format_exc())
                    reply = "Had trouble processing your voice note. Please try again."
            else:
                # Document → CSV upload handler
                reply = await handle_csv_upload(db, trader, media_url)
        else:
            reply = run_agent(db, trader, incoming_message)
    except Exception as e:
        import traceback
        print(f"❌ WhatsApp handler error: {str(e)}")
        print(traceback.format_exc())
        reply = "Something went wrong. Please try again."

    # Fallback reply if somehow reply is still None
    if reply is None:
        print(f"❌ CRITICAL: reply is None for {incoming_phone}")
        reply = "I'm having trouble right now. Please try again."

    response = MessagingResponse()
    response.message(reply)
    print(f"📱 WhatsApp {incoming_phone}: {incoming_message[:50] if incoming_message else '(voice)'}... | 200 OK | Reply: {reply[:50]}...")
    return Response(content=str(response), media_type="application/xml")


# ============================================================
# Trader Dashboard API Endpoints
# ============================================================

# main.py — replace single endpoint with three

@app.get("/dashboard/validate")
async def validate_token(token: str, db: Session = Depends(get_db)):
    """Auth only — validates token, returns trader profile"""
    trader = TraderService.validate_dashboard_token(db, token)

    if not trader:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired link. Text DASHBOARD to get a new one."
        )

    return {
        "trader": {
            "phone": trader.phone_number,
            "streak": trader.streak_count,
            "credit_score": trader.credit_score,
            "member_since": trader.created_at.strftime("%B %Y")
        }
    }


@app.get("/dashboard/stats")
async def get_stats(token: str, db: Session = Depends(get_db)):
    """Financial stats — requires valid session token"""
    trader = TraderService.validate_dashboard_token(db, token)

    if not trader:
        raise HTTPException(status_code=401, detail="Session expired.")

    return {
        "today": TraderService.get_today_total(db, trader.id),
        "week": TraderService.get_week_summary(db, trader.id),
        "month": TraderService.get_month_summary(db, trader.id),
        "chart_data": TraderService.get_daily_chart_data(db, trader.id),
        "debtors": TraderService.get_debtors(db, trader.id) 
    }


@app.get("/api/dashboard/trader/{token}/transactions", response_model=TraderTransactionsResponse)
async def get_trader_transactions(
    token: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tx_type: str = Query(None, description="Filter by type: income, expense"),
    db: Session = Depends(get_db)
):
    """Get trader's transactions"""
    trader = TraderService.validate_dashboard_token(db, token)
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    query = db.query(Transaction).filter(Transaction.trader_id == trader.id)
    
    if tx_type and tx_type in ["income", "expense"]:
        query = query.filter(Transaction.type == tx_type)
    
    total = query.count()
    transactions = query.order_by(desc(Transaction.logged_at)).offset(offset).limit(limit).all()
    
    return {
        "trader_id": trader.id,
        "data": [
            {
                "id": tx.id,
                "type": tx.type,
                "amount": float(tx.amount),
                "category": tx.category,
                "description": tx.description,
                "logged_at": tx.logged_at.isoformat()
            }
            for tx in transactions
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }