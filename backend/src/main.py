from fastapi import FastAPI, Request, Depends, Query, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.rest import Client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from src.csv_handler import handle_csv_upload
from src.models import get_db, Trader, Transaction
from src.helpers import TraderService
from src.schemas import (
    TraderProfileResponse, TraderTransactionsResponse, TraderStatsResponse,
    TraderRankingResponse, TransactionData, ErrorResponse
)
from sqlalchemy.orm import Session 
from sqlalchemy import desc, func
from src.agent import run_agent

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
    media_url = form_data.get("MediaUrl")

    trader = TraderService.get_or_create_trader(db, incoming_phone)

    if media_url:
        reply = await handle_csv_upload(db, trader, media_url)
    else:
        reply = run_agent(db, trader, incoming_message)

    send_whatsapp_message(incoming_phone, reply)
    return Response("OK", status_code=200)


def send_whatsapp_message(to_number: str, message_body: str):
    """
    Send a WhatsApp message via Twilio
    """
    try:
        message = client.messages.create(
            from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
            body=message_body,
            to={to_number}
        )
        print(f"Message sent: {message.sid}")
        return message.sid
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return None


# ============================================================
# Trader Dashboard API Endpoints
# ============================================================

@app.get("/api/dashboard/trader/{trader_id}", response_model=TraderProfileResponse)
async def get_trader_profile(trader_id: int, db: Session = Depends(get_db)):
    """Get trader profile information"""
    trader = db.query(Trader).filter(Trader.id == trader_id).first()
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    return {
        "trader_id": trader.id,
        "phone_number": trader.phone_number,
        "credit_score": trader.credit_score or 0,
        "streak_count": trader.streak_count,
        "joined_date": trader.created_at.isoformat(),
        "last_active": trader.last_log_date.isoformat() if trader.last_log_date else None
    }


@app.get("/api/dashboard/trader/{trader_id}/transactions", response_model=TraderTransactionsResponse)
async def get_trader_transactions(
    trader_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tx_type: str = Query(None, description="Filter by type: income, expense"),
    db: Session = Depends(get_db)
):
    """Get trader's transactions"""
    trader = db.query(Trader).filter(Trader.id == trader_id).first()
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    query = db.query(Transaction).filter(Transaction.trader_id == trader_id)
    
    if tx_type and tx_type in ["income", "expense"]:
        query = query.filter(Transaction.type == tx_type)
    
    total = query.count()
    transactions = query.order_by(desc(Transaction.logged_at)).offset(offset).limit(limit).all()
    
    return {
        "trader_id": trader_id,
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


@app.get("/api/dashboard/trader/{trader_id}/stats", response_model=TraderStatsResponse)
async def get_trader_stats(
    trader_id: int,
    period: str = Query("30d", description="Period: 7d, 30d, 90d, 1y"),
    db: Session = Depends(get_db)
):
    """Get trader's statistics for a period"""
    trader = db.query(Trader).filter(Trader.id == trader_id).first()
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    # Parse period
    today = datetime.now().date()
    if period == "7d":
        start = today - timedelta(days=7)
    elif period == "30d":
        start = today - timedelta(days=30)
    elif period == "90d":
        start = today - timedelta(days=90)
    elif period == "1y":
        start = today - timedelta(days=365)
    else:
        start = today - timedelta(days=30)
    
    # Query transactions within period
    transactions = db.query(Transaction).filter(
        Transaction.trader_id == trader_id,
        Transaction.logged_at >= datetime.combine(start, datetime.min.time())
    ).all()
    
    income_txs = [tx for tx in transactions if tx.type == "income"]
    expense_txs = [tx for tx in transactions if tx.type == "expense"]
    
    total_income = sum(float(tx.amount) for tx in income_txs)
    total_expense = sum(float(tx.amount) for tx in expense_txs)
    
    return {
        "trader_id": trader_id,
        "period": period,
        "total_transactions": len(transactions),
        "income_transactions": len(income_txs),
        "expense_transactions": len(expense_txs),
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": total_income - total_expense,
        "average_transaction": (total_income + total_expense) / len(transactions) if transactions else 0
    }


@app.get("/api/dashboard/traders/ranking", response_model=TraderRankingResponse)
async def get_traders_ranking(
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("volume", description="Sort by: volume, credit_score, transactions"),
    db: Session = Depends(get_db)
):
    """Get top traders ranking"""
    traders = db.query(Trader).all()
    
    # Calculate stats for each trader
    traders_with_stats = []
    for trader in traders:
        tx_count = db.query(func.count(Transaction.id)).filter(
            Transaction.trader_id == trader.id
        ).scalar() or 0
        
        total_volume = db.query(func.sum(Transaction.amount)).filter(
            Transaction.trader_id == trader.id
        ).scalar() or 0
        
        traders_with_stats.append({
            "trader_id": trader.id,
            "phone_number": trader.phone_number,
            "credit_score": trader.credit_score or 0,
            "total_volume": float(total_volume),
            "transaction_count": tx_count,
            "streak_count": trader.streak_count
        })
    
    # Sort based on parameter
    if sort_by == "volume":
        traders_with_stats.sort(key=lambda x: x["total_volume"], reverse=True)
    elif sort_by == "credit_score":
        traders_with_stats.sort(key=lambda x: x["credit_score"], reverse=True)
    else:  # transactions
        traders_with_stats.sort(key=lambda x: x["transaction_count"], reverse=True)
    
    # Add rank
    ranked = [
        {**trader, "rank": idx + 1}
        for idx, trader in enumerate(traders_with_stats[:limit])
    ]
    
    return {
        "data": ranked,
        "sort_by": sort_by,
        "total_traders": len(traders),
        "returned": len(ranked)
    }
