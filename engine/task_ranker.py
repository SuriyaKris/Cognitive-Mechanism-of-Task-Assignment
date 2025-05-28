# engine/task_ranker.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.priority_tables import priority_tables
from engine.feedback_updater import fetch_priorities, insert_or_update_priority

# FER-2013 emotion labels
emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

def assign_task(role, fused_probs, employee_id=None):
    """
    Assigns the best task based on the employee's fused emotion probabilities.
    If employee-specific data does not exist, initializes it from global priorities.
    """

    task_scores = {}

    if employee_id:
        print(f"[INFO] Checking personalized priority table for employee {employee_id}...")

        # Check if employee already has data
        existing_data = []
        for emotion in emotion_labels:
            personalized_tasks = fetch_priorities(employee_id, emotion)  # returns list of (task, score)
            existing_data.extend(personalized_tasks)

        if not existing_data:
            print(f"[INFO] No personalized data found for {employee_id}. Initializing from general priority table...")

            # Copy general role table to employee-specific table
            if role not in priority_tables:
                raise ValueError(f"Role '{role}' not found in priority tables.")
            
            general_priority = priority_tables[role]

            for emotion, tasks in general_priority.items():
                for task_name, priority_score in tasks.items():
                    insert_or_update_priority(employee_id, emotion, task_name, priority_score)

            print(f"[INFO] Initialized personalized priority table for employee {employee_id}.")

        else:
            print(f"[INFO] Personalized data found for {employee_id}. Using updated priorities.")

        # Now fetch personalized data for assignment
        all_tasks = []
        for emotion in emotion_labels:
            personalized_tasks = fetch_priorities(employee_id, emotion)
            all_tasks.extend([(emotion, task, score) for task, score in personalized_tasks])

        # Calculate weighted scores
        for emotion, task_name, priority_score in all_tasks:
            emotion_index = emotion_labels.index(emotion)
            emotion_probability = fused_probs[emotion_index]
            weighted_score = emotion_probability * priority_score

            if task_name in task_scores:
                task_scores[task_name] += weighted_score
            else:
                task_scores[task_name] = weighted_score

    else:
        # If no employee ID, fallback to global static table
        task_scores = _calculate_from_global(role, fused_probs)

    best_task = max(task_scores, key=task_scores.get)
    best_score = task_scores[best_task]

    return best_task, best_score

def _calculate_from_global(role, fused_probs):
    """
    Internal helper: Calculate task scores from static global priority table.
    """
    if role not in priority_tables:
        raise ValueError(f"Role '{role}' not found in priority tables.")

    task_data = priority_tables[role]
    task_scores = {}

    for emotion, tasks in task_data.items():
        if emotion not in emotion_labels:
            continue
        emotion_index = emotion_labels.index(emotion)
        emotion_probability = fused_probs[emotion_index]

        for task_name, priority in tasks.items():
            weighted_score = emotion_probability * priority
            if task_name in task_scores:
                task_scores[task_name] += weighted_score
            else:
                task_scores[task_name] = weighted_score

    return task_scores
