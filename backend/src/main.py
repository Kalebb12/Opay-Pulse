from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response
from twilio.rest import Client
import os
from dotenv import load_dotenv
from src.models import get_db
from src.helpers import TraderService
from sqlalchemy.orm import Session 

load_dotenv()


app = FastAPI(title="Opay Pulse API")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
 
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@app.get("/")
async def root():
    return {"message": "Welcome to the Opay Pulse API!"}


@app.post("/whatsapp")
async def handle_whatsapp(request: Request, db: Session = Depends(get_db)):
    """
    Receive messages from Twilio WhatsApp
    """
    
    # Parse incoming data
    form_data = await request.form()
    incoming_phone = form_data.get("From")  # e.g., "whatsapp:+2348032XXXXXX"
    incoming_message = form_data.get("Body", "").strip()
    
    print(f"\n Incoming message from {incoming_phone}")
    print(f"   Message: {incoming_message}")
    
    # Step 1: Get or create trader
    trader = TraderService.get_or_create_trader(db, incoming_phone)
    
    # Step 2: Log the incoming message
    TraderService.log_message(db, trader.id, incoming_message, "inbound")
    
    # Step 3: Update streak
    TraderService.update_streak(db, trader.id)
    
    # Step 4: Generate response (dummy for now)
    current_streak = TraderService.get_streak(db, trader.id)
    
    reply_message = f"""✅ Logged.

You said: "{incoming_message}"

🔥 Streak: {current_streak} days

Reply HELP for commands."""
    
    # Step 5: Send response back
    send_whatsapp_message(incoming_phone, reply_message)
    
    # Step 6: Log the outgoing message
    TraderService.log_message(db, trader.id, reply_message, "outbound")
    
    # Return OK to Twilio
    return Response("OK", status_code=200)


def send_whatsapp_message(to_number: str, message_body: str):
    """
    Send a WhatsApp message via Twilio
    """
    try:
        message = client.messages.create(
            from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
            body=message_body,
            to={to_number}
        )
        print(f"Message sent: {message.sid}")
        return message.sid
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return None