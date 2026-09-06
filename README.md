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
   `python -m src.train_model`
7. Start the web app:
   `python app/app.py`
8. Open `http://127.0.0.1:5000` in your browser. Use `127.0.0.1` rather than `localhost` so the local OAuth callback matches the registered redirect URI.

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
4. If the OAuth consent screen is in Testing mode, add each account that will connect under **Test users**.
5. Install the requirements and start the app.
6. Open `http://127.0.0.1:5000`, click `Connect Gmail`, and complete Google's consent flow.
7. Review the results at `Open Gmail inbox`.

The OAuth file and saved token are excluded by `.gitignore`. The classifier identifies messages as likely spam or ham; it does not prove sender identity or that a message is authentic.

## Public Deployment with Render

The repository includes `Procfile` and `render.yaml` for deployment on Render.

1. Push the repository to GitHub.
2. Create a Render account and choose **New + → Web Service**.
3. Connect `Nayan-CodeHub/Spam-Mail-Detection`.
4. Use the build command `pip install -r requirements.txt && python -m src.train_model` and start command `gunicorn app.app:app`. The build command trains the classifier because model files are excluded from Git.
5. In Render, add a secret file at `/etc/secrets/credentials.json` containing the Google OAuth Web client JSON. Do not commit this file to GitHub.
6. Set `FLASK_SECRET_KEY` to a long random value. Set `GOOGLE_CREDENTIALS_PATH=/etc/secrets/credentials.json`.
7. Enable the Gmail API in the same Google Cloud project as the OAuth client.
8. After Render gives you an HTTPS URL, add `https://YOUR-RENDER-DOMAIN.onrender.com/oauth2callback` to the Google OAuth client redirect URIs.
9. Update the OAuth consent screen and complete Google verification before allowing general public users.

For a real public service, move the per-user Gmail tokens from local files into an encrypted persistent database. Render's normal filesystem is ephemeral, so local token files can be lost when the service restarts. The current file-based storage is suitable for local development or a limited demonstration deployment only.

### Multiple Users and Public Deployment

Each authorized Google account is stored under a separate hashed token filename, so switching accounts locally does not reuse the previous user's Gmail token. For a real public deployment, do not use local files as the permanent token store. Use a server-side database with encryption at rest, secure cookies, a randomly generated `FLASK_SECRET_KEY`, HTTPS, and a production WSGI server.

In Google Cloud, move the OAuth consent screen from Testing to Production and complete Google's verification requirements for Gmail scopes before allowing general public users. The local `127.0.0.1` redirect URI is for development only; a deployed site needs its own HTTPS callback URI.
