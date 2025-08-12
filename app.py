from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import spacy
from fuzzywuzzy import process
from knowledge_base import faq_knowledge_base, intent_keywords, intent_responses
import os
import json
import requests

# --------- CONFIG ---------
app = Flask(__name__)
app.secret_key = "your_secret_key"

HF_API_KEY = "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"  # ✅ Your HuggingFace API key

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "chat_history.json")
USERS_FILE = os.path.join(BASE_DIR, "users.json")

# Create empty history file if not exists
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

# --------- INIT ---------
nlp = spacy.load("en_core_web_sm")

# --------- INTENT DETECTION ---------
def detect_intent(user_input):
    doc = nlp(user_input.lower())
    for token in doc:
        for intent, keywords in intent_keywords.items():
            if token.lemma_ in keywords:
                return intent
    return "unknown"

# --------- HUGGINGFACE FALLBACK ---------
def ask_huggingface_fallback(prompt):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    # Step 1: QA Model with FAQ as context
    qa_url = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
    context = " ".join([f"{k}: {v}" for k, v in faq_knowledge_base.items()])
    qa_body = {"inputs": {"question": prompt, "context": context}}

    try:
        qa_response = requests.post(qa_url, headers=headers, json=qa_body)
        qa_response.raise_for_status()
        qa_result = qa_response.json()

        if isinstance(qa_result, dict) and qa_result.get("answer") and qa_result["answer"].strip() not in ["", "unanswerable"]:
            return qa_result["answer"].strip()
    except Exception:
        pass  # If QA fails, fallback to text generation

    # Step 2: Text Generation Model
    tg_url = "https://api-inference.huggingface.co/models/google/flan-t5-base"
    tg_body = {"inputs": prompt}

    try:
        tg_response = requests.post(tg_url, headers=headers, json=tg_body)
        tg_response.raise_for_status()
        tg_result = tg_response.json()

        if isinstance(tg_result, list) and len(tg_result) > 0 and "generated_text" in tg_result[0]:
            return tg_result[0]["generated_text"].strip()
        elif isinstance(tg_result, dict) and "generated_text" in tg_result:
            return tg_result["generated_text"].strip()

        return "⚠️ Sorry, I couldn’t generate a valid response."
    except requests.exceptions.RequestException as e:
        return f"HuggingFace API error: {str(e)}"

# --------- CHATBOT LOGIC ---------
def analyze_question(user_input):
    # Intent responses
    intent = detect_intent(user_input)
    if intent in intent_responses:
        return intent_responses[intent]

    # Direct keyword match
    doc = nlp(user_input.lower())
    keywords = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]

    for keyword in keywords:
        if keyword in faq_knowledge_base:
            return faq_knowledge_base[keyword]

    # Fuzzy matching
    best_match, score = process.extractOne(user_input.lower(), faq_knowledge_base.keys())
    if score and score > 80:
        return faq_knowledge_base[best_match]

    # Fallback: HuggingFace
    return ask_huggingface_fallback(user_input)

# --------- SAVE HISTORY ---------
def save_message_to_history(sender, message):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as file:
                history = json.load(file)
        except json.JSONDecodeError:
            history = []
    history.append({"sender": sender, "message": message})
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

# --------- USER MANAGEMENT ---------
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def save_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = password
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)
    return True

def authenticate_user(username, password):
    users = load_users()
    return users.get(username) == password

# --------- ROUTES ---------
@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if authenticate_user(username, password):
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username") or request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if not username or not password or not confirm:
            return render_template("login.html", error="All fields are required")

        if password != confirm:
            return render_template("login.html", error="Passwords do not match")

        if save_user(username, password):
            return redirect(url_for("login"))
        else:
            return render_template("login.html", error="Username already exists")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/get_response", methods=["POST"])
def get_response():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    if request.content_type != "application/json":
        return jsonify({"error": "Use Content-Type: application/json"}), 415

    user_input = request.json.get("user_input")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        bot_response = analyze_question(user_input)
        save_message_to_history("user", user_input)
        save_message_to_history("bot", bot_response)
        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/history")
def chat_history():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as file:
            try:
                history = json.load(file)
            except json.JSONDecodeError:
                history = []
    else:
        history = []
    return render_template("history.html", history=history)

@app.route("/clear_history", methods=["POST"])
def clear_history():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        with open(HISTORY_FILE, "w") as file:
            json.dump([], file)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# --------- START APP ---------
if __name__ == "__main__":
    app.run(debug=True)
