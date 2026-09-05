# Spam Mail Detector

A beginner-friendly machine learning project that classifies text messages as **Spam** or **Ham (Not Spam)** using TF-IDF and Multinomial Naive Bayes.

## Features
- Text cleaning and preprocessing
- TF-IDF feature extraction
- Multinomial Naive Bayes classifier
- Accuracy, precision, recall and F1-score
- Confusion matrix
- Saved confusion-matrix chart
- Flask web interface
- Read-only Gmail inbox scanning with OAuth
- Model persistence using Joblib

## Project Structure
```text
Spam-Mail-Detector/
├── app/
│   ├── app.py
│   └── templates/
│       ├── gmail_setup.html
│       ├── inbox.html
│       └── index.html
├── dataset/
│   └── spam.csv
├── models/
│   ├── spam_classifier.pkl
│   └── confusion_matrix.png
├── src/
│   ├── __init__.py
│   ├── gmail_client.py
│   ├── text_preprocessing.py
│   ├── train_model.py
│   └── predict.py
├── requirements.txt
└── README.md
```

## Setup in VS Code
1. Open this folder in VS Code.
2. Open the terminal.
3. Create a virtual environment:
   `python -m venv .venv`
4. Activate it:
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`
   - Windows CMD: `.venv\Scripts\activate`
5. Install packages:
   `pip install -r requirements.txt`
6. Train the model:
   `python src/train_model.py`
7. Start the web app:
   `python app/app.py`
8. Open the local address shown in the terminal.

## Dataset
The project uses the public [SMS Spam Collection dataset](https://archive.ics.uci.edu/dataset/228/sms+spam+collection), with 5,574 messages and columns named `label` and `message`.

## Machine Learning Workflow
1. Load messages and `spam`/`ham` labels from the CSV.
2. Lowercase each message, tokenize alphabetic words, and remove English stopwords.
3. Convert the cleaned tokens into TF-IDF features, including unigrams and bigrams.
4. Split the data into stratified training and test sets.
5. Train a Multinomial Naive Bayes classifier.
6. Report accuracy, precision, recall, F1-score, and the confusion matrix.
7. Save the classifier and confusion-matrix chart in `models/`.

Run the training and command-line predictor as modules from the project root:

```text
python -m src.train_model
python -m src.predict
```

The full dataset provides a more meaningful evaluation than a small demonstration sample. Keep the test split and random seed unchanged when reporting results so the evaluation remains reproducible.

## Example
Input:
`Congratulations! You won a free prize. Click now!`

Expected result:
`SPAM`

Input:
`Can you send me the notes after class?`

Expected result:
`HAM`

## Gmail Inbox Scanning

The web app can optionally connect to Gmail and classify the latest inbox messages. It uses Google OAuth with the read-only Gmail scope; it never sends, deletes, or changes email.

1. Enable the Gmail API in Google Cloud Console.
2. Create OAuth credentials for a Web application and add `http://127.0.0.1:5000/oauth2callback` as an authorized redirect URI.
3. Download the JSON file, rename it to `credentials.json`, and place it in the project root beside `requirements.txt`.
4. Install the updated requirements and start the app.
5. Click `Connect Gmail` and complete Google's consent flow.
6. Review the results at `Open Gmail inbox`.

The OAuth file and saved token are excluded by `.gitignore`. The classifier identifies messages as likely spam or ham; it does not prove sender identity or that a message is authentic.

### Multiple Users and Public Deployment

Each authorized Google account is stored under a separate hashed token filename, so switching accounts locally does not reuse the previous user's Gmail token. For a real public deployment, do not use local files as the permanent token store. Use a server-side database with encryption at rest, secure cookies, a randomly generated `FLASK_SECRET_KEY`, HTTPS, and a production WSGI server.

In Google Cloud, move the OAuth consent screen from Testing to Production and complete Google's verification requirements for Gmail scopes before allowing general public users. The local `127.0.0.1` redirect URI is for development only; a deployed site needs its own HTTPS callback URI.
