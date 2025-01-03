from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from auth import sign_up, log_in
from chatbot import get_response
from datetime import datetime
import os
import speech_recognition as sr

app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)  # Secure random key for session management

message_history = {}

@app.route("/")
def home():
    return redirect(url_for("login"))  # Redirect to login page

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        result = log_in(username, password)  # Handle login logic
        if "successful" in result:
            session["username"] = username
            return redirect(url_for("index"))  # Redirect to the index page after login
        return render_template("login.html", message=result)  # Display error message
    return render_template("login.html")

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up_page():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        full_name = request.form["full_name"]
        result = sign_up(username, password, email, full_name)  # Handle signup logic
        return render_template("sign_up.html", message=result)  # Display success/error message
    return render_template("sign_up.html")

@app.route("/index")
def index():
    if "username" not in session:  # Ensure the user is logged in
        return redirect(url_for("login"))  # Redirect to login if not logged in
    return render_template("index.html", username=session["username"])


@app.route("/ai_assistant", methods=["GET", "POST"])
def ai_assistant():
    if "username" not in session:  # Ensure the user is logged in
        return redirect(url_for("login"))

    username = session["username"]
    
    # Initialize the current chat if not exists
    if 'current_chat' not in session:
        today_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session['current_chat'] = today_date

    chat_name = session['current_chat']
    
    # Initialize message history for the chat if not exists
    if chat_name not in message_history:
        message_history[chat_name] = []

    if request.method == "POST":
        user_message = request.form["user_message"]
        # Add user message to chat history
        message_history[chat_name].append(f"You: {user_message}")

        # Get AI response (replace with actual AI logic)
        ai_response = f"AI: I heard you say '{user_message}'. How can I assist further?"
        message_history[chat_name].append(ai_response)

    # Pass both message_history and chat_name to the template
    return render_template(
        "chatbot.html",
        message_history=message_history,
        chat_name=chat_name,
        messages=message_history.get(chat_name, [])
    )

@app.route("/chatbot", methods=["GET", "POST"])
@app.route("/chatbot/<chat_name>", methods=["GET", "POST"])
def chatbot(chat_name=None):
    if "username" not in session:
        return redirect(url_for("login"))

    if chat_name is None:
        if 'current_chat' not in session:
            today_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            session['current_chat'] = today_date  # Initialize current chat if not set
        chat_name = session['current_chat']

    # Ensure message history exists for the chat
    if chat_name not in message_history:
        message_history[chat_name] = []  # Initialize chat history if not set

    if request.method == "POST":
        user_message = request.form["message"]
        
        # Add the user's message to the chat history
        message_history[chat_name].append(f"You: {user_message}")

        # Simulate AI response (replace with actual AI logic, e.g., OpenAI, etc.)
        ai_response = get_response(user_message)  # Call your AI response function
        message_history[chat_name].append(f"AI: {ai_response}")

        # Store the response in the session (optional)
        session['message_history'] = message_history

    # Get the current date in "YYYY-MM-DD" format
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Pass the current date to the template along with message history
    return render_template(
        "chatbot.html",
        message_history=message_history,
        chat_name=chat_name,

        bot_response=message_history.get(chat_name, [])[-1] if message_history.get(chat_name) else None
    )

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    session.pop("current_chat", None)  # Clear current chat session
    return redirect(url_for("login"))


@app.route("/rename_chat/<chat_name>", methods=["GET"])
def rename_chat(chat_name):
    new_name = request.args.get('new_name')
    if new_name:
        if chat_name in message_history:
            if new_name in message_history:
                return redirect(url_for("chatbot", chat_name=chat_name, message="A chat with that name already exists."))
            else:
                # Rename the chat
                message_history[new_name] = message_history.pop(chat_name)
                return redirect(url_for("chatbot", chat_name=new_name))
        else:
            return redirect(url_for("chatbot", chat_name=chat_name, message="Chat not found."))
    return redirect(url_for("chatbot", chat_name=chat_name, message="Invalid new name."))

@app.route("/new_chat", methods=["GET"])
def new_chat():
    chat_name = "Chat" + str(len(message_history) + 1)
    message_history[chat_name] = []
    return redirect(url_for("chatbot", chat_name=chat_name))

# Download Chat Route
@app.route("/download_chat/<chat_name>")
def download_chat(chat_name):
    # Save the chat to a text file
    chat_file = f"{chat_name}.txt"
    with open(chat_file, "w") as f:
        for message in message_history[chat_name]:
            f.write(message + "\n")
    return send_file(chat_file, as_attachment=True)

# Delete Chat Route
@app.route("/delete_chat/<chat_name>")
def delete_chat(chat_name):
    if chat_name in message_history:
        del message_history[chat_name]
    return redirect(url_for("chatbot"))

# Speech-to-Text Route
@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            return jsonify({'text': text})
        except sr.UnknownValueError:
            return jsonify({'text': "Sorry, I couldn't understand what you said."})
        except sr.RequestError as e:
            return jsonify({'text': f"Error with the service: {e}"})

if __name__ == "__main__":
    app.run(debug=True)
