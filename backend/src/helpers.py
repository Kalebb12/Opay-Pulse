from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models import Trader, Transaction
from datetime import date, datetime, timedelta


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