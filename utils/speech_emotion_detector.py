# utils/speech_emotion_detector.py

import torch
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
import sounddevice as sd
import numpy as np

# FER-2013 compatible emotion order
emotion_labels = ['angry', 'happy', 'fear', 'disgust', 'sad', 'surprise', 'neutral']

# Load the real pretrained model from Huggingface
def load_speech_emotion_model(model_name="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"):
    processor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
    model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)
    model.eval()
    return model, processor

# Record 10 seconds of audio
def record_audio(duration=10, sample_rate=16000):
    print("\n[INFO] Recording 10 seconds of audio...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    recording = recording.flatten()
    return recording, sample_rate

# Predict emotion probabilities using the pretrained model
def predict_emotion_from_speech(model, processor):
    audio, sample_rate = record_audio()

    inputs = processor(audio, sampling_rate=sample_rate, return_tensors="pt", padding=True)

    with torch.no_grad():
        logits = model(**inputs).logits
        probabilities = torch.softmax(logits, dim=-1).cpu().numpy().flatten()

    # Ensure the probabilities are mapped to 7 emotions (truncate or pad if needed)
    if len(probabilities) > 7:
        probabilities = probabilities[:7]
    elif len(probabilities) < 7:
        probabilities = np.pad(probabilities, (0, 7 - len(probabilities)), 'constant')

    return probabilities.tolist()
