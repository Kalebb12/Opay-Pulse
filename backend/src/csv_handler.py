import httpx
import pandas as pd
import os
import time
# from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.helpers import TraderService


async def handle_csv_upload(db: Session, trader, media_url: str) -> str:

    # Eligibility check first — no point processing if they can't apply
    if trader.streak_count < 30:
        days_left = 30 - trader.streak_count
        return f"""❌ Not eligible yet.

You need {days_left} more days of logging before you can apply for credit.

Keep logging daily. Your streak is at {trader.streak_count} days."""

    csv_path = None

    try:
        csv_path = await download_csv(media_url, trader.id)
        opay_data = parse_opay_csv(csv_path)

        if not opay_data["success"]:
            return f"""❌ Could not read that file.

Error: {opay_data['error']}

Make sure you're sending your OPay transaction history as a CSV file.

Steps:
1. Open OPay app
2. Transaction History
3. Export → Download CSV
4. Send the file here"""

        # Generate and save credit score
        score = TraderService.calculate_credit_score(db, trader.id, opay_data)
        TraderService.save_credit_score(db, trader.id, score)

        # Match lenders
        lenders = TraderService.match_lenders(score, opay_data["monthly_avg_income"])

        return build_credit_reply(score, lenders, opay_data)

    except Exception as e:
        print(f"❌ CSV upload error: {str(e)}")
        return "Something went wrong processing your file. Please try again."

    finally:
        if csv_path and os.path.exists(csv_path):
            os.remove(csv_path)


async def download_csv(media_url: str, trader_id: int) -> str:
    temp_path = f"/tmp/opay_{trader_id}_{int(time.time())}.csv"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            media_url,
            auth=(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            ),
            timeout=30.0
        )
        response.raise_for_status()

        with open(temp_path, "wb") as f:
            f.write(response.content)

    print(f"📥 Downloaded CSV to: {temp_path}")
    return temp_path


def parse_opay_csv(csv_path: str) -> dict:

    try:
        df = pd.read_csv(csv_path)

        # Print columns so you can see the real OPay format
        print(f"📊 CSV columns: {list(df.columns)}")
        print(f"📊 First row: {df.iloc[0].to_dict() if len(df) > 0 else 'empty'}")

        # Normalize column names
        df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

        # Find amount column
        amount_col = next(
            (c for c in df.columns if "amount" in c), None
        )

        # Find type/direction column
        type_col = next(
            (c for c in df.columns if any(
                k in c for k in ["type", "direction", "transaction_type", "cr/dr"]
            )), None
        )

        # Find date column
        date_col = next(
            (c for c in df.columns if any(
                k in c for k in ["date", "time", "created", "timestamp"]
            )), None
        )

        if not amount_col:
            return {
                "success": False,
                "error": f"No amount column found. Columns detected: {list(df.columns)}"
            }

        # Clean and parse amounts
        df[amount_col] = (
            df[amount_col]
            .astype(str)
            .str.replace(",", "")
            .str.replace("₦", "")
            .str.replace(" ", "")
            .pipe(pd.to_numeric, errors="coerce")
        )
        df = df.dropna(subset=[amount_col])

        # Parse dates
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

        # Separate income from expense
        if type_col:
            col_values = df[type_col].astype(str).str.lower()
            income_mask = col_values.str.contains("credit|cr|in|receive|received", na=False)
            expense_mask = col_values.str.contains("debit|dr|out|send|sent|payment", na=False)

            income_df = df[income_mask]
            expense_df = df[expense_mask]
        else:
            # No type column — split by positive/negative amounts
            income_df = df[df[amount_col] > 0]
            expense_df = df[df[amount_col] < 0]

        total_income = float(income_df[amount_col].abs().sum())
        total_expense = float(expense_df[amount_col].abs().sum())

        # Monthly stats for scoring
        monthly_avg_income = total_income
        income_std_dev = 0
        months_active = 1

        if date_col and not income_df.empty:
            income_df = income_df.copy()
            income_df["month"] = income_df[date_col].dt.to_period("M")
            monthly_groups = income_df.groupby("month")[amount_col].sum().abs()

            months_active = max(len(monthly_groups), 1)
            monthly_avg_income = float(monthly_groups.mean())
            income_std_dev = float(monthly_groups.std() or 0)

        return {
            "success": True,
            "total_income": total_income,
            "total_expense": total_expense,
            "monthly_avg_income": monthly_avg_income,
            "income_std_dev": income_std_dev,
            "months_active": months_active,
            "total_transactions": len(df)
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def build_credit_reply(score: int, lenders: list, opay_data: dict) -> str:

    if score >= 700:
        band = "Excellent ⭐⭐⭐"
    elif score >= 600:
        band = "Good ⭐⭐"
    elif score >= 500:
        band = "Fair ⭐"
    else:
        band = "Building 🔄"

    reply = f"""🎯 Ledger Credit Score: {score}
{band}

Based on:
📊 {opay_data['months_active']} months OPay history
💰 Avg monthly: ₦{opay_data['monthly_avg_income']:,.0f}
📋 {opay_data['total_transactions']} transactions\n\n"""

    if not lenders:
        reply += """You don't qualify for offers yet.

Keep logging daily to improve your score."""
        return reply

    reply += "💼 You Qualify For:\n\n"

    for i, lender in enumerate(lenders, 1):
        reply += f"""{i}. {lender['lender']}
   Amount: ₦{lender['amount']:,.0f}
   Rate:   {lender['rate']}
   Term:   {lender['tenure']}\n\n"""

    reply += "Reply the lender name to get details.\nFunds hit your OPay wallet in 24 hours."

    return reply