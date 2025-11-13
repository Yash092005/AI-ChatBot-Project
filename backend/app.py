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
    session_id = request.json.get("session_id", None)
    print("USER MSG RECEIVED:", user_message)  # Debug log

    if not user_message:
        return jsonify({"reply": "Hey there! Feel free to ask me anything about water conservation. I'm here to help!"})

    try:
        # Get or create session
        session_id, session_data = get_session(session_id)

        # Check if this is a water calculation request
        if is_water_calculation_request(user_message):
            calculation_result = calculate_usage()
            bot_reply = f"I'd be happy to help calculate your water usage! Based on average household usage, here's what I found:\n\n💧 **Daily Usage**: {calculation_result} liters\n\nThis is just an estimate though. Want to dive deeper into any specific area? I can help you understand where you might be using the most water and how to reduce it!"
        else:
            # Build conversation context with personality and knowledge base
            context_messages = build_conversation_context(session_data, user_message)

            # Generate AI response with full context
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=context_messages
            )

            bot_reply = response.choices[0].message.content

        # Store message in session history
        session_data['messages'].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        session_data['messages'].append({
            'role': 'assistant',
            'content': bot_reply,
            'timestamp': datetime.now().isoformat()
        })

        print("BOT REPLY:", bot_reply)  # Debug log
        return jsonify({
            "reply": bot_reply,
            "session_id": session_id
        })

    except Exception as e:
        print("ERROR:", str(e))

        # Enhanced error handling with friendly fallback messages
        if "rate" in str(e).lower():
            fallback_msg = "Whoa! You're chatting up a storm! Give me just a moment to catch up with your questions. 😊"
        elif "timeout" in str(e).lower():
            fallback_msg = "Hmm, I'm having a bit of trouble connecting right now. Could you try that again in a second?"
        elif "connection" in str(e).lower():
            fallback_msg = "I'm having some network issues, but I'm still here to help! Could you rephrase that and try again?"
        else:
            fallback_msg = "I seem to be having a technical hiccup, but I'd love to help you with water conservation! Try asking me about saving water in your kitchen, bathroom, or garden."

        return jsonify({
            "reply": fallback_msg,
            "session_id": session_id or str(uuid.uuid4())
        })

@app.route("/calculate", methods=["POST"])
def calculate():
    """Enhanced water calculation endpoint"""
    try:
        data = request.json.get("data", {})
        session_id = request.json.get("session_id", None)

        # Get session for context
        if session_id:
            _, session_data = get_session(session_id)
        else:
            session_data = {'messages': []}

        # Extract calculation parameters
        showers = data.get("showers", 2)  # Default: 2 showers
        shower_time = data.get("shower_time", 10)  # Default: 10 minutes
        toilet_flushes = data.get("toilet_flushes", 6)  # Default: 6 flushes
        faucet_use = data.get("faucet_use", 5)  # Default: 5 minutes
        laundry = data.get("laundry", 1)  # Default: 1 load

        # Calculate usage (rough estimates in liters)
        shower_usage = showers * shower_time * 12  # ~12 liters per minute
        toilet_usage = toilet_flushes * 6  # ~6 liters per flush
        faucet_usage = faucet_use * 8  # ~8 liters per minute
        laundry_usage = laundry * 75  # ~75 liters per load

        total_daily = shower_usage + toilet_usage + faucet_usage + laundry_usage
        total_monthly = total_daily * 30
        total_yearly = total_daily * 365

        response_data = {
            "daily": round(total_daily, 1),
            "monthly": round(total_monthly, 1),
            "yearly": round(total_yearly, 1),
            "breakdown": {
                "showers": round(shower_usage, 1),
                "toilet": round(toilet_usage, 1),
                "faucet": round(faucet_usage, 1),
                "laundry": round(laundry_usage, 1)
            }
        }

        # Generate personalized response
        if total_daily > 200:
            suggestion = "That's higher than average! The biggest opportunity I see is shorter showers - cutting just 5 minutes can save ~60 liters daily!"
        elif total_daily > 150:
            suggestion = "You're doing okay, but there's room for improvement. Try focusing on the area with your highest usage above."
        else:
            suggestion = "Great job! You're using water efficiently. Want to explore even more ways to save?"

        return jsonify({
            "data": response_data,
            "suggestion": suggestion,
            "reply": f"Here's your water usage breakdown:\n\n💧 **Daily**: {response_data['daily']} liters\n📅 **Monthly**: {response_data['monthly']} liters\n📊 **Yearly**: {response_data['yearly']} liters\n\n{suggestion}\n\nWant tips on reducing your highest usage area?"
        })

    except Exception as e:
        print("CALCULATION ERROR:", str(e))
        return jsonify({
            "reply": "I had trouble calculating that. Let's try a simpler approach - I can give you general tips for saving water in your home!",
            "data": None
        })

@app.route("/clear_session", methods=["POST"])
def clear_session():
    """Clear session history for a fresh start"""
    session_id = request.json.get("session_id")
    if session_id and session_id in sessions:
        del sessions[session_id]

    new_session_id, _ = get_session()
    return jsonify({
        "session_id": new_session_id,
        "reply": "Great! Let's start fresh. What water conservation topic can I help you with today?"
    })

if __name__ == "__main__":
    app.run(debug=True)
