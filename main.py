
from dotenv import load_dotenv
import requests
import openai
import os
from fastapi import FastAPI, Request
app = FastAPI()
# Replace clearly with your own OpenAI API key
load_dotenv()  # clearly loads variables from your .env file
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.get("/")
async def root():
    return {"message": "RixDigi AI WhatsApp API is running!"}

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    try:
        incoming_msg = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        sender_number = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional customer support assistant for RixDigi, a digital marketing agency."},
                {"role": "user", "content": incoming_msg}
            ]
        )

        reply = response.choices[0].message.content

        send_whatsapp_message(sender_number, reply)

    except Exception as e:
        print(f"Error: {e}")

    return {"status": "success"}

def send_whatsapp_message(to, message):
    url = "https://graph.facebook.com/v18.0/648346951698338/messages"
    headers = {
        "Authorization": "Bearer EAAan76DIlQEBO0N5c6LxWWDix5sUaBO0K3V62I2FSQyGh0Ke3r9CR7az4ZBg4o050PphtZCYQikJOBj1NL0ILEZCnA6uCxXaNoiXJ9J0JMAO1zrQOjSsdwnZBzAwIQKrfeSDnedz3mgpJg13B2ksHZAWVWdSKT8q7SPSC77qt6Yju8lRXAalRqBfNzEmRuvIGY3lIzG7ZB0FyngumEBpKhWLb3wxzVTNv7XeeZBMnVmCEoZD",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.json())
