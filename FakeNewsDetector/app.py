from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
import numpy as np
import nltk
from nltk.corpus import stopwords
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Load model and vectorizer safely
MODEL_PATH = 'model.pkl'
VEC_PATH = 'vectorizer.pkl'

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(VEC_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    print("Model and Vectorizer loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    vectorizer = None

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

def get_top_features(text, vectorizer, model, n=3):
    """Extract which words influenced the decision the most."""
    cleaned = clean_text(text)
    words = cleaned.split()
    
    if not words:
        return []
        
    vec = vectorizer.transform([cleaned])
    
    # Get indices of words present in the text
    feature_names = np.array(vectorizer.get_feature_names_out())
    # Find nonzero elements in the vector
    nonzero_indices = vec.nonzero()[1]
    
    if len(nonzero_indices) == 0:
        return []

    # Get coefficients for these words
    coeffs = model.coef_[0]
    word_scores = []
    
    for idx in nonzero_indices:
        word = feature_names[idx]
        score = coeffs[idx]
        word_scores.append((word, score))
    
    # If prediction is Real (label 1), higher positive score means more influence
    # If prediction is Fake (label 0), higher negative score means more influence
    
    # Sort by absolute influence
    word_scores.sort(key=lambda x: abs(x[1]), reverse=True)
    
    return [word for word, score in word_scores[:n]]

@app.route('/predict', methods=['POST'])
def predict():
    if model is None or vectorizer is None:
        return jsonify({"error": "Model not loaded. Please train the model first."}), 500

    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']
    
    if not text.strip():
        return jsonify({"error": "Empty text"}), 400

    cleaned = clean_text(text)
    if not cleaned.strip():
        return jsonify({
            "prediction": "Unknown",
            "confidence": 0,
            "explanation": "Text contains only stopwords or punctuation."
        })

    # Vectorize
    vec = vectorizer.transform([cleaned])
    
    # Predict
    prediction = model.predict(vec)[0]
    probabilities = model.predict_proba(vec)[0]
    
    # 0 = Fake, 1 = Real
    pred_label = "Real News" if prediction == 1 else "Fake News"
    confidence = float(probabilities[prediction]) * 100
    
    # Get explanation (top keywords)
    top_words = get_top_features(text, vectorizer, model)
    explanation = f"Key indicators: {', '.join(top_words)}" if top_words else "No significant keywords found."

    return jsonify({
        "prediction": pred_label,
        "confidence": round(confidence, 2),
        "explanation": explanation
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
