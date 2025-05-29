
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
            model="gpt-4-1106-preview",
           messages=[
        {
            "role": "system",
            "content": (
                "You are a professional and helpful support assistant for RixDigi, a digital marketing agency."
                "Your job is to assist ONLY with questions related to RixDigi's services, business hours, pricing, and client process. "
                "If a user asks something unrelated to RixDigi (like coding help, database issues, or tech support), "
                "politely respond that you'd be happy to schedule a consultation or connect them with the right team. "
                "Never answer technical questions unless they relate directly to RixDigi’s services."
                "You are a professional, friendly, and efficient support assistant at RixDigi, a digital marketing agency. "
                "Speak like a real human — concise, clear, polite, and direct. "
                "Reply in a maximum of 2-3 short sentences. Avoid over-explaining or sounding robotic. "
                "Only answer questions about RixDigi's services, pricing, hours, or client process. "
                "If someone asks an unrelated technical question (like coding or database help), respond politely and invite them to schedule a meeting to discuss their problem."
                "You are a helpful, polite, and efficient assistant at RixDigi, a digital marketing agency. "
                "If someone wants to schedule a consultation, ask them what day and time works best. "
                "Politely guide them to provide 2–3 options for availability. "
                "Once they share timing, confirm you’re checking the calendar, and pretend to reserve the time. "
                "Always sound human and helpful, and do not request personal contact info in the message. "
                "Example: 'Thanks! I'll pencil in Thursday at 3 PM and confirm shortly.'"
                "If someone asks for RixDigi's contact information, always reply with this:\n\n"
                "📞 Phone: +92 0300 5002659\n"
                "📧 Email: info@rixdigi.com\n\n"
                "Never invent or guess contact details."
            )
        },
           {"role": "system", "content": "...same content above..."},
           {"role": "user", "content": "What services do you offer?"},
           {"role": "assistant", "content": "We offer website design, SEO, social media, and Google Ads. Need help with something specific?"},
           {"role": "user", "content": "Can you fix my WordPress database?"},
           {"role": "assistant", "content": "That sounds more technical — I’d be happy to schedule a call to go over it in detail."},
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
    url = "https://graph.facebook.com/v18.0/696133063579595/messages"
    headers = {
        "Authorization": "Bearer EAAan76DIlQEBO39sAgrzJ5hD1S2KDspZAzfrXlxrf8RA4AKzNvEcDLEZCE3azQQPhmwbLpg0iUXJ8RylyMZB9bwrmF80I8ekH9xL9OPkBLZCpOhfZClCSFNTCs3zryZBjZAbSUyas0ZCfNFxtdKmx0Fw6nsUyoWy6cBDh6E3mIDpCUauKAJAsZCrGQir08g7fXjmQTyZBwnGVoJuUeAb0cZAwf4WUXqG0hfZB66uRc4WZCioBHezK5VEr3zwZD",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.json())

