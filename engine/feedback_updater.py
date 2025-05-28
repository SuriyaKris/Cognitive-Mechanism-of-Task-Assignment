# engine/feedback_updater.py

import sqlite3
import os

DB_PATH = "data/employee_priority.db"

# Initialize the database (only once)
def initialize_database():
    if not os.path.exists("data"):
        os.makedirs("data")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_priority_table (
            employee_id TEXT,
            emotion TEXT,
            task TEXT,
            score REAL,
            PRIMARY KEY (employee_id, emotion, task)
        )
    """)
    conn.commit()
    conn.close()

# Insert or Update a task score
def insert_or_update_priority(employee_id, emotion, task, score):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO employee_priority_table (employee_id, emotion, task, score)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(employee_id, emotion, task) DO UPDATE SET score=excluded.score
    """, (employee_id, emotion, task, score))

    conn.commit()
    conn.close()

# Fetch priorities for an employee and a given emotion
def fetch_priorities(employee_id, emotion):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT task, score FROM employee_priority_table
        WHERE employee_id = ? AND emotion = ?
        ORDER BY score DESC
    """, (employee_id, emotion))

    results = cursor.fetchall()
    conn.close()
    return results

# Update task score based on feedback
def update_priority_based_on_feedback(employee_id, emotion, task, rating, alpha=0.1):
    conn = sqlite3.connect("data/employee_priority.db")
    cursor = conn.cursor()

    # Normalize rating to 0–1
    normalized_rating = rating / 5.0

    # Get current priority
    cursor.execute("""
        SELECT score FROM employee_priority_table
        WHERE employee_id = ? AND emotion = ? AND task = ?
    """, (employee_id, emotion, task))
    result = cursor.fetchone()

    if result:
        old_score = result[0]
        new_score = old_score + alpha * (normalized_rating - old_score)

        cursor.execute("""
            UPDATE employee_priority_table
            SET score = ?
            WHERE employee_id = ? AND emotion = ? AND task = ?
        """, (new_score, employee_id, emotion, task))
    else:
        # Fallback: if task not found (should not happen)
        cursor.execute("""
            INSERT INTO employee_priority_table (employee_id, emotion, task, score)
            VALUES (?, ?, ?, ?)
        """, (employee_id, emotion, task, normalized_rating))

    conn.commit()
    conn.close()

