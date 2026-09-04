import os
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
from src.text_preprocessing import preprocess_text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "dataset", "spam.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "spam_classifier.pkl")
CONFUSION_MATRIX_PATH = os.path.join(MODEL_DIR, "confusion_matrix.png")

df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=["label", "message"])
df["label"] = df["label"].str.lower().str.strip()
df["message"] = df["message"].astype(str).str.lower()

X_train, X_test, y_train, y_test = train_test_split(
    df["message"], df["label"], test_size=0.25, random_state=42, stratify=df["label"]
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        tokenizer=preprocess_text,
        preprocessor=None,
        token_pattern=None,
        lowercase=False,
        ngram_range=(1, 2),
    )),
    ("classifier", MultinomialNB())
])

model.fit(X_train, y_train)
predictions = model.predict(X_test)

print("\n=== Spam Mail Detector Evaluation ===")
print(f"Accuracy : {accuracy_score(y_test, predictions):.2f}")
print(f"Precision: {precision_score(y_test, predictions, pos_label="spam", zero_division=0):.2f}")
print(f"Recall   : {recall_score(y_test, predictions, pos_label="spam", zero_division=0):.2f}")
print(f"F1 Score : {f1_score(y_test, predictions, pos_label="spam", zero_division=0):.2f}")
print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))
print("Confusion Matrix:")
matrix = confusion_matrix(y_test, predictions, labels=["ham", "spam"])
print(matrix)

ConfusionMatrixDisplay(
    confusion_matrix=matrix,
    display_labels=["Ham", "Spam"],
).plot(cmap="Blues")
plt.title("Spam Mail Detector Confusion Matrix")
plt.tight_layout()

os.makedirs(MODEL_DIR, exist_ok=True)
plt.savefig(CONFUSION_MATRIX_PATH, dpi=150)
plt.close()
joblib.dump(model, MODEL_PATH)
print(f"\nModel saved to: {MODEL_PATH}")
print(f"Confusion matrix saved to: {CONFUSION_MATRIX_PATH}")
