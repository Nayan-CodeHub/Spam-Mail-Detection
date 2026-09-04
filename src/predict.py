import os
import joblib
from src.text_preprocessing import preprocess_text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "spam_classifier.pkl")

def predict_message(message):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not found. Run: python src/train_model.py")
    model = joblib.load(MODEL_PATH)
    prediction = model.predict([message])[0]
    probability = max(model.predict_proba([message])[0])
    return prediction, probability

if __name__ == "__main__":
    text = input("Enter a message: ")
    label, confidence = predict_message(text)
    print(f"Prediction: {label.upper()} ({confidence * 100:.1f}% confidence)")
