import pandas as pd
import numpy as np
import pickle
import nltk
from nltk.corpus import stopwords
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

# Download NLTK stopwords if not available
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = re.sub(r'[^\w\s]', '', str(text))
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in stop_words])
    return text

def create_dummy_dataset():
    """Load the ISOT Fake News Dataset from True.csv and Fake.csv."""
    print("Loading ISOT dataset...")
    
    # Load True news (real news, label 1)
    try:
        true_df = pd.read_csv('True.csv')
        true_df['label'] = 1  # Real news
    except FileNotFoundError:
        print("True.csv not found. Please download the ISOT Fake News Dataset from Kaggle and place True.csv in the current directory.")
        return pd.DataFrame(columns=['text', 'label'])
    
    # Load Fake news (fake news, label 0)
    try:
        fake_df = pd.read_csv('Fake.csv')
        fake_df['label'] = 0  # Fake news
    except FileNotFoundError:
        print("Fake.csv not found. Please download the ISOT Fake News Dataset from Kaggle and place Fake.csv in the current directory.")
        return pd.DataFrame(columns=['text', 'label'])
    
    # Combine the datasets
    df = pd.concat([true_df[['text', 'label']], fake_df[['text', 'label']]], ignore_index=True)
    
    print(f"Dataset loaded: {len(df)} samples ({len(fake_df)} fake, {len(true_df)} real)")
    return df

def train():
    df = create_dummy_dataset()
    
    print("Cleaning text...")
    df['clean_text'] = df['text'].apply(clean_text)

    X = df['clean_text']
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Vectorizing text...")
    vectorizer = TfidfVectorizer(max_features=5000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("Training Logistic Regression model...")
    model = LogisticRegression()
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    print(f"Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")

    # Save model and vectorizer
    print("Saving model and vectorizer...")
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)

    print("Training complete!")

if __name__ == '__main__':
    train()
