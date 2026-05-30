from fastapi import FastAPI, Request, Depends, Query
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.rest import Client
import os
from dotenv import load_dotenv
from datetime import date
from src.csv_handler import handle_csv_upload
from src.models import get_db
from src.helpers import TraderService
from src.analytics import AnalyticsService
from src.schemas import (
    MetricsSummary, TransactionAnalytics, TransactionTrendResponse,
    CategoryDistributionResponse, UserGrowthResponse, TopTradersResponse,
    CreditScoreDistributionResponse, IncomeVsExpenseResponse,
    TransactionsResponse, TraderPerformance, PeriodComparisonResponse
)
from sqlalchemy.orm import Session 
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
# Dashboard API Endpoints
# ============================================================

@app.get("/api/metrics/summary", response_model=MetricsSummary)
async def get_metrics_summary(db: Session = Depends(get_db)):
    """Get overall KPI metrics"""
    return AnalyticsService.get_metrics_summary(db)


@app.get("/api/metrics/transactions", response_model=TransactionAnalytics)
async def get_transaction_metrics(
    period: str = Query("30d", description="Period: 7d, 30d, 90d, 1y"),
    category: str = Query("all", description="Category filter"),
    db: Session = Depends(get_db)
):
    """Get transaction analytics for a period"""
    return AnalyticsService.get_transaction_analytics(db, period, category if category != "all" else None)


@app.get("/api/analytics/transaction-trend", response_model=TransactionTrendResponse)
async def get_transaction_trend(
    period: str = Query("7d", description="Period: 7d, 30d, 90d, 1y"),
    group_by: str = Query("daily", description="Group by: daily, weekly, monthly"),
    db: Session = Depends(get_db)
):
    """Get transaction trends over time"""
    return AnalyticsService.get_transaction_trend(db, period, group_by)


@app.get("/api/analytics/category-distribution", response_model=CategoryDistributionResponse)
async def get_category_distribution(
    period: str = Query("30d", description="Period: 7d, 30d, 90d, 1y"),
    db: Session = Depends(get_db)
):
    """Get category distribution for income"""
    return AnalyticsService.get_category_distribution(db, period)


@app.get("/api/metrics/user-growth", response_model=UserGrowthResponse)
async def get_user_growth(
    period: str = Query("30d", description="Period: 7d, 30d, 90d, 1y"),
    group_by: str = Query("daily", description="Group by: daily, weekly"),
    db: Session = Depends(get_db)
):
    """Get user growth metrics"""
    return AnalyticsService.get_user_growth(db, period)


@app.get("/api/traders/top", response_model=TopTradersResponse)
async def get_top_traders(
    limit: int = Query(10, ge=1, le=100, description="Number of traders to return"),
    sort_by: str = Query("volume", description="Sort by: volume, score, streak"),
    period: str = Query("30d", description="Period: 7d, 30d, 90d, 1y"),
    db: Session = Depends(get_db)
):
    """Get top traders by various metrics"""
    return AnalyticsService.get_top_traders(db, limit, sort_by, period)


@app.get("/api/analytics/credit-score-distribution", response_model=CreditScoreDistributionResponse)
async def get_credit_score_distribution(db: Session = Depends(get_db)):
    """Get credit score distribution"""
    return AnalyticsService.get_credit_score_distribution(db)


@app.get("/api/analytics/income-vs-expense", response_model=IncomeVsExpenseResponse)
async def get_income_vs_expense(
    period: str = Query("7d", description="Period: 7d, 30d, 90d, 1y"),
    db: Session = Depends(get_db)
):
    """Get income vs expense comparison"""
    return AnalyticsService.get_income_vs_expense(db, period)


@app.get("/api/transactions/recent", response_model=TransactionsResponse)
async def get_recent_transactions(
    limit: int = Query(20, ge=1, le=100, description="Number of transactions to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    sort_by: str = Query("date", description="Sort by: date, amount"),
    order: str = Query("desc", description="Order: asc, desc"),
    db: Session = Depends(get_db)
):
    """Get recent transactions with pagination"""
    return AnalyticsService.get_recent_transactions(db, limit, offset, sort_by, order)


@app.get("/api/traders/{trader_id}/performance", response_model=TraderPerformance)
async def get_trader_performance(
    trader_id: int,
    period: str = Query("30d", description="Period: 7d, 30d, 90d, 1y"),
    db: Session = Depends(get_db)
):
    """Get individual trader performance metrics"""
    performance = AnalyticsService.get_trader_performance(db, trader_id, period)
    if not performance:
        return {"detail": "Trader not found"}, 404
    return performance


@app.get("/api/analytics/period-comparison", response_model=PeriodComparisonResponse)
async def get_period_comparison(
    current_period: str = Query("7d", description="Current period: 7d, 30d, 90d, 1y"),
    db: Session = Depends(get_db)
):
    """Compare current period with previous period"""
    return AnalyticsService.get_period_comparison(db, current_period)


@app.get("/api/transactions/search", response_model=TransactionsResponse)
async def search_transactions(
    tx_type: str = Query(None, description="Filter by type: income, expense"),
    category: str = Query(None, description="Filter by category"),
    min_amount: float = Query(None, description="Minimum amount"),
    max_amount: float = Query(None, description="Maximum amount"),
    start_date: date = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(None, description="End date (YYYY-MM-DD)"),
    trader_id: int = Query(None, description="Filter by trader ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Search and filter transactions"""
    return AnalyticsService.search_transactions(
        db, tx_type, category, min_amount, max_amount, start_date, end_date, trader_id, limit, offset
    )