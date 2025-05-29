# Cognitive-Mechanism-of-Task-Assignment
The Cognitive Mechanism of Task Assignment is a system that uses multimodal emotion recognition and cognitive computing to enhance workplace productivity. The system gets facial, text and speech in real time for emotion detection and then recommends task dynamically based on priority given to each tasks for each emotion.
This project is an intelligent system that detects employee emotions in real-time using multimodal inputs—text, speech, and facial expressions—to recommend personalized work tasks. Inspired by human cognitive adaptability, the system dynamically suggests tasks aligned with the emotional state of the user, enhancing productivity and well-being in professional environments.

🚀 Features
🎯 Real-time multimodal emotion detection using:

Text analysis (NLP-based)

Speech emotion recognition

Facial expression analysis (CNN-based)

✅ Personalized task recommendation based on detected emotions and past behavior.

🗂️ Employee profile and job role integration for context-aware recommendations.

🧠 System learns from employee task choices over time to refine future suggestions.

👥 HR Dashboard for:

Reviewing completed tasks

Rating employee performance

👨‍💼 HR Dashboard
HR can log in using secure credentials to:

View completed employee tasks

Assign performance ratings (1 to 5)

Update employee-specific task preferences

Analyze general task priority tables by job role



Viewing personalized and general priority tables

Download or Place Pretrained Models
Place your pretrained facial emotion recognition model inside the models/ directory.
models/fer_resnet18.pth


📌 Notes
This system is designed to be adaptive—it updates preferences based on employee choices and HR feedback.

Emotion detection works in real-time using webcam and microphone inputs.

All task interactions and emotion labels are stored in a local SQLite database for continuous learning.


🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss your ideas.

