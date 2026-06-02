from google import genai
from google.genai import types
from dotenv import load_dotenv
from src.helpers import TraderService
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are Credit Ledger, a financial assistant for Nigerian informal traders on WhatsApp.

You help traders track daily sales and expenses, view summaries, and access credit.

Rules:
- Be concise and friendly
- Handle Pidgin English, Yoruba mixed English, and standard English naturally
- Reply customer in their language/speaking style
- Convert shorthand amounts: 60k = 60000, 1.5m = 1500000
- Always call a tool when intent is clear
- If unclear, ask one short clarifying question
- Never explain what you are about to do — just do it
"""


# ============================================================
# Tool definitions
# ============================================================

def log_transaction(type: str, amount: float, category: str, description: str = "") -> dict:
    """Log a financial transaction for the trader.
    Call this when the user mentions selling, buying, income,
    expenses, or any money movement.

    Args:
        type: 'income' if money came in, 'expense' if money went out
        amount: Amount in naira. Convert shorthand e.g. 60k = 60000
        category: One of: sales, stock, transport, rent, utilities, other
        description: Short description of the transaction
    """
    return {}


def get_summary(period: str) -> dict:
    """Get the trader's financial summary.
    Call when user asks how they are doing, wants a report,
    asks about profit, revenue, performance, or earnings.

    Args:
        period: 'today', 'week', or 'month'
    """
    return {}


def undo_last() -> dict:
    """Remove the last logged transaction.
    Call when user says they made a mistake, wants to undo,
    or correct the last entry.
    """
    return {}


def apply_for_loan() -> dict:
    """Start the loan or credit score process.
    Call when user asks about loans, credit, borrowing money,
    or wants to know their credit score.
    """
    return {}


def view_dashboard() -> dict:
    """Generate a dashboard link for the trader.
    Call when user asks to see their dashboard, profile, or visual report.
    """
    return {}

def log_credit_sale(
    customer_name: str,
    amount: float,
    due_date: str = "",
    notes: str = ""
) -> dict:
    """Log a sale made on credit — when a customer takes goods and will pay later.
    Call when trader says someone bought on credit, owes them money,
    or took goods without paying yet.

    Args:
        customer_name: Name of the customer who owes money
        amount: Amount owed in naira
        due_date: When they're expected to pay e.g. 'Friday', '2024-06-01' (optional)
        notes: What was sold or any extra details (optional)
    """
    return {}


def log_credit_payment(
    customer_name: str,
    amount_paid: float
) -> dict:
    """Record a payment from a customer who bought on credit.
    Call when trader says a customer has paid, settled their debt,
    or made a part payment.

    Args:
        customer_name: Name of the customer paying
        amount_paid: Amount they paid in naira
    """
    return {}


def get_debtors(filter: str = "all") -> dict:
    """Show list of customers who owe the trader money.
    Call when trader asks who owes them, wants to see outstanding debts,
    or asks about a specific customer's balance.

    Args:
        filter: 'all' for everyone, 'overdue' for late payments, 'recent' for last 7 days
    """
    return {}


# ============================================================
# Agent runner — single Gemini call
# ============================================================

def run_agent(db, trader, user_message: str) -> str:

    trader_context = f"""Trader context:
- Phone: {trader.phone_number}
- Streak: {trader.streak_count} days
- Credit score: {trader.credit_score or 'Not yet generated'}
"""

    user_content = trader_context + "\n\nUser: " + user_message

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[log_transaction, get_summary, undo_last, apply_for_loan, view_dashboard, log_credit_sale, log_credit_payment, get_debtors],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            )
        )

    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return "I'm a bit busy right now. Please try again in a few seconds."
        print(f"❌ Gemini error: {str(e)}")
        return "Something went wrong. Please try again."

    # No tool call — agent replied directly
    if not response.function_calls:
        return response.text

    fn = response.function_calls[0]
    fn_name = fn.name
    fn_args = dict(fn.args)

    print(f"🔧 Tool: {fn_name} | Args: {fn_args}")

    # Execute tool against database
    tool_result = execute_tool(db, trader, fn_name, fn_args)

    print(f"✅ Result: {tool_result}")

    # Build reply locally — no second Gemini call
    return build_reply(fn_name, tool_result, trader)


# ============================================================
# Build reply from tool result
# ============================================================

def build_reply(tool_name: str, result: dict, trader) -> str:

    if tool_name == "log_transaction":
        if not result.get("success"):
            return "❌ Couldn't log that. Please try again."

        return f"""✅ Logged.

Today:
💰 Income:  ₦{result['today_income']:,.0f}
💸 Expense: ₦{result['today_expense']:,.0f}
📈 Profit:  ₦{result['today_profit']:,.0f}

🔥 Streak: {result['streak']} days{f"{chr(10)}{30 - result['streak']} more days to unlock credit score." if result['streak'] < 30 else chr(10) + "✅ Eligible for credit. Send 'apply for loan'."}"""

    elif tool_name == "get_summary":
        period = result.get("period", "week")
        income = result.get("income", 0)
        expense = result.get("expense", 0)
        profit = result.get("profit", 0)
        margin = result.get("margin", 0)
        growth = result.get("growth", 0)
        growth_str = f"+{growth:.1f}%" if growth >= 0 else f"{growth:.1f}%"

        return f"""📊 {period.title()} Summary

💰 Revenue:  ₦{income:,.0f}
💸 Expenses: ₦{expense:,.0f}
📈 Profit:   ₦{profit:,.0f}
📉 Margin:   {margin:.1f}%
📊 vs Last {period.title()}: {growth_str}

🔥 Streak: {trader.streak_count} days"""

    elif tool_name == "undo_last":
        if not result.get("success"):
            return "Nothing to undo. You haven't logged anything yet."

        removed = result["removed"]
        tx_type = "Income" if removed["type"] == "income" else "Expense"

        return f"""↩️ Undone.

Removed: {tx_type} ₦{removed['amount']:,.0f} ({removed['category']})

Send your corrected entry whenever you're ready."""

    elif tool_name == "apply_for_loan":
        if not result.get("eligible"):
            days_left = 30 - result.get("streak", 0)
            return f"""❌ Not eligible yet.

You need {days_left} more days of logging to apply.

Keep going — every day builds your credit profile."""

        if result.get("credit_score"):
            return f"""Your Ledger Credit Score: {result['credit_score']}

Upload your OPay statement CSV to see current loan offers."""

        return """To generate your credit score, upload your OPay statement CSV.

How to get it:
1. Open OPay app
2. Go to Transaction History
3. Export → Download CSV
4. Send the file here"""

    elif tool_name == "view_dashboard":
        return f"""📊 Your Dashboard

{result['url']}

Link expires in {result['expires_in']}.
Open it to see your full P&L, charts, and credit score."""

    elif tool_name == "log_credit_sale":
        due = f"\nDue: {result['due_date']}" if result.get("due_date") else ""
        return f"""📝 Credit sale logged.

Customer: {result['customer']}
Amount:   ₦{result['amount']:,.0f}{due}

Reply 'who owes me' anytime to see all outstanding debts."""

    elif tool_name == "log_credit_payment":
        if not result.get("found"):
            return f"❌ Couldn't find an outstanding debt for {result.get('customer', 'that customer')}. Check the name and try again."

        if result.get("fully_paid"):
            return f"""✅ Payment recorded. Debt cleared.

{result.get('customer')} has fully paid.
Amount received: ₦{result.get('amount_paid', 0):,.0f}"""

        return f"""✅ Payment recorded.

{result.get('customer')} paid ₦{result.get('amount_paid', 0):,.0f}
Balance remaining: ₦{result.get('balance_remaining', 0):,.0f}"""

    elif tool_name == "get_debtors":
        debtors = result.get("debtors", [])
        total = result.get("total_outstanding", 0)

        if not debtors:
            return "✅ Nobody owes you anything right now."

        reply = f"""💰 Outstanding Debts
Total: ₦{total:,.0f} from {len(debtors)} {'person' if len(debtors) == 1 else 'people'}\n\n"""

        for d in debtors:
            overdue_tag = " ⚠️ OVERDUE" if d.get("overdue") else ""
            due_str = f" (due {d['due_date']})" if d.get("due_date") else ""
            reply += f"• {d['name']}{overdue_tag}\n  Owes: ₦{d['balance']:,.0f}{due_str}\n\n"

        return reply.strip()

    return "Done."

    


# ============================================================
# Tool execution
# ============================================================

def execute_tool(db, trader, tool_name: str, args: dict) -> dict:

    if tool_name == "log_transaction":
        TraderService.add_transaction(
            db,
            trader.id,
            args["type"],
            args["amount"],
            args["category"],
            args.get("description", "")
        )
        TraderService.update_streak(db, trader.id)
        db.refresh(trader)
        totals = TraderService.get_today_total(db, trader.id)

        return {
            "success": True,
            "today_income": totals["income"],
            "today_expense": totals["expense"],
            "today_profit": totals["profit"],
            "streak": trader.streak_count
        }

    elif tool_name == "get_summary":
        period = args.get("period", "week")

        if period == "today":
            return TraderService.get_today_total(db, trader.id)
        elif period == "month":
            return TraderService.get_month_summary(db, trader.id)
        else:
            return TraderService.get_week_summary(db, trader.id)

    elif tool_name == "undo_last":
        last_tx = TraderService.get_last_transaction(db, trader.id)

        if not last_tx:
            return {"success": False}

        tx_info = {
            "type": last_tx.type,
            "amount": float(last_tx.amount),
            "category": last_tx.category
        }
        TraderService.delete_transaction(db, last_tx.id, trader.id)

        return {"success": True, "removed": tx_info}

    elif tool_name == "apply_for_loan":
        return {
            "streak": trader.streak_count,
            "eligible": trader.streak_count >= 30,
            "credit_score": trader.credit_score
        }

    elif tool_name == "view_dashboard":
        token = TraderService.generate_dashboard_token(db, trader.id)
        dashboard_url = f"{os.getenv('FRONTEND_URL')}/dashboard?token={token}"

        return {
            "url": dashboard_url,
            "expires_in": "10 minutes"
        }


    elif tool_name == "select_lender":
        lender_name = args.get("lender_name")
        amount = args.get("amount")
        rate = args.get("rate")
        tenure = args.get("tenure_months")

        TraderService.create_loan_application(
            db,
            trader.id,
            lender_name,
            amount,
            rate,
            tenure,
            trader.credit_score
        )
        return {"success": True, "lender": lender_name}

    elif tool_name == "log_credit_sale":
        result = TraderService.log_credit_sale(
            db,
            trader.id,
            args["customer_name"],
            args["amount"],
            args.get("due_date", ""),
            args.get("notes", "")
        )
        return {
            "success": True,
            "customer": result.customer_name,
            "amount": float(result.amount_owed),
            "due_date": result.due_date.strftime("%d %b") if result.due_date else None
        }

    elif tool_name == "log_credit_payment":
        return TraderService.log_credit_payment(
            db,
            trader.id,
            args["customer_name"],
            args["amount_paid"]
        )

    elif tool_name == "get_debtors":
        return TraderService.get_debtors(
            db,
            trader.id,
            args.get("filter", "all")
        )

    return {"error": f"Unknown tool: {tool_name}"}