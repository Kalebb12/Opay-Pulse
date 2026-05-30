from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response
from twilio.rest import Client
import os
from dotenv import load_dotenv
from src.csv_handler import handle_csv_upload
from src.models import get_db
from src.helpers import TraderService
from sqlalchemy.orm import Session 
from src.agent import run_agent

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
    form_data = await request.form()
    incoming_phone = form_data.get("From")
    incoming_message = form_data.get("Body", "").strip()
    media_url = form_data.get("MediaUrl")

    trader = TraderService.get_or_create_trader(db, incoming_phone)

    if media_url:
        reply = await handle_csv_upload(db, trader, media_url)
    else:
        reply = run_agent(db, trader, incoming_message)

    send_whatsapp_message(incoming_phone, reply)
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