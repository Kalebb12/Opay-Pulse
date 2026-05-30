from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


# ============================================================
# Metric Cards & Summary
# ============================================================

class MetricsSummary(BaseModel):
    """Overall KPI metrics"""
    total_traders: int
    active_traders_today: int
    total_transactions: int
    total_volume: float
    average_transaction: float
    average_credit_score: int


# ============================================================
# Transaction Analytics
# ============================================================

class TransactionAnalytics(BaseModel):
    """Transaction analytics for a period"""
    total: int
    income: float
    expense: float
    net: float
    success_rate: float
    categories: Dict[str, float]


# ============================================================
# Transaction Trend
# ============================================================

class DailyTransaction(BaseModel):
    """Daily transaction data"""
    date: str
    income: float
    expense: float
    net: float


class TransactionTrendResponse(BaseModel):
    """Transaction trend data"""
    data: List[DailyTransaction]


# ============================================================
# Category Distribution
# ============================================================

class CategoryData(BaseModel):
    """Category distribution data"""
    name: str
    value: float
    percentage: float


class CategoryDistributionResponse(BaseModel):
    """Category distribution response"""
    data: List[CategoryData]


# ============================================================
# User Growth
# ============================================================

class DailyGrowth(BaseModel):
    """Daily user growth data"""
    date: str
    new_traders: int
    active_traders: int
    cumulative: int


class UserGrowthResponse(BaseModel):
    """User growth response"""
    data: List[DailyGrowth]


# ============================================================
# Top Traders
# ============================================================

class TopTrader(BaseModel):
    """Top trader data"""
    rank: int
    trader_id: int
    phone_number: str
    total_volume: float
    transaction_count: int
    credit_score: int
    streak_count: int


class TopTradersResponse(BaseModel):
    """Top traders response"""
    data: List[TopTrader]


# ============================================================
# Credit Score Distribution
# ============================================================

class CreditScoreBucket(BaseModel):
    """Credit score distribution bucket"""
    range: str
    count: int


class CreditScoreDistributionResponse(BaseModel):
    """Credit score distribution response"""
    data: List[CreditScoreBucket]


# ============================================================
# Income vs Expense
# ============================================================

class IncomeExpenseData(BaseModel):
    """Daily income vs expense data"""
    date: str
    income: float
    expense: float


class IncomeVsExpenseResponse(BaseModel):
    """Income vs expense response"""
    data: List[IncomeExpenseData]


# ============================================================
# Transactions
# ============================================================

class TransactionData(BaseModel):
    """Transaction data"""
    id: int
    trader_id: int
    trader_phone: str
    type: str
    amount: float
    category: str
    description: Optional[str]
    logged_at: str


class TransactionsResponse(BaseModel):
    """Transactions response with pagination"""
    data: List[TransactionData]
    total: int
    limit: int
    offset: int


# ============================================================
# Trader Performance
# ============================================================

class TraderPerformance(BaseModel):
    """Trader performance metrics"""
    trader_id: int
    phone_number: str
    total_transactions: int
    total_volume: float
    average_transaction: float
    income_transactions: int
    expense_transactions: int
    income_total: float
    expense_total: float
    credit_score: int
    streak_count: int
    joined_date: str


# ============================================================
# Period Comparison
# ============================================================

class PeriodStats(BaseModel):
    """Statistics for a period"""
    transactions: int
    volume: float
    average_transaction: float


class PeriodChange(BaseModel):
    """Change percentages"""
    transactions: float
    volume: float
    average_transaction: float


class PeriodComparisonResponse(BaseModel):
    """Period comparison response"""
    current_period: PeriodStats
    previous_period: PeriodStats
    change: PeriodChange


# ============================================================
# Error Responses
# ============================================================

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    status_code: int
