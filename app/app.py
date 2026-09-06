import os
import sys
import joblib
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "spam_classifier.pkl")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.gmail_client import clear_credentials, create_oauth_flow, fetch_latest_messages, get_user_identity, save_credentials, load_credentials

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-development-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

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
        gmail_connected=load_credentials(session.get("gmail_user_id")) is not None,
    )


@app.route("/connect/gmail")
def connect_gmail():
    if request.host == "localhost:5000":
        return redirect("http://127.0.0.1:5000/connect/gmail")
    try:
        flow = create_oauth_flow(url_for("gmail_callback", _external=True))
    except FileNotFoundError:
        return render_template("gmail_setup.html", error="Google OAuth credentials are missing on the server.")
    except ValueError:
        return render_template("gmail_setup.html", error="The server's credentials.json is not valid JSON. Replace the Render secret file with the downloaded Google OAuth JSON.")
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    session["oauth_state"] = state
    session["oauth_code_verifier"] = flow.code_verifier
    return redirect(authorization_url)


@app.route("/oauth2callback")
def gmail_callback():
    state = session.get("oauth_state")
    code_verifier = session.get("oauth_code_verifier")
    if not state or not code_verifier:
        return "OAuth session expired. Return to the home page and try again.", 400
    if request.args.get("state") != state:
        session.pop("oauth_state", None)
        session.pop("oauth_code_verifier", None)
        return "OAuth state validation failed. Start a new Gmail connection.", 400
    if request.args.get("error"):
        error_code = request.args.get("error")
        error_description = request.args.get("error_description", "No description provided")
        session.pop("oauth_state", None)
        session.pop("oauth_code_verifier", None)
        return render_template(
            "gmail_setup.html",
            error=f"Google returned {error_code}: {error_description}",
        ), 400
    flow = create_oauth_flow(url_for("gmail_callback", _external=True), state=state)
    flow.code_verifier = code_verifier
    try:
        flow.fetch_token(code=request.args["code"])
    except Exception as error:
        app.logger.exception("Gmail OAuth callback failed")
        session.pop("oauth_state", None)
        session.pop("oauth_code_verifier", None)
        return render_template(
            "gmail_setup.html",
            error=f"Google authorization failed ({type(error).__name__}). Check the test-user and redirect-URI settings, then try again.",
        ), 400
    gmail_user_id, gmail_email = get_user_identity(flow.credentials)
    save_credentials(flow.credentials, gmail_user_id)
    session["gmail_user_id"] = gmail_user_id
    session["gmail_email"] = gmail_email
    session.pop("oauth_state", None)
    session.pop("oauth_code_verifier", None)
    return redirect(url_for("inbox"))


@app.route("/inbox")
def inbox():
    if load_credentials(session.get("gmail_user_id")) is None:
        return redirect(url_for("connect_gmail"))
    model = load_model()
    if model is None:
        return render_template("inbox.html", error="Train the model before scanning your inbox.", messages=[])
    try:
        messages = fetch_latest_messages(session["gmail_user_id"], limit=10)
        for message in messages:
            message["result"], message["confidence"] = classify_message(model, message["body"])
        return render_template("inbox.html", messages=messages, error=None)
    except Exception as error:
        return render_template("inbox.html", messages=[], error=f"Could not read Gmail: {error}")


@app.route("/disconnect/gmail", methods=["POST"])
def disconnect_gmail():
    clear_credentials(session.get("gmail_user_id"))
    session.pop("gmail_user_id", None)
    session.pop("gmail_email", None)
    session.pop("oauth_state", None)
    session.pop("oauth_code_verifier", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
