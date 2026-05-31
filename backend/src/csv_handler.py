import httpx
import pandas as pd
import os
import time
import math
from sqlalchemy.orm import Session
from src.helpers import TraderService

async def handle_csv_upload(db: Session, trader, media_url: str) -> str:

    if trader.streak_count < 30:
        days_left = 30 - trader.streak_count
        return f"""❌ Not eligible yet.

You need {days_left} more days of logging to apply for credit.

Your streak: {trader.streak_count} days."""

    csv_path = None

    try:
        csv_path = await download_csv(media_url, trader.id)

        # Use new parser
        opay_data = parse_opay_statement(csv_path)

        if not opay_data.get("success"):
            return f"""❌ Could not read that file.

{opay_data.get('error', 'Unknown error')} 

Make sure you are sending the OPay statement export as an XLSX file."""

        score = TraderService.calculate_credit_score(db, trader.id, opay_data)
        TraderService.save_credit_score(db, trader.id, score)
        lenders = TraderService.match_lenders(score, opay_data["monthly_avg_income"])
        # match_data = TraderService.match_csv_to_logs(db, trader.id, opay_data)

        return build_credit_reply(score, lenders, opay_data)

    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return "Something went wrong processing your file. Please try again."

    finally:
        if csv_path and os.path.exists(csv_path):
            os.remove(csv_path)

async def download_csv(media_url: str, trader_id: int) -> str:
    temp_path = f"/tmp/opay_{trader_id}_{int(time.time())}.xlsx"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            media_url,
            auth=(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            ),
            timeout=30.0,
            follow_redirects=True
        )
        response.raise_for_status()

        with open(temp_path, "wb") as f:
            f.write(response.content)

    print(f"📥 Downloaded CSV to: {temp_path}")
    return temp_path

def clean_float(val, default=0.0):
    """Convert NaN/inf to safe default"""
    try:
        if val is None or math.isnan(val) or math.isinf(val):
            return default
    except (TypeError, ValueError):
        return default
    return float(val)

def parse_opay_statement(file_path: str) -> dict:
    """
    Parse OPay XLSX bank statement export.
    
    Format:
    - Several header rows (account info, balances, etc.)
    - Then a transaction table starting with:
      Trans. Date | Value Date | Description | Debit(₦) | Credit(₦) | Balance After(₦) | Channel | Transaction Reference
    """
    try:
        # Read the full sheet without assuming header row
        df = pd.read_excel(file_path, header=None, engine="openpyxl")

        print(f"📊 Raw shape: {df.shape}")
        print(f"📊 First 10 rows:\n{df.head(10)}")

        # Find the row where the actual transaction table starts
        # Look for the row containing "Trans. Date"
        header_row_index = None

        for i, row in df.iterrows():
            row_values = [str(v).strip().lower() for v in row.values]
            if any("trans. date" in v or "trans date" in v for v in row_values):
                header_row_index = i
                break

        if header_row_index is None:
            return {
                "success": False,
                "error": "Could not find transaction table. Make sure this is an OPay statement export."
            }

        print(f"📊 Table starts at row: {header_row_index}")

        # Re-read with correct header row
        df = pd.read_excel(
            file_path,
            header=header_row_index,
            engine="openpyxl"
        )

        # Normalize column names
        df.columns = df.columns.str.strip()

        print(f"📊 Columns found: {list(df.columns)}")

        # Find debit and credit columns
        debit_col = next(
            (c for c in df.columns if "debit" in str(c).lower()), None
        )
        credit_col = next(
            (c for c in df.columns if "credit" in str(c).lower()), None
        )
        date_col = next(
            (c for c in df.columns if "trans" in str(c).lower() and "date" in str(c).lower()), None
        )

        if not credit_col:
            return {
                "success": False,
                "error": f"Could not find Credit column. Columns found: {list(df.columns)}"
            }

        # Clean up "--" values (OPay uses this for empty cells)
        def clean_amount(val):
            if pd.isna(val):
                return 0
            val_str = str(val).strip().replace(",", "").replace("₦", "").replace("--", "0")
            try:
                return float(val_str)
            except:
                return 0

        df["_credit"] = df[credit_col].apply(clean_amount)
        df["_debit"] = df[debit_col].apply(clean_amount) if debit_col else 0

        # Drop rows where both credit and debit are 0 (empty/summary rows)
        df = df[(df["_credit"] > 0) | (df["_debit"] > 0)]

        # Parse dates
        if date_col:
            df["_date"] = pd.to_datetime(df[date_col], errors="coerce")

        total_credit = float(df["_credit"].sum())
        total_debit = float(df["_debit"].sum())

        monthly_avg_income = total_credit
        income_std_dev = 0.0
        months_active = 1

        if date_col:
            income_df = df[df["_credit"] > 0].copy()
            income_df = income_df.dropna(subset=["_date"])

            if not income_df.empty:
                income_df["_month"] = income_df["_date"].dt.to_period("M")
                monthly_groups = income_df.groupby("_month")["_credit"].sum()

                months_active = max(len(monthly_groups), 1)
                monthly_avg_income = float(monthly_groups.mean())
                income_std_dev = float(monthly_groups.std() or 0)

        # Clean everything before returning
        return {
            "success": True,
            "total_income": clean_float(total_credit),
            "total_expense": clean_float(total_debit),
            "monthly_avg_income": clean_float(monthly_avg_income),
            "income_std_dev": clean_float(income_std_dev),
            "months_active": int(months_active),
            "total_transactions": int(len(df))
        }

    except Exception as e:
        print(f"❌ Parse error: {str(e)}")
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