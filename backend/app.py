from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
from groq import Groq
from flask_cors import CORS

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
