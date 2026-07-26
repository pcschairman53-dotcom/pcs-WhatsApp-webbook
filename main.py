from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import os

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "pcs_verify_token_2026")


@app.get("/")
def home():
    return {"status": "PCS WhatsApp Webhook Running"}


@app.get("/webhook")
async def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    print("MODE:", mode)
    print("TOKEN:", token)
    print("VERIFY_TOKEN:", VERIFY_TOKEN)

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    return PlainTextResponse("Verification failed", status_code=403)

import requests

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    print(body)

    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" in value:
            msg = value["messages"][0]
            sender = msg["from"]
            text = msg["text"]["body"]

            reply = f"Hello! You said: {text}"

            url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"

            headers = {
                "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                "Content-Type": "application/json"
            }

            data = {
                "messaging_product": "whatsapp",
                "to": sender,
                "type": "text",
                "text": {
                    "body": reply
                }
            }

            r = requests.post(url, headers=headers, json=data)
            print(r.status_code, r.text)

    except Exception as e:
        print(e)

    return {"status": "received"}
