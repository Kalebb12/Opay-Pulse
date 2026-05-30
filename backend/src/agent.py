from google import genai
from google.genai import types
from dotenv  import load_dotenv
from src.helpers import TraderService
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are OPay Pulse, a financial assistant for Nigerian informal traders on WhatsApp.

You help traders track daily sales and expenses, view summaries, and access credit.

Rules:
- Be concise and friendly
- Handle Pidgin English, Yoruba mixed English, and standard English naturally
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


# ============================================================
# Agent runner
# ============================================================

def run_agent(db, trader, user_message: str) -> str:

    trader_context = f"""Trader context:
- Phone: {trader.phone_number}
- Streak: {trader.streak_count} days
- Credit score: {trader.credit_score or 'Not yet generated'}
"""

    user_content = trader_context + "\n\nUser: " + user_message

    # First call — agent decides which tool to use
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[log_transaction, get_summary, undo_last, apply_for_loan],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            )
        )
    )

    # Check if agent wants to call a tool
    if not response.function_calls:
        # Agent replied directly — no tool needed
        return response.text

    fn = response.function_calls[0]
    fn_name = fn.name
    fn_args = dict(fn.args)

    print(f"🔧 Agent calling tool: {fn_name} with args: {fn_args}")

    # Execute tool against real database
    tool_result = execute_tool(db, trader, fn_name, fn_args)

    print(f"✅ Tool result: {tool_result}")

    # Send tool result back to agent for final response
    # KEY FIX: use response.candidates[0].content directly
    # instead of manually reconstructing FunctionCall
    final_response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text=user_content)]
            ),
            response.candidates[0].content,  # ← the model's function call, untouched
            types.Content(
                role="user",
                parts=[types.Part(
                    function_response=types.FunctionResponse(
                        name=fn_name,
                        response=tool_result
                    )
                )]
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        )
    )

    return final_response.text


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
            data = TraderService.get_today_total(db, trader.id)
        elif period == "week":
            data = TraderService.get_week_summary(db, trader.id)
        elif period == "month":
            data = TraderService.get_month_summary(db, trader.id)
        else:
            data = TraderService.get_week_summary(db, trader.id)

        return data

    elif tool_name == "undo_last":
        last_tx = TraderService.get_last_transaction(db, trader.id)

        if not last_tx:
            return {"success": False, "message": "No transactions to undo"}

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
            "credit_score": trader.credit_score,
            "instruction": "Ask user to upload OPay CSV to generate credit score"
        }

    return {"error": f"Unknown tool: {tool_name}"}