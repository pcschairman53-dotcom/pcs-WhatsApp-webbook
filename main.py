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

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    return PlainTextResponse("Verification failed", status_code=403)


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    print(body)
    return {"status": "received"}
