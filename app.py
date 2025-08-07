from flask import Flask, request
import requests
from groq import Groq

app = Flask(__name__)

# Groq API
import os
from dotenv import load_dotenv

load_dotenv()

# Groq API
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Send message to Telegram (supports long replies)
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    chunks = [text[i:i+4096] for i in range(0, len(text), 4096)]
    for chunk in chunks:
        try:
            requests.post(url, json={"chat_id": chat_id, "text": chunk})
        except Exception as e:
            print("Telegram error:", e)

@app.route("/")
def home():
    return "🧴 Skincare chatbot (Groq) is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Telegram data:", data)

    try:
        if "message" in data and "text" in data["message"]:
            message = data["message"]["text"]
            chat_id = data["message"]["chat"]["id"]

            if message.lower() == "/start":
                send_message(chat_id, "Hi! 👋 I'm your skincare buddy. Tell me about your skin issues (e.g. oily with acne) 💬")
                return "ok"

            prompt = f"""You are a skincare expert and reply like a friendly chatbot.
Keep the response short, with emojis, and easy to read — like a conversation.
No bold or markdown, just plain text.

User: {message}"""

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a friendly skincare expert. Reply casually and helpfully in chat format."},
                    {"role": "user", "content": prompt}
                ]
            )

            reply = response.choices[0].message.content.strip()
            send_message(chat_id, reply)

    except Exception as e:
        print("❌ Error:", e)
        send_message(chat_id, "Oops! Something went wrong. Try again!")

    return "ok"

if __name__ == "__main__":
    app.run(port=5000)
