# Spam Mail Detector - Project Requirements

## 1. Objective

Build a text classification system that distinguishes between spam and non-spam (ham) messages.

## 2. Dataset Requirement

Use a public labeled text dataset. This project uses the UCI SMS Spam Collection:

- 5,574 labeled messages
- Labels: `spam` and `ham`
- File: `dataset/spam.csv`
- Required columns: `label`, `message`

The dataset is SMS-based, but it is accepted by the assignment because the SMS Spam Collection is one of the suggested public datasets.

## 3. Required Project Structure

```text
Spam-Mail-Detector/
├── app/
│   ├── app.py
│   └── templates/
│       └── index.html
├── dataset/
│   └── spam.csv
├── models/
│   ├── spam_classifier.pkl
│   └── confusion_matrix.png
├── src/
│   ├── __init__.py
│   ├── text_preprocessing.py
│   ├── train_model.py
│   └── predict.py
├── .vscode/
│   └── extensions.json
├── requirements.txt
├── README.md
└── PROJECT_REQUIREMENTS.md
```

## 4. Python Dependencies

The required packages are listed in `requirements.txt`:

- `pandas`: load and prepare the dataset
- `scikit-learn`: preprocessing, TF-IDF, model training, and evaluation
- `flask`: web interface
- `joblib`: save and load the trained model
- `matplotlib`: create the confusion-matrix chart
- `google-api-python-client`: read Gmail messages through the Gmail API
- `google-auth-oauthlib`: authenticate with Google OAuth

Recommended VS Code extensions:

- Python: `ms-python.python`
- Python Debugger: `ms-python.debugpy`

## 5. Machine Learning Workflow

1. Load messages and labels from `dataset/spam.csv`.
2. Remove rows with missing labels or messages.
3. Convert text to lowercase.
4. Tokenize alphabetic words.
5. Remove English stopwords.
6. Convert cleaned text into TF-IDF unigram and bigram features.
7. Split the data into stratified training and testing sets.
8. Train a Multinomial Naive Bayes classifier.
9. Measure accuracy, precision, recall, F1-score, and the confusion matrix.
10. Save the trained model and confusion-matrix image in `models/`.
11. Use the Flask application to classify new messages.

Optional Gmail workflow:

1. Add a Google OAuth Web-application file named `credentials.json` to the project root, with `http://127.0.0.1:5000/oauth2callback` as an authorized redirect URI.
2. Enable the Gmail API in Google Cloud Console.
3. Click `Connect Gmail` in the web app.
4. Approve read-only access.
5. Review the latest inbox messages and their spam/ham predictions.

The Gmail integration only requests `gmail.readonly` access. It does not send, delete, or modify email, and it does not establish that a message is genuinely authentic.

## Public Deployment Requirements

The local version supports switching between accounts by storing each account's token separately. Before making the site public:

- Deploy Flask behind HTTPS with a production WSGI server.
- Set a strong random `FLASK_SECRET_KEY` environment variable.
- Replace local token files with an encrypted server-side database keyed by the Google user ID.
- Configure the deployed HTTPS OAuth callback URI in Google Cloud.
- Move the OAuth consent screen to Production and complete Google verification for Gmail access.
- Never commit `credentials.json`, access tokens, or client secrets.

## 6. Running the Project

From the project root, create and activate a virtual environment:

```text
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```text
pip install -r requirements.txt
```

Train the model:

```text
python -m src.train_model
```

Run a command-line prediction:

```text
python -m src.predict
```

Start the web application:

```text
python app\app.py
```

Open the application at:

```text
http://127.0.0.1:5000
```

## 7. Expected Evaluation Output

The current full-dataset run reports approximately:

```text
Accuracy : 0.97
Precision: 1.00
Recall   : 0.75
F1 Score : 0.86
```

The exact values can vary if the dataset, test split, or model configuration changes.

## 8. Submission Evidence

Include these items in the final submission:

- Source code and project structure
- Dataset source and format description
- `requirements.txt`
- Training output with evaluation metrics
- Confusion-matrix image
- Screenshot of the Flask interface
- Example spam and ham predictions
- A limitation note explaining that some spam messages may be classified as ham
