from datetime import date, datetime, timedelta

from src.models import get_db, Transaction
from src.helpers import TraderService

PHONE = "+2347083112827"

INCOME_CATEGORIES = ["sales", "services", "cashback", "mobile top-up"]
EXPENSE_CATEGORIES = ["stock", "transport", "rent", "supplies", "wages", "marketing"]

DEMO_NOTEBOOK = [
    "Daily sales deposit",
    "Service payment received",
    "Cashback credit",
    "Inventory purchase",
    "Local transport",
    "Supplier payment",
    "Rent payment",
    "Staff wages",
    "Marketing spend",
    "Office supplies",
]


def build_demo_transactions():
    today = date.today()
    txs = []
    days = 90

    for day_offset in range(days):
        day = today - timedelta(days=(days - 1) - day_offset)
        base_time = datetime(day.year, day.month, day.day, 12, 0)

        if day_offset % 2 == 0:
            amount = 22000 + ((day_offset * 650) % 24000)
            category = INCOME_CATEGORIES[day_offset % len(INCOME_CATEGORIES)]
            description = DEMO_NOTEBOOK[day_offset % len(DEMO_NOTEBOOK)]
            txs.append({
                "type": "income",
                "amount": amount,
                "category": category,
                "description": description,
                "logged_at": base_time,
            })

        if day_offset % 3 == 0:
            amount = 4800 + ((day_offset * 720) % 15000)
            category = EXPENSE_CATEGORIES[day_offset % len(EXPENSE_CATEGORIES)]
            description = DEMO_NOTEBOOK[(day_offset + 4) % len(DEMO_NOTEBOOK)]
            txs.append({
                "type": "expense",
                "amount": amount,
                "category": category,
                "description": description,
                "logged_at": base_time + timedelta(hours=4),
            })

    return txs


def main():
    db = next(get_db())
    try:
        trader = TraderService.get_or_create_trader(db, PHONE)

        deleted = db.query(Transaction).filter(Transaction.trader_id == trader.id).delete()
        db.commit()
        print(f"Cleared {deleted} existing transaction(s) for {PHONE}")

        demo_transactions = build_demo_transactions()
        for tx in demo_transactions:
            db.add(Transaction(
                trader_id=trader.id,
                type=tx["type"],
                amount=tx["amount"],
                category=tx["category"],
                description=tx["description"],
                logged_at=tx["logged_at"],
            ))

        db.commit()
        total = db.query(Transaction).filter(Transaction.trader_id == trader.id).count()
        print(f"Inserted {len(demo_transactions)} demo transactions for {PHONE}")
        print(f"Trader {PHONE} now has {total} transactions")

    finally:
        db.close()


if __name__ == "__main__":
    main()
