# 💧 Water Chatbot

## 📌 Project Overview
This project is a chatbot for water-related queries.  

- Built using **Python (Flask)** for the backend.  
- Uses an **AI model (OpenAI/Groq API)** to generate responses.  
- **Frontend** built with HTML, CSS, and JavaScript for chat interface.  
- Supports **dark mode** and **typing animation** for better user experience.  

---

## 📂 Folder Structure
```
water-chatbot/
│
├─ backend/
│   ├─ app.py                # Flask backend
│   ├─ .env                  # API key stored here
│   ├─ requirements.txt      # Python dependencies
│   ├─ templates/
│   │   └─ index.html        # Chatbot HTML interface
│   └─ static/
│       ├─ style.css         # Styling for chat interface
│       └─ script.js         # JS for sending/receiving messages
│
├─ frontend/                 # UI related files
├─ kb/                       # Knowledge base (if any)
├─ database/                 # Database files (.sql)
└─ README.md                 # Project documentation
```

---

## ▶️ How to Run the Bot
1. Make sure **Python 3.10+** is installed.  
2. Open terminal in the **backend** folder.  
3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
4. Make sure `.env` file contains your API key:  
   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxx
   ```
5. Start the Flask server:  
   ```bash
   python app.py
   ```
6. Open browser and go to:  
   ```
   http://127.0.0.1:5000
   ```

---

## 💬 How to Use
- Type your message in the input box.  
- Click **Send** or press **Enter**.  
- The bot will reply after a short *“typing” animation*.  
- Switch between **Dark 🌙 / Light ☀️ Mode** using the toggle in header.  

---

## 📝 Notes for Examiners
- The bot requires **internet access** (uses AI API).  
- Make sure the API key in `.env` is valid; otherwise, it will show an error.  
- Frontend is fully **responsive** and can handle multiple messages.  

---

✦ Developed with ❤️ for learning & experimentation.
