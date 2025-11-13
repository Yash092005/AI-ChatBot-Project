from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timedelta
from groq import Groq
from flask_cors import CORS
import re
import json

# Import local modules
from kb_search import kb_search
from calc import calculate_usage

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Session storage for conversation history
sessions = {}

# Personality system prompt
PERSONALITY_PROMPT = """You are a friendly and knowledgeable water conservation assistant. Your personality should be:

🌊 **Professional yet Approachable**: You're an expert but talk like a helpful friend, not a textbook. Use clear, simple language that anyone can understand.

💬 **Conversational Tone**:
- Use natural contractions (it's, you're, I'll)
- Start with friendly acknowledgments ("Great question!", "That's smart thinking!")
- Be encouraging and positive
- Ask follow-up questions to keep the conversation going

🎯 **Helpful Focus**:
- Break down complex topics into simple, actionable steps
- Use examples and analogies when explaining concepts
- Always provide practical advice people can actually use
- Focus on water conservation but stay conversational

🚫 **What to Avoid**:
- Don't be overly formal or academic
- Don't use slang or overly casual language
- Don't just dump facts - explain WHY things matter
- Don't be robotic - show some personality!

Example response style:
"Great question! Bathroom water usage can really add up. Here are my top 3 simple tips that actually work:

1️⃣ Shorter showers - Try aiming for 5-7 minutes instead of 15
2️⃣ Fix those drips - Even small leaks waste gallons daily!
3️⃣ Low-flow fixtures - They cut usage by 30-50% without you noticing

Which of these interests you most? I can dive deeper into any of them!""""

def get_session(session_id=None):
    """Get or create a session for conversation history"""
    if not session_id:
        session_id = str(uuid.uuid4())

    if session_id not in sessions:
        sessions[session_id] = {
            'messages': [],
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
    else:
        sessions[session_id]['last_activity'] = datetime.now()

    return session_id, sessions[session_id]

def build_conversation_context(session_data, user_message):
    """Build context for AI including conversation history and knowledge base"""
    context_messages = []

    # Add personality system message if this is the start of conversation
    if not session_data['messages']:
        context_messages.append({"role": "system", "content": PERSONALITY_PROMPT})

    # Add recent conversation history (last 10 exchanges)
    recent_messages = session_data['messages'][-10:]
    for msg in recent_messages:
        if msg['role'] == 'user':
            context_messages.append({"role": "user", "content": msg['content']})
        else:
            context_messages.append({"role": "assistant", "content": msg['content']})

    # Search knowledge base for relevant information
    kb_info = kb_search(user_message)

    # Add knowledge base context if found
    if kb_info and not kb_info.startswith("I can help with"):
        context_messages.append({
            "role": "system",
            "content": f"Relevant water conservation information: {kb_info}. Use this to enhance your response, but keep your natural conversational style."
        })

    # Add current user message
    context_messages.append({"role": "user", "content": user_message})

    return context_messages

def is_water_calculation_request(message):
    """Check if user is asking for water calculation"""
    calc_keywords = [
        'calculate', 'calculation', 'usage', 'consumption', 'footprint',
        'how much water', 'water use', 'gallons', 'liters', 'estimate'
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in calc_keywords)

def cleanup_old_sessions():
    """Remove sessions older than 1 hour"""
    cutoff = datetime.now() - timedelta(hours=1)
    expired_sessions = [
        session_id for session_id, data in sessions.items()
        if data['last_activity'] < cutoff
    ]
    for session_id in expired_sessions:
        del sessions[session_id]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    print("USER MSG RECEIVED:", user_message)  # Debug log

    if not user_message:
        return jsonify({"reply": "You sent an empty message!"})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": user_message}]
        )

        bot_reply = response.choices[0].message.content
        print("BOT REPLY:", bot_reply)  # Debug log
        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"reply": f"Error generating response: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
