
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "RixDigi AI WhatsApp API is running!"}

# ✅ WhatsApp webhook verification
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == "rixdigi0325":
        return PlainTextResponse(content=params.get("hub.challenge"))
    return PlainTextResponse(status_code=403, content="Invalid token")

# ✅ Handle incoming messages
@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        phone_number = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]

        # Generate GPT-4 response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for RixDigi, a digital marketing agency."},
                {"role": "user", "content": message}
            ]
        )
        reply = response.choices[0].message.content

        # Send reply via WhatsApp
        send_whatsapp_message(phone_number, reply)

    except Exception as e:
        print(f"Error: {e}")

    return {"status": "success"}

def send_whatsapp_message(to, message):
    url = "https://graph.facebook.com/v18.0/648346951698338/messages"
    headers = {
        "Authorization": "Bearer EAAan76DIlQEBO5200njS2gFcJPsGeUGIxAehnbUYuzeUt8HrP58X9gHWyVQvm4bTM3Kbm7WzDw12jq8U66gqtDHzshtYTGGbt4coZAVFj6vshLZBAvMi7J051nHpE1uDOZAdnlwYaUaGkPTsRgINDKhA4afZB5OKd7euxZC9DdpJbTjkhaFsRNdXdtz2lGRezynHMQKyII2qxzsUPbUmrnV6OSnY4zpziNDNfGwZB17ESGOMD4RwDd",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.json())

