from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load model functions
from utils.facial_emotion_detector import predict_emotion_from_face, load_facial_emotion_model
from utils.speech_emotion_detector import predict_emotion_from_speech, load_speech_emotion_model
from utils.text_emotion_detector import predict_emotion_from_text, load_text_emotion_model
from engine.fusion_engine import fuse_emotions
from engine.task_ranker import assign_task
from engine.feedback_updater import update_priority_based_on_feedback
from data.priority_tables import priority_table_developer, priority_table_devops, priority_table_designer

app = Flask(__name__)
app.secret_key = "your-secret-key"  

# Load models once
facial_model = load_facial_emotion_model()
speech_model, speech_processor = load_speech_emotion_model()
text_model, text_tokenizer = load_text_emotion_model()

emotion_labels = ['angry', 'happy', 'fear', 'disgust', 'sad', 'surprise', 'neutral']

# DB Initialization
def initialize_role_db():
    if not os.path.exists("data"):
        os.makedirs("data")
    conn = sqlite3.connect("data/employee_roles.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_roles (
            employee_id TEXT PRIMARY KEY,
            role TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def initialize_completed_task_db():
    conn = sqlite3.connect("data/completed_tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS completed_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            task TEXT,
            emotion TEXT,
            timestamp TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()

initialize_role_db()
initialize_completed_task_db()

#  get role from database
def get_role(employee_id):
    conn = sqlite3.connect("data/employee_roles.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM employee_roles WHERE employee_id = ?", (employee_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Route: Login Page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        employee_id = request.form["employee_id"].strip()
        conn = sqlite3.connect("data/employee_roles.db")
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM employee_roles WHERE employee_id = ?", (employee_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return redirect(url_for("emotion_input", employee_id=employee_id))
        else:
            return redirect(url_for("select_role", employee_id=employee_id))
    return render_template("login.html")

# Route: Select Role
@app.route("/select-role/<employee_id>", methods=["GET", "POST"])
def select_role(employee_id):
    if request.method == "POST":
        selected_role = request.form["role"]
        conn = sqlite3.connect("data/employee_roles.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO employee_roles (employee_id, role) VALUES (?, ?)", (employee_id, selected_role))
        conn.commit()
        conn.close()
        return redirect(url_for("emotion_input", employee_id=employee_id))
    return render_template("role_select.html", employee_id=employee_id)

# Route: Emotion Input and Task Assignment
@app.route("/emotion-input/<employee_id>", methods=["GET", "POST"])
def emotion_input(employee_id):
    if request.method == "POST":
        text_input = request.form["text_input"]
        text_probs = predict_emotion_from_text(text_model, text_tokenizer, text_input)
        face_probs = predict_emotion_from_face(facial_model)
        speech_probs = predict_emotion_from_speech(speech_model, speech_processor)
        fused_probs = fuse_emotions(face_probs, speech_probs, text_probs)
        role = get_role(employee_id)
        task, score = assign_task(role=role, fused_probs=fused_probs, employee_id=employee_id)
        emotion_vector = list(zip(emotion_labels, fused_probs))
        dominant_emotion = emotion_labels[fused_probs.index(max(fused_probs))]
        return render_template("task_assigned.html",
                               employee_id=employee_id,
                               emotion_vector=emotion_vector,
                               task=task,
                               score=round(score, 4),
                               dominant_emotion=dominant_emotion)
    return render_template("emotion_input.html", employee_id=employee_id)

# Route: Mark task completed
@app.route("/task-completed/<employee_id>/<task>", methods=["POST"])
def mark_completed(employee_id, task):
    emotion = request.form.get("emotion")
    conn = sqlite3.connect("data/completed_tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO completed_tasks (employee_id, task, emotion, timestamp, status)
        VALUES (?, ?, ?, ?, ?)
    """, (employee_id, task, emotion, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "pending"))
    conn.commit()
    conn.close()
    return render_template("task_completed.html", employee_id=employee_id, task=task)


# HR Login
HR_USERNAME = "admin"
HR_PASSWORD = "admin123"

@app.route("/hr-login", methods=["GET", "POST"])
def hr_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == HR_USERNAME and password == HR_PASSWORD:
            session["hr_logged_in"] = True
            return redirect(url_for("hr_dashboard"))
        else:
            return render_template("hr_login.html", error="Invalid credentials")
    return render_template("hr_login.html")

# HR Logout
@app.route("/hr-logout")
def hr_logout():
    session.pop("hr_logged_in", None)
    return redirect(url_for("hr_login"))

# HR Dashboard
@app.route("/hr-dashboard")
def hr_dashboard():
    if not session.get("hr_logged_in"):
        return redirect(url_for("hr_login"))
    conn = sqlite3.connect("data/completed_tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, employee_id, task, emotion, timestamp
        FROM completed_tasks
        WHERE status = 'pending'
        ORDER BY timestamp DESC
    """)
    tasks = cursor.fetchall()
    conn.close()
    return render_template("hr_dashboard.html", tasks=tasks)

# Rate a Task
@app.route("/rate-task/<int:task_id>", methods=["GET", "POST"])
def rate_task(task_id):
    if not session.get("hr_logged_in"):
        return redirect(url_for("hr_login"))

    if request.method == "POST":
        rating = int(request.form["rating"])
        employee_id = request.form["employee_id"]
        task = request.form["task"]
        emotion = request.form["emotion"]
        update_priority_based_on_feedback(employee_id, emotion, task, rating)
        conn = sqlite3.connect("data/completed_tasks.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE completed_tasks SET status = 'rated' WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("hr_dashboard"))

    conn = sqlite3.connect("data/completed_tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id, task, emotion, timestamp FROM completed_tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    return render_template("rate_task.html", task_id=task_id, task=task)

# View Priorities
@app.route("/view-priorities/<employee_id>")
def view_priorities(employee_id):
    if not session.get("hr_logged_in"):
        return redirect(url_for("hr_login"))
    conn = sqlite3.connect("data/employee_priority.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT emotion, task, score
        FROM employee_priority_table
        WHERE employee_id = ?
        ORDER BY emotion, score DESC
    """, (employee_id,))
    results = cursor.fetchall()
    conn.close()
    return render_template("employee_priority_view.html", employee_id=employee_id, priorities=results)

# View Task History
@app.route("/employee-history/<employee_id>")
def employee_history(employee_id):
    if not session.get("hr_logged_in"):
        return redirect(url_for("hr_login"))

    conn = sqlite3.connect("data/completed_tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT task, emotion, timestamp, status
        FROM completed_tasks
        WHERE employee_id = ?
        ORDER BY timestamp DESC
    """, (employee_id,))
    history = cursor.fetchall()
    conn.close()

    return render_template("employee_history.html", employee_id=employee_id, history=history)

# View General Priority Table
@app.route("/general-priority")
def general_priority():
    if not session.get("hr_logged_in"):
        return redirect(url_for("hr_login"))

    return render_template("general_priority.html",
        dev=priority_table_developer,
        devops=priority_table_devops,
        designer=priority_table_designer)

@app.route("/hr-dashboard-extended", methods=["GET", "POST"])
def hr_dashboard_extended():
    if not session.get("hr_logged_in"):
        return redirect(url_for("hr_login"))

    conn = sqlite3.connect("data/employee_roles.db")
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id FROM employee_roles ORDER BY employee_id")
    employees = [row[0] for row in cursor.fetchall()]
    conn.close()

    selected_id = None
    history = []
    priorities = []

    if request.method == "POST":
        selected_id = request.form.get("employee_id")

        # Fetch task history
        conn = sqlite3.connect("data/completed_tasks.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT task, emotion, timestamp, status
            FROM completed_tasks
            WHERE employee_id = ?
            ORDER BY timestamp DESC
        """, (selected_id,))
        history = cursor.fetchall()
        conn.close()

        # Fetch priorities
        conn = sqlite3.connect("data/employee_priority.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT emotion, task, score
            FROM employee_priority_table
            WHERE employee_id = ?
            ORDER BY emotion, score DESC
        """, (selected_id,))
        priorities = cursor.fetchall()
        conn.close()

    return render_template("hr_dashboard_extended.html",
                           employees=employees,
                           selected_id=selected_id,
                           history=history,
                           priorities=priorities)


if __name__ == "__main__":
    app.run(debug=True)
