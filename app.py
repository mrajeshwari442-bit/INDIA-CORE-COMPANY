"""
app.py

Flask backend for the INDIA CORE COMPANY chatbot.
It receives a user message from the frontend, sends it to the Gemini
API along with the system prompt from chatbot_config.py, and returns
the model's reply as JSON.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from chatbot_config import SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Please add it to your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# Create the Gemini model with the company-specific system prompt
model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=SYSTEM_PROMPT,
)

app = Flask(__name__)


@app.route("/")
def home():
    """Render the chat UI."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Receive a user message and return the chatbot's reply."""
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a message before sending."}), 400

    try:
        response = model.generate_content(user_message)
        reply_text = response.text.strip() if response.text else (
            "Sorry, I couldn't generate a response. Please try again."
        )
    except Exception as exc:
        reply_text = f"Something went wrong while contacting the AI service: {exc}"

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)
