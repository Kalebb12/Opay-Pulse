from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models import CreditSale, Trader, Transaction, DashboardToken
from datetime import date, datetime, timedelta
import secrets

class TraderService:

    # ============================================================
    # Trader Management
    # ============================================================

    @staticmethod
    def get_or_create_trader(db: Session, phone_number: str):
        clean_phone = phone_number.replace("whatsapp:", "")

        trader = db.query(Trader).filter(
            Trader.phone_number == clean_phone
        ).first()

        if not trader:
            trader = Trader(
                phone_number=clean_phone,
                created_at=datetime.now(),
                streak_count=0
            )
            db.add(trader)
            db.commit()
            db.refresh(trader)
            print(f"✅ New trader: {clean_phone}")
        else:
            print(f"✅ Existing trader: {clean_phone}")

        return trader

    @staticmethod
    def update_streak(db: Session, trader_id: int):
        trader = db.query(Trader).filter(Trader.id == trader_id).first()

        if not trader:
            return

        today = date.today()
        last_log = trader.last_log_date.date() if trader.last_log_date else None

        if last_log != today:
            trader.streak_count += 1
            trader.last_log_date = datetime.now()
            db.commit()
            print(f"🔥 Streak updated: {trader.streak_count}")

    # ============================================================
    # Transactions
    # ============================================================

    @staticmethod
    def add_transaction(
        db: Session,
        trader_id: int,
        tx_type: str,
        amount: float,
        category: str,
        description: str = None
    ):
        tx = Transaction(
            trader_id=trader_id,
            type=tx_type,
            amount=amount,
            category=category,
            description=description,
            logged_at=datetime.now()
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def get_last_transaction(db: Session, trader_id: int):
        return db.query(Transaction).filter(
            Transaction.trader_id == trader_id
        ).order_by(Transaction.logged_at.desc()).first()

    @staticmethod
    def delete_transaction(db: Session, transaction_id: int, trader_id: int):
        tx = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.trader_id == trader_id
        ).first()

        if tx:
            db.delete(tx)
            db.commit()
            return True

        return False

    # ============================================================
    # Summaries
    # ============================================================

    @staticmethod
    def get_today_total(db: Session, trader_id: int) -> dict:
        today = date.today()

        income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.trader_id == trader_id,
            Transaction.type == "income",
            func.date(Transaction.logged_at) == today
        ).scalar() or 0

        expense = db.query(func.sum(Transaction.amount)).filter(
            Transaction.trader_id == trader_id,
            Transaction.type == "expense",
            func.date(Transaction.logged_at) == today
        ).scalar() or 0

        return {
            "income": float(income),
            "expense": float(expense),
            "profit": float(income - expense)
        }

    @staticmethod
    def get_week_summary(db: Session, trader_id: int) -> dict:
        week_start = date.today() - timedelta(days=7)
        prev_week_start = week_start - timedelta(days=7)

        def query_period(start, end):
            income = db.query(func.sum(Transaction.amount)).filter(
                Transaction.trader_id == trader_id,
                Transaction.type == "income",
                func.date(Transaction.logged_at) >= start,
                func.date(Transaction.logged_at) < end
            ).scalar() or 0

            expense = db.query(func.sum(Transaction.amount)).filter(
                Transaction.trader_id == trader_id,
                Transaction.type == "expense",
                func.date(Transaction.logged_at) >= start,
                func.date(Transaction.logged_at) < end
            ).scalar() or 0

            return float(income), float(expense)

        income, expense = query_period(week_start, date.today())
        prev_income, _ = query_period(prev_week_start, week_start)

        profit = income - expense
        margin = (profit / income * 100) if income > 0 else 0
        growth = ((income - prev_income) / prev_income * 100) if prev_income > 0 else 0

        return {
            "income": income,
            "expense": expense,
            "profit": profit,
            "margin": round(margin, 1),
            "growth": round(growth, 1),
            "period": "week"
        }

    @staticmethod
    def get_month_summary(db: Session, trader_id: int) -> dict:
        today = date.today()
        month_start = today.replace(day=1)

        # Previous month
        if month_start.month == 1:
            prev_month_start = month_start.replace(year=month_start.year - 1, month=12)
        else:
            prev_month_start = month_start.replace(month=month_start.month - 1)

        def query_period(start, end):
            income = db.query(func.sum(Transaction.amount)).filter(
                Transaction.trader_id == trader_id,
                Transaction.type == "income",
                func.date(Transaction.logged_at) >= start,
                func.date(Transaction.logged_at) < end
            ).scalar() or 0

            expense = db.query(func.sum(Transaction.amount)).filter(
                Transaction.trader_id == trader_id,
                Transaction.type == "expense",
                func.date(Transaction.logged_at) >= start,
                func.date(Transaction.logged_at) < end
            ).scalar() or 0

            return float(income), float(expense)

        income, expense = query_period(month_start, today)
        prev_income, _ = query_period(prev_month_start, month_start)

        profit = income - expense
        margin = (profit / income * 100) if income > 0 else 0
        growth = ((income - prev_income) / prev_income * 100) if prev_income > 0 else 0

        return {
            "income": income,
            "expense": expense,
            "profit": profit,
            "margin": round(margin, 1),
            "growth": round(growth, 1),
            "period": "month"
        }

    # ============================================================
    # Credit Scoring
    # ============================================================

    @staticmethod
    def calculate_credit_score(db: Session, trader_id: int, opay_data: dict) -> int:
        trader = db.query(Trader).filter(Trader.id == trader_id).first()

        # Component 1: Streak consistency (max 200 pts)
        streak_score = min((trader.streak_count / 30) * 200, 200)

        # Component 2: Income consistency from OPay data (max 250 pts)
        std_dev = opay_data.get("income_std_dev", 0)
        consistency_score = max(250 - std_dev * 2, 0)

        # Component 3: Profit margin from trader logs (max 200 pts)
        month_data = TraderService.get_month_summary(db, trader_id)
        margin = month_data.get("margin", 0)
        margin_score = min(margin * 4, 200)

        # Component 4: Transaction volume from OPay data (max 200 pts)
        monthly_avg = opay_data.get("monthly_avg_income", 0)
        volume_score = min((monthly_avg / 500000) * 200, 200)

        total = streak_score + consistency_score + margin_score + volume_score
        score = int(300 + (total / 850 * 550))

        return max(300, min(score, 850))

    @staticmethod
    def save_credit_score(db: Session, trader_id: int, score: int):
        trader = db.query(Trader).filter(Trader.id == trader_id).first()
        if trader:
            trader.credit_score = score
            db.commit()

    @staticmethod
    def match_lenders(credit_score: int, monthly_income: float) -> list:
        loan_amount = monthly_income * 0.6

        if credit_score >= 700:
            return [
                {"lender": "Carbon", "amount": loan_amount, "rate": "6% monthly", "tenure": "6 months"},
                {"lender": "FairMoney", "amount": loan_amount * 0.8, "rate": "7% monthly", "tenure": "3 months"},
            ]
        elif credit_score >= 600:
            return [
                {"lender": "FairMoney", "amount": loan_amount * 0.7, "rate": "8% monthly", "tenure": "3 months"},
            ]
        elif credit_score >= 500:
            return [
                {"lender": "Paylater", "amount": loan_amount * 0.5, "rate": "10% monthly", "tenure": "2 months"},
            ]

        return []
    
    @staticmethod
    def generate_dashboard_token(db: Session, trader_id: int) -> str:
        # Invalidate any existing unused tokens for this trader
        db.query(DashboardToken).filter(
            DashboardToken.trader_id == trader_id,
            DashboardToken.used == False
        ).delete()
        db.commit()

        # Generate new token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=10)

        db_token = DashboardToken(
            trader_id=trader_id,
            token=token,
            expires_at=expires_at
        )
        db.add(db_token)
        db.commit()

        return token

    @staticmethod
    def get_daily_chart_data(db: Session, trader_id: int, days: int = 30) -> list:
        """
        Returns last N days of daily income/expense/profit.
        Used by the dashboard chart.
        """
        daily_data = []

        for i in range(days - 1, -1, -1):
            day = date.today() - timedelta(days=i)

            income = db.query(func.sum(Transaction.amount)).filter(
                Transaction.trader_id == trader_id,
                Transaction.type == "income",
                func.date(Transaction.logged_at) == day
            ).scalar() or 0

            expense = db.query(func.sum(Transaction.amount)).filter(
                Transaction.trader_id == trader_id,
                Transaction.type == "expense",
                func.date(Transaction.logged_at) == day
            ).scalar() or 0

            daily_data.append({
                "date": day.strftime("%d %b"),
                "income": float(income),
                "expense": float(expense),
                "profit": float(income - expense)
            })

        return daily_data
    
    
    @staticmethod
    def validate_dashboard_token(db: Session, token: str):
        """
        Returns trader if token is valid, None if invalid or expired.
        """
        db_token = db.query(DashboardToken).filter(
            DashboardToken.token == token,
            DashboardToken.used == False
        ).first()

        if not db_token:
            return None

        # Check expiry
        if datetime.now() > db_token.expires_at:
            db.delete(db_token)
            db.commit()
            return None

        # Mark token as used
        # db_token.used = True
        # db.commit()

        # Return the trader
        trader = db.query(Trader).filter(
            Trader.id == db_token.trader_id
        ).first()

        return trader

    

    @staticmethod
    def get_trader_dashboard_data(db: Session, trader_id: int) -> dict:
        """All data needed for the dashboard"""
        trader = db.query(Trader).filter(Trader.id == trader_id).first()

        week = TraderService.get_week_summary(db, trader_id)
        month = TraderService.get_month_summary(db, trader_id)
        today = TraderService.get_today_total(db, trader_id)

        # Last 30 days of daily totals for chart
        daily_data = []
        for i in range(29, -1, -1):
            day = date.today() - timedelta(days=i)

            income = db.query(func.sum(Transaction.amount)).filter(
                Transaction.trader_id == trader_id,
                Transaction.type == "income",
                func.date(Transaction.logged_at) == day
            ).scalar() or 0

            expense = db.query(func.sum(Transaction.amount)).filter(
                Transaction.trader_id == trader_id,
                Transaction.type == "expense",
                func.date(Transaction.logged_at) == day
            ).scalar() or 0

            daily_data.append({
                "date": day.strftime("%d %b"),
                "income": float(income),
                "expense": float(expense),
                "profit": float(income - expense)
            })

        return {
            "trader": {
                "phone": trader.phone_number,
                "streak": trader.streak_count,
                "credit_score": trader.credit_score,
                "member_since": trader.created_at.strftime("%B %Y")
            },
            "today": today,
            "week": week,
            "month": month,
            "chart_data": daily_data
        }

    @staticmethod
    def log_credit_sale(
        db: Session,
        trader_id: int,
        customer_name: str,
        amount: float,
        due_date_str: str = "",
        notes: str = ""
    ):
        # Parse due date if provided
        due_date = None
        if due_date_str:
            try:
                from dateutil import parser as date_parser
                due_date = date_parser.parse(due_date_str, fuzzy=True)
            except:
                pass  # No due date if unparseable

        # Check if customer already has an outstanding balance
        existing = db.query(CreditSale).filter(
            CreditSale.trader_id == trader_id,
            CreditSale.customer_name.ilike(customer_name),
            CreditSale.status.in_(["outstanding", "partially_paid"])
        ).first()

        if existing:
            # Add to existing debt
            existing.amount_owed = float(existing.amount_owed) + amount
            existing.updated_at = datetime.now()
            if due_date:
                existing.due_date = due_date
            db.commit()
            return existing
        else:
            credit = CreditSale(
                trader_id=trader_id,
                customer_name=customer_name.strip().title(),
                amount_owed=amount,
                amount_paid=0,
                due_date=due_date,
                notes=notes,
                status="outstanding"
            )
            db.add(credit)
            db.commit()
            db.refresh(credit)
            return credit


    @staticmethod
    def log_credit_payment(
        db: Session,
        trader_id: int,
        customer_name: str,
        amount_paid: float
    ):
        # Find their most recent outstanding debt
        credit = db.query(CreditSale).filter(
            CreditSale.trader_id == trader_id,
            CreditSale.customer_name.ilike(f"%{customer_name}%"),
            CreditSale.status.in_(["outstanding", "partially_paid"])
        ).order_by(CreditSale.created_at.desc()).first()

        if not credit:
            return {"found": False, "customer": customer_name}

        credit.amount_paid = float(credit.amount_paid) + amount_paid
        credit.updated_at = datetime.now()

        balance = float(credit.amount_owed) - float(credit.amount_paid)

        if balance <= 0:
            credit.status = "paid"
        else:
            credit.status = "partially_paid"

        db.commit()

        return {
            "found": True,
            "customer": credit.customer_name,
            "amount_paid": amount_paid,
            "balance_remaining": max(balance, 0),
            "fully_paid": credit.status == "paid"
        }


    @staticmethod
    def get_debtors(db: Session, trader_id: int, filter: str = "all") -> dict:
        query = db.query(CreditSale).filter(
            CreditSale.trader_id == trader_id,
            CreditSale.status.in_(["outstanding", "partially_paid"])
        )

        if filter == "overdue":
            query = query.filter(
                CreditSale.due_date < datetime.now(),
                CreditSale.due_date.isnot(None)
            )
        elif filter == "recent":
            week_ago = datetime.now() - timedelta(days=7)
            query = query.filter(CreditSale.created_at >= week_ago)

        debtors = query.order_by(CreditSale.amount_owed.desc()).all()

        total_owed = sum(
            float(d.amount_owed) - float(d.amount_paid)
            for d in debtors
        )

        return {
            "debtors": [
                {
                    "name": d.customer_name,
                    "owed": float(d.amount_owed),
                    "paid": float(d.amount_paid),
                    "balance": float(d.amount_owed) - float(d.amount_paid),
                    "status": d.status,
                    "due_date": d.due_date.strftime("%d %b") if d.due_date else None,
                    "overdue": d.due_date and d.due_date < datetime.now()
                }
                for d in debtors
            ],
            "total_outstanding": total_owed,
            "total_debtors": len(debtors)
        }