from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
from dotenv import load_dotenv
import uuid
import json
import os
from datetime import datetime

# -------------------- Environment Setup --------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_key_123")

# -------------------- Gemini API Configuration --------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Gemini API key not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------- File Constants --------------------
USERS_FILE = "users.json"

# -------------------- Helper: File Handling --------------------
def read_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

def write_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# -------------------- Helper: Chat History --------------------
def history_file():
    if 'user' in session:
        name = session['user']['name'].lower().replace(" ", "_")
        return f"chat_history_{name}.json"
    return "chat_history_guest.json"

def load_history():
    return read_json(history_file())

def save_history(history):
    write_json(history_file(), history)

def get_chat_by_id(chat_id):
    return next((c for c in load_history() if c['id'] == chat_id), None)

def create_new_chat():
    chat_id = str(uuid.uuid4())[:8]
    new_chat = {"id": chat_id, "title": "New Chat", "messages": []}
    history = load_history()
    history.append(new_chat)
    save_history(history)
    return chat_id

# -------------------- Helper: User Auth --------------------
def load_users():
    return read_json(USERS_FILE)

def save_users(users):
    write_json(USERS_FILE, users)

# -------------------- Template Filter --------------------
@app.template_filter('timestamp')
def timestamp_filter(index):
    now = datetime.now()
    return now.strftime('%I:%M %p')

# -------------------- Routes: Authentication --------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"].lower()
        password = request.form["password"]

        users = load_users()
        if any(u["email"] == email for u in users):
            return "⚠️ Email already registered."

        hashed_pw = generate_password_hash(password)
        users.append({"name": name, "email": email, "password": hashed_pw})
        save_users(users)

        session["user"] = {"name": name, "email": email}
        return redirect(url_for("home"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]

        users = load_users()
        user = next((u for u in users if u["email"] == email), None)

        if user and check_password_hash(user["password"], password):
            session["user"] = {"name": user["name"], "email": user["email"]}
            return redirect(url_for("home"))

        return "⚠️ Invalid email or password."

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# -------------------- Routes: Chat --------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("signup"))

    history = load_history()
    if history:
        return redirect(url_for("chat", chat_id=history[-1]["id"]))

    new_chat_id = create_new_chat()
    return redirect(url_for("chat", chat_id=new_chat_id))

@app.route("/chat/<chat_id>")
def chat(chat_id):
    if "user" not in session:
        return redirect(url_for("signup"))

    current = get_chat_by_id(chat_id)
    if not current:
        return redirect(url_for("home"))

    return render_template("index.html", current_chat=current, chats=load_history(), username=session["user"]["name"])

@app.route("/chat/<chat_id>/send", methods=["POST"])
def send(chat_id):
    if "user" not in session:
        return redirect(url_for("signup"))

    user_input = request.form["msg"]

    try:
        response = model.generate_content(user_input)
        if hasattr(response, 'text'):
            bot_reply = response.text.strip()
        elif hasattr(response, 'candidates'):
            bot_reply = response.candidates[0].content.parts[0].text.strip()
        else:
            bot_reply = "⚠️ Gemini response format unknown."
    except Exception as e:
        bot_reply = f"⚠️ Error: {str(e)}"

    history = load_history()
    for chat in history:
        if chat["id"] == chat_id:
            chat["messages"].append({"user": user_input, "bot": bot_reply})
            if chat["title"] == "New Chat":
                chat["title"] = (user_input[:20] + "...") if len(user_input) > 20 else user_input
            break
    save_history(history)

    return redirect(url_for("chat", chat_id=chat_id))

@app.route("/new")
def new_chat():
    if "user" not in session:
        return redirect(url_for("signup"))
    return redirect(url_for("chat", chat_id=create_new_chat()))

@app.route("/chat/<chat_id>/delete", methods=["POST"])
def delete_chat(chat_id):
    if "user" not in session:
        return redirect(url_for("signup"))

    history = load_history()
    updated_history = [chat for chat in history if chat["id"] != chat_id]
    save_history(updated_history)

    return redirect(url_for("chat", chat_id=updated_history[-1]["id"] if updated_history else create_new_chat()))

# ✅ New Route: Delete all chat history
@app.route("/delete_history", methods=["POST"])
def delete_history():
    if "user" not in session:
        return redirect(url_for("signup"))

    save_history([])  # Empty the JSON history file
    return redirect(url_for("home"))

# -------------------- Run App --------------------
if __name__ == "__main__":
    app.run(debug=True)
