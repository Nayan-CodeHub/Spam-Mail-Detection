import os
import sys
import joblib
from flask import Flask, redirect, render_template, request, session, url_for

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "spam_classifier.pkl")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.gmail_client import create_oauth_flow, fetch_latest_messages, save_credentials, load_credentials

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-development-key")

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


def classify_message(model, message):
    prediction = model.predict([message])[0]
    confidence = max(model.predict_proba([message])[0]) * 100
    return ("SPAM" if prediction == "spam" else "HAM"), confidence

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    confidence = None
    message = ""

    if request.method == "POST":
        message = request.form.get("message", "").strip()
        model = load_model()

        if not message:
            result = "Please enter a message."
        elif model is None:
            result = "Model not trained yet. Run: python src/train_model.py"
        else:
            result, confidence = classify_message(model, message)

    return render_template(
        "index.html",
        result=result,
        confidence=confidence,
        message=message,
        gmail_connected=load_credentials() is not None,
    )


@app.route("/connect/gmail")
def connect_gmail():
    try:
        flow = create_oauth_flow(url_for("gmail_callback", _external=True))
    except FileNotFoundError:
        return render_template("gmail_setup.html")
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    session["oauth_state"] = state
    return redirect(authorization_url)


@app.route("/oauth2callback")
def gmail_callback():
    state = session.get("oauth_state")
    if not state:
        return "OAuth session expired. Return to the home page and try again.", 400
    if request.args.get("state") != state:
        session.pop("oauth_state", None)
        return "OAuth state validation failed. Start a new Gmail connection.", 400
    if request.args.get("error"):
        error_code = request.args.get("error")
        error_description = request.args.get("error_description", "No description provided")
        session.pop("oauth_state", None)
        return render_template(
            "gmail_setup.html",
            error=f"Google returned {error_code}: {error_description}",
        ), 400
    flow = create_oauth_flow(url_for("gmail_callback", _external=True), state=state)
    try:
        flow.fetch_token(code=request.args["code"])
    except Exception as error:
        app.logger.exception("Gmail OAuth callback failed")
        session.pop("oauth_state", None)
        return render_template(
            "gmail_setup.html",
            error=f"Google authorization failed ({type(error).__name__}). Check the test-user and redirect-URI settings, then try again.",
        ), 400
    save_credentials(flow.credentials)
    session.pop("oauth_state", None)
    return redirect(url_for("inbox"))


@app.route("/inbox")
def inbox():
    if load_credentials() is None:
        return redirect(url_for("connect_gmail"))
    model = load_model()
    if model is None:
        return render_template("inbox.html", error="Train the model before scanning your inbox.", messages=[])
    try:
        messages = fetch_latest_messages(limit=10)
        for message in messages:
            message["result"], message["confidence"] = classify_message(model, message["body"])
        return render_template("inbox.html", messages=messages, error=None)
    except Exception as error:
        return render_template("inbox.html", messages=[], error=f"Could not read Gmail: {error}")

if __name__ == "__main__":
    app.run(debug=True)
