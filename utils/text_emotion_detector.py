# utils/text_emotion_detector.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

# Define FER-2013 emotion labels
fer_emotion_labels = ['angry', 'happy', 'fear', 'disgust', 'sad', 'surprise', 'neutral']

# Load pre-trained text emotion model
def load_text_emotion_model(model_name="nateraw/bert-base-uncased-emotion"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()
    return model, tokenizer

# Predict emotion probabilities from text
def predict_emotion_from_text(model, tokenizer, text_input):
    inputs = tokenizer(text_input, return_tensors="pt", truncation=True)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1).cpu().numpy().flatten()

    # Handle mismatch: map output to FER-2013 7 classes
    # The model may have more classes, so we truncate or pad to 7
    if len(probabilities) > 7:
        probabilities = probabilities[:7]
    elif len(probabilities) < 7:
        probabilities = np.pad(probabilities, (0, 7 - len(probabilities)), 'constant')

    return probabilities.tolist()
