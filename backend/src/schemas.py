from pydantic import BaseModel
from typing import List, Optional


# ============================================================
# Trader Profile
# ============================================================

class TraderProfileResponse(BaseModel):
    """Trader profile information"""
    trader_id: int
    phone_number: str
    credit_score: int
    streak_count: int
    joined_date: str
    last_active: Optional[str]


# ============================================================
# Transaction Data
# ============================================================

class TransactionData(BaseModel):
    """Transaction data"""
    id: int
    type: str
    amount: float
    category: str
    description: Optional[str]
    logged_at: str


class TraderTransactionsResponse(BaseModel):
    """Trader transactions response with pagination"""
    trader_id: int
    data: List[TransactionData]
    total: int
    limit: int
    offset: int


# ============================================================
# Trader Statistics
# ============================================================

class TraderStatsResponse(BaseModel):
    """Trader statistics for a period"""
    trader_id: int
    period: str
    total_transactions: int
    income_transactions: int
    expense_transactions: int
    total_income: float
    total_expense: float
    net_balance: float
    average_transaction: float


# ============================================================
# Trader Ranking
# ============================================================

class RankedTrader(BaseModel):
    """Ranked trader data"""
    rank: int
    trader_id: int
    phone_number: str
    credit_score: int
    total_volume: float
    transaction_count: int
    streak_count: int


class TraderRankingResponse(BaseModel):
    """Traders ranking response"""
    data: List[RankedTrader]
    sort_by: str
    total_traders: int
    returned: int


# ============================================================
# Error Responses
# ============================================================

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    status_code: int

