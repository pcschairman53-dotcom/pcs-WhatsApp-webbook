from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import os
import requests
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "pcs_verify_token_2026")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


@app.get("/")
def home():
    return {"status": "PCS WhatsApp Webhook Running"}


@app.get("/webhook")
async def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    return PlainTextResponse("Verification failed", status_code=403)


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

            # ===== Gemini AI =====
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"""
You are PCS AI WhatsApp Assistant.

Rules:
- Detect the user's language automatically.
- Reply in the same language as the user.
- If the user mixes multiple languages, reply naturally in the same style.
- Keep answers clear, accurate and professional.
- Be polite and helpful.
- Keep replies under 120 words unless the user asks for a detailed explanation.

User Message:
{text}
"""
                )

                reply = response.text

            except Exception as e:
                print("Gemini Error:", e)
                reply = "Sorry, I'm temporarily unavailable. Please try again in a moment."

            # ===== Send WhatsApp Reply =====
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
        print("Webhook Error:", e)

    return {"status": "received"}
