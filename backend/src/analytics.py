from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from src.models import Trader, Transaction
from datetime import date, datetime, timedelta
from typing import List, Dict, Tuple


class AnalyticsService:
    """Service for dashboard analytics queries"""

    # ============================================================
    # Helper Methods
    # ============================================================

    @staticmethod
    def get_date_range(period: str = "30d") -> Tuple[date, date]:
        """Parse period string and return start and end dates"""
        today = date.today()
        
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
        
        return start, today

    @staticmethod
    def get_previous_date_range(period: str = "30d") -> Tuple[date, date]:
        """Get the previous period for comparison"""
        today = date.today()
        
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        elif period == "1y":
            days = 365
        else:
            days = 30
        
        end = today - timedelta(days=days)
        start = end - timedelta(days=days)
        return start, end

    # ============================================================
    # Key Metrics Summary
    # ============================================================

    @staticmethod
    def get_metrics_summary(db: Session) -> dict:
        """Get overall KPI metrics"""
        today = date.today()
        week_start = today - timedelta(days=7)
        
        total_traders = db.query(func.count(Trader.id)).scalar() or 0
        
        active_traders_today = db.query(func.count(Trader.id)).filter(
            Trader.last_log_date >= datetime.combine(today, datetime.min.time())
        ).scalar() or 0
        
        total_transactions = db.query(func.count(Transaction.id)).scalar() or 0
        
        total_volume = db.query(func.sum(Transaction.amount)).scalar() or 0
        
        avg_transaction = db.query(func.avg(Transaction.amount)).scalar() or 0
        
        avg_score = db.query(func.avg(Trader.credit_score)).scalar() or 0
        
        return {
            "total_traders": int(total_traders),
            "active_traders_today": int(active_traders_today),
            "total_transactions": int(total_transactions),
            "total_volume": float(total_volume),
            "average_transaction": float(avg_transaction) if avg_transaction else 0,
            "average_credit_score": int(avg_score) if avg_score else 0
        }

    # ============================================================
    # Transaction Analytics
    # ============================================================

    @staticmethod
    def get_transaction_analytics(db: Session, period: str = "30d", category: str = None) -> dict:
        """Get transaction analytics for a period"""
        start, end = AnalyticsService.get_date_range(period)
        
        query = db.query(Transaction).filter(
            Transaction.logged_at >= datetime.combine(start, datetime.min.time()),
            Transaction.logged_at <= datetime.combine(end, datetime.max.time())
        )
        
        if category and category != "all":
            query = query.filter(Transaction.category == category)
        
        transactions = query.all()
        
        total_count = len(transactions)
        income_total = sum(t.amount for t in transactions if t.type == "income")
        expense_total = sum(t.amount for t in transactions if t.type == "expense")
        net = income_total - expense_total
        
        # Calculate success rate (assuming all logged transactions are successful)
        success_rate = 100.0 if total_count > 0 else 0
        
        # Category breakdown
        categories = {}
        for tx in transactions:
            if tx.category not in categories:
                categories[tx.category] = 0
            if tx.type == "income":
                categories[tx.category] += float(tx.amount)
        
        return {
            "total": total_count,
            "income": float(income_total),
            "expense": float(expense_total),
            "net": float(net),
            "success_rate": success_rate,
            "categories": categories
        }

    # ============================================================
    # Transaction Trend
    # ============================================================

    @staticmethod
    def get_transaction_trend(db: Session, period: str = "7d", group_by: str = "daily") -> dict:
        """Get transaction trends over time"""
        start, end = AnalyticsService.get_date_range(period)
        
        transactions = db.query(Transaction).filter(
            Transaction.logged_at >= datetime.combine(start, datetime.min.time()),
            Transaction.logged_at <= datetime.combine(end, datetime.max.time())
        ).all()
        
        # Group transactions by date
        daily_data = {}
        current = start
        while current <= end:
            daily_data[current.isoformat()] = {"income": 0, "expense": 0, "net": 0}
            current += timedelta(days=1)
        
        # Aggregate transactions
        for tx in transactions:
            tx_date = tx.logged_at.date()
            if tx_date.isoformat() in daily_data:
                if tx.type == "income":
                    daily_data[tx_date.isoformat()]["income"] += float(tx.amount)
                else:
                    daily_data[tx_date.isoformat()]["expense"] += float(tx.amount)
        
        # Calculate net for each day
        for date_str in daily_data:
            daily_data[date_str]["net"] = daily_data[date_str]["income"] - daily_data[date_str]["expense"]
        
        data = [
            {
                "date": date_str,
                "income": values["income"],
                "expense": values["expense"],
                "net": values["net"]
            }
            for date_str, values in sorted(daily_data.items())
        ]
        
        return {"data": data}

    # ============================================================
    # Category Distribution
    # ============================================================

    @staticmethod
    def get_category_distribution(db: Session, period: str = "30d") -> dict:
        """Get category distribution"""
        start, end = AnalyticsService.get_date_range(period)
        
        transactions = db.query(Transaction).filter(
            Transaction.logged_at >= datetime.combine(start, datetime.min.time()),
            Transaction.logged_at <= datetime.combine(end, datetime.max.time()),
            Transaction.type == "income"
        ).all()
        
        categories = {}
        total_income = 0
        
        for tx in transactions:
            category = tx.category or "Other"
            amount = float(tx.amount)
            categories[category] = categories.get(category, 0) + amount
            total_income += amount
        
        # Convert to list with percentages
        data = []
        for category, value in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (value / total_income * 100) if total_income > 0 else 0
            data.append({
                "name": category,
                "value": value,
                "percentage": round(percentage, 1)
            })
        
        return {"data": data}

    # ============================================================
    # User Growth Metrics
    # ============================================================

    @staticmethod
    def get_user_growth(db: Session, period: str = "30d") -> dict:
        """Get user growth metrics"""
        start, end = AnalyticsService.get_date_range(period)
        
        all_traders = db.query(Trader).all()
        
        # Group traders by creation date
        daily_data = {}
        current = start
        while current <= end:
            daily_data[current.isoformat()] = {"new_traders": 0, "active_traders": 0}
            current += timedelta(days=1)
        
        # Count new traders per day
        for trader in all_traders:
            created_date = trader.created_at.date()
            if start <= created_date <= end:
                daily_data[created_date.isoformat()]["new_traders"] += 1
        
        # Count active traders per day
        transactions = db.query(Transaction).filter(
            Transaction.logged_at >= datetime.combine(start, datetime.min.time()),
            Transaction.logged_at <= datetime.combine(end, datetime.max.time())
        ).all()
        
        active_traders_per_day = {}
        for tx in transactions:
            tx_date = tx.logged_at.date()
            if tx_date.isoformat() not in active_traders_per_day:
                active_traders_per_day[tx_date.isoformat()] = set()
            active_traders_per_day[tx_date.isoformat()].add(tx.trader_id)
        
        for date_str, trader_ids in active_traders_per_day.items():
            if date_str in daily_data:
                daily_data[date_str]["active_traders"] = len(trader_ids)
        
        # Calculate cumulative
        cumulative = 0
        data = []
        for date_str in sorted(daily_data.keys()):
            cumulative += daily_data[date_str]["new_traders"]
            data.append({
                "date": date_str,
                "new_traders": daily_data[date_str]["new_traders"],
                "active_traders": daily_data[date_str]["active_traders"],
                "cumulative": cumulative
            })
        
        return {"data": data}

    # ============================================================
    # Top Traders
    # ============================================================

    @staticmethod
    def get_top_traders(
        db: Session,
        limit: int = 10,
        sort_by: str = "volume",
        period: str = "30d"
    ) -> dict:
        """Get top traders by various metrics"""
        start, end = AnalyticsService.get_date_range(period)
        
        transactions = db.query(Transaction).filter(
            Transaction.logged_at >= datetime.combine(start, datetime.min.time()),
            Transaction.logged_at <= datetime.combine(end, datetime.max.time())
        ).all()
        
        # Aggregate trader metrics
        trader_metrics = {}
        for tx in transactions:
            if tx.trader_id not in trader_metrics:
                trader_metrics[tx.trader_id] = {
                    "total_volume": 0,
                    "transaction_count": 0,
                    "transactions": []
                }
            if tx.type == "income":
                trader_metrics[tx.trader_id]["total_volume"] += float(tx.amount)
            trader_metrics[tx.trader_id]["transaction_count"] += 1
            trader_metrics[tx.trader_id]["transactions"].append(tx)
        
        # Enrich with trader data
        data = []
        for rank, (trader_id, metrics) in enumerate(sorted(
            trader_metrics.items(),
            key=lambda x: x[1]["total_volume"] if sort_by == "volume" else x[1]["transaction_count"],
            reverse=True
        )[:limit]):
            trader = db.query(Trader).filter(Trader.id == trader_id).first()
            if trader:
                data.append({
                    "rank": rank + 1,
                    "trader_id": trader_id,
                    "phone_number": trader.phone_number,
                    "total_volume": metrics["total_volume"],
                    "transaction_count": metrics["transaction_count"],
                    "credit_score": trader.credit_score or 0,
                    "streak_count": trader.streak_count or 0
                })
        
        return {"data": data}

    # ============================================================
    # Credit Score Distribution
    # ============================================================

    @staticmethod
    def get_credit_score_distribution(db: Session) -> dict:
        """Get distribution of credit scores"""
        traders = db.query(Trader).filter(Trader.credit_score != None).all()
        
        # Define score buckets
        buckets = {
            "300-400": 0,
            "400-500": 0,
            "500-600": 0,
            "600-700": 0,
            "700-800": 0,
            "800-900": 0,
            "900+": 0
        }
        
        for trader in traders:
            score = trader.credit_score
            if score < 400:
                buckets["300-400"] += 1
            elif score < 500:
                buckets["400-500"] += 1
            elif score < 600:
                buckets["500-600"] += 1
            elif score < 700:
                buckets["600-700"] += 1
            elif score < 800:
                buckets["700-800"] += 1
            elif score < 900:
                buckets["800-900"] += 1
            else:
                buckets["900+"] += 1
        
        data = [
            {"range": range_str, "count": count}
            for range_str, count in buckets.items()
        ]
        
        return {"data": data}

    # ============================================================
    # Income vs Expense Comparison
    # ============================================================

    @staticmethod
    def get_income_vs_expense(db: Session, period: str = "7d") -> dict:
        """Get income vs expense comparison"""
        start, end = AnalyticsService.get_date_range(period)
        
        transactions = db.query(Transaction).filter(
            Transaction.logged_at >= datetime.combine(start, datetime.min.time()),
            Transaction.logged_at <= datetime.combine(end, datetime.max.time())
        ).all()
        
        # Group by date
        daily_data = {}
        current = start
        while current <= end:
            daily_data[current.isoformat()] = {"income": 0, "expense": 0}
            current += timedelta(days=1)
        
        # Aggregate
        for tx in transactions:
            tx_date = tx.logged_at.date()
            if tx_date.isoformat() in daily_data:
                if tx.type == "income":
                    daily_data[tx_date.isoformat()]["income"] += float(tx.amount)
                else:
                    daily_data[tx_date.isoformat()]["expense"] += float(tx.amount)
        
        data = [
            {
                "date": date_str,
                "income": values["income"],
                "expense": values["expense"]
            }
            for date_str, values in sorted(daily_data.items())
        ]
        
        return {"data": data}

    # ============================================================
    # Recent Transactions
    # ============================================================

    @staticmethod
    def get_recent_transactions(
        db: Session,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "date",
        order: str = "desc"
    ) -> dict:
        """Get recent transactions with pagination"""
        query = db.query(Transaction)
        
        if sort_by == "date":
            if order == "desc":
                query = query.order_by(desc(Transaction.logged_at))
            else:
                query = query.order_by(Transaction.logged_at)
        elif sort_by == "amount":
            if order == "desc":
                query = query.order_by(desc(Transaction.amount))
            else:
                query = query.order_by(Transaction.amount)
        
        total = query.count()
        transactions = query.offset(offset).limit(limit).all()
        
        data = []
        for tx in transactions:
            trader = db.query(Trader).filter(Trader.id == tx.trader_id).first()
            data.append({
                "id": tx.id,
                "trader_id": tx.trader_id,
                "trader_phone": trader.phone_number if trader else "Unknown",
                "type": tx.type,
                "amount": float(tx.amount),
                "category": tx.category,
                "description": tx.description,
                "logged_at": tx.logged_at.isoformat()
            })
        
        return {
            "data": data,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    # ============================================================
    # Trader Performance
    # ============================================================

    @staticmethod
    def get_trader_performance(db: Session, trader_id: int, period: str = "30d") -> dict:
        """Get individual trader performance metrics"""
        start, end = AnalyticsService.get_date_range(period)
        
        trader = db.query(Trader).filter(Trader.id == trader_id).first()
        if not trader:
            return None
        
        transactions = db.query(Transaction).filter(
            Transaction.trader_id == trader_id,
            Transaction.logged_at >= datetime.combine(start, datetime.min.time()),
            Transaction.logged_at <= datetime.combine(end, datetime.max.time())
        ).all()
        
        income_txs = [t for t in transactions if t.type == "income"]
        expense_txs = [t for t in transactions if t.type == "expense"]
        
        income_total = sum(t.amount for t in income_txs)
        expense_total = sum(t.amount for t in expense_txs)
        
        return {
            "trader_id": trader_id,
            "phone_number": trader.phone_number,
            "total_transactions": len(transactions),
            "total_volume": float(income_total + expense_total),
            "average_transaction": float(sum(t.amount for t in transactions) / len(transactions)) if transactions else 0,
            "income_transactions": len(income_txs),
            "expense_transactions": len(expense_txs),
            "income_total": float(income_total),
            "expense_total": float(expense_total),
            "credit_score": trader.credit_score or 0,
            "streak_count": trader.streak_count or 0,
            "joined_date": trader.created_at.isoformat()
        }

    # ============================================================
    # Period Comparison
    # ============================================================

    @staticmethod
    def get_period_comparison(db: Session, current_period: str = "7d") -> dict:
        """Compare current period with previous period"""
        current_start, current_end = AnalyticsService.get_date_range(current_period)
        prev_start, prev_end = AnalyticsService.get_previous_date_range(current_period)
        
        def get_period_stats(start, end):
            txs = db.query(Transaction).filter(
                Transaction.logged_at >= datetime.combine(start, datetime.min.time()),
                Transaction.logged_at <= datetime.combine(end, datetime.max.time())
            ).all()
            
            income = sum(t.amount for t in txs if t.type == "income")
            total = sum(t.amount for t in txs)
            
            return {
                "transactions": len(txs),
                "volume": float(income),
                "average_transaction": float(total / len(txs)) if txs else 0
            }
        
        current = get_period_stats(current_start, current_end)
        previous = get_period_stats(prev_start, prev_end)
        
        # Calculate changes
        tx_change = ((current["transactions"] - previous["transactions"]) / previous["transactions"] * 100) if previous["transactions"] > 0 else 0
        volume_change = ((current["volume"] - previous["volume"]) / previous["volume"] * 100) if previous["volume"] > 0 else 0
        avg_change = ((current["average_transaction"] - previous["average_transaction"]) / previous["average_transaction"] * 100) if previous["average_transaction"] > 0 else 0
        
        return {
            "current_period": current,
            "previous_period": previous,
            "change": {
                "transactions": round(tx_change, 1),
                "volume": round(volume_change, 1),
                "average_transaction": round(avg_change, 1)
            }
        }

    # ============================================================
    # Search & Filter Transactions
    # ============================================================

    @staticmethod
    def search_transactions(
        db: Session,
        tx_type: str = None,
        category: str = None,
        min_amount: float = None,
        max_amount: float = None,
        start_date: date = None,
        end_date: date = None,
        trader_id: int = None,
        limit: int = 20,
        offset: int = 0
    ) -> dict:
        """Search and filter transactions"""
        query = db.query(Transaction)
        
        if tx_type and tx_type != "all":
            query = query.filter(Transaction.type == tx_type)
        
        if category and category != "all":
            query = query.filter(Transaction.category == category)
        
        if min_amount is not None:
            query = query.filter(Transaction.amount >= min_amount)
        
        if max_amount is not None:
            query = query.filter(Transaction.amount <= max_amount)
        
        if start_date:
            query = query.filter(Transaction.logged_at >= datetime.combine(start_date, datetime.min.time()))
        
        if end_date:
            query = query.filter(Transaction.logged_at <= datetime.combine(end_date, datetime.max.time()))
        
        if trader_id:
            query = query.filter(Transaction.trader_id == trader_id)
        
        total = query.count()
        transactions = query.order_by(desc(Transaction.logged_at)).offset(offset).limit(limit).all()
        
        data = []
        for tx in transactions:
            trader = db.query(Trader).filter(Trader.id == tx.trader_id).first()
            data.append({
                "id": tx.id,
                "trader_id": tx.trader_id,
                "trader_phone": trader.phone_number if trader else "Unknown",
                "type": tx.type,
                "amount": float(tx.amount),
                "category": tx.category,
                "description": tx.description,
                "logged_at": tx.logged_at.isoformat()
            })
        
        return {
            "data": data,
            "total": total,
            "limit": limit,
            "offset": offset
        }
