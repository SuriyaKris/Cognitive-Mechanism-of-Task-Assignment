# utils/facial_emotion_detector.py

import torch
import torch.nn as nn
import torchvision.transforms as transforms
import cv2
import numpy as np

# Load ResNet18 model
def load_facial_emotion_model(model_path='models/fer_resnet18.pth'):
    model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=False)
    model.fc = nn.Linear(model.fc.in_features, 7)  # 7 emotion classes
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

# Predict emotion from webcam when user presses any key
def predict_emotion_from_face(model):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Webcam could not be accessed!")

    print("\n[INFO] Webcam is ON. Press any key to capture the frame...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            continue

        cv2.imshow("Press any key to capture", frame)
        if cv2.waitKey(1) & 0xFF != 255:  # 255 = no key pressed
            break

    cap.release()
    cv2.destroyAllWindows()

    # Preprocess frame
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((48, 48)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])

    img = transform(frame)
    img = img.unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        outputs = model(img)
        probabilities = torch.softmax(outputs, dim=1).cpu().numpy().flatten()

    return probabilities.tolist()
