"""
Firebase Firestore client wrapper for the 30-Day Habit Tracker.
Handles all database operations for habits, progress, and reports.
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
from utils.constants import (
    CHALLENGE_DURATION, STATUS_ACTIVE, STATUS_COMPLETED,
    GOOD_HABIT, BAD_HABIT, TIMEZONE
)


# ─── Initialization ──────────────────────────────────────────────────

_db = None


def initialize_firebase():
    """
    Initialize the Firebase Admin SDK.
    Supports two methods:
      1. FIREBASE_CREDENTIALS env var — JSON string (for Railway)
      2. FIREBASE_CREDENTIALS_FILE env var — path to JSON file (for local dev)
    """
    global _db

    cred = None

    # Method 1: JSON file path (easier for local development)
    cred_file = os.getenv("FIREBASE_CREDENTIALS_FILE")
    if cred_file and os.path.exists(cred_file):
        cred = credentials.Certificate(cred_file)
        print(f"🔑 Using Firebase credentials from file: {cred_file}")

    # Method 2: Inline JSON string (for Railway / production)
    if cred is None:
        cred_json = os.getenv("FIREBASE_CREDENTIALS")
        if not cred_json:
            raise ValueError(
                "Firebase credentials not found. Set either:\n"
                "  • FIREBASE_CREDENTIALS_FILE = path to your JSON key file\n"
                "  • FIREBASE_CREDENTIALS = full JSON string of the key"
            )
        try:
            cred_dict = json.loads(cred_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"FIREBASE_CREDENTIALS is not valid JSON: {e}")
        cred = credentials.Certificate(cred_dict)
        print("🔑 Using Firebase credentials from environment variable.")

    firebase_admin.initialize_app(cred)
    _db = firestore.client()
    print("✅ Firebase Firestore initialized successfully.")
    return _db


def get_db():
    """Get the Firestore client instance."""
    global _db
    if _db is None:
        _db = initialize_firebase()
    return _db


# ─── Habit CRUD ──────────────────────────────────────────────────────

def create_habit(user_id: str, habit_name: str, habit_type: str) -> dict:
    """
    Create a new 30-day habit challenge for a user.

    Args:
        user_id: Discord user ID
        habit_name: Name of the habit
        habit_type: 'good' or 'bad'

    Returns:
        The created habit document as a dict
    """
    db = get_db()
    now = datetime.now(TIMEZONE)
    challenge_end = now + timedelta(days=CHALLENGE_DURATION)

    habit_data = {
        "name": habit_name,
        "type": habit_type,
        "created_at": now,
        "challenge_end": challenge_end,
        "current_streak": 0,
        "best_streak": 0,
        "total_days_completed": 0,
        "total_penalties": 0,
        "resets": 0,
        "daily_log": {},
        "status": STATUS_ACTIVE,
        "last_poll_date": None,
    }

    # Use habit name (lowercase, stripped) as document ID for uniqueness per user
    habit_id = habit_name.lower().strip().replace(" ", "_")
    doc_ref = db.collection("users").document(str(user_id)) \
                .collection("habits").document(habit_id)

    # Check if habit already exists
    if doc_ref.get().exists:
        return None  # Signal that habit already exists

    doc_ref.set(habit_data)
    habit_data["id"] = habit_id
    return habit_data


def get_all_habits(user_id: str, active_only: bool = False) -> list:
    """Get all habits for a user."""
    db = get_db()
    query = db.collection("users").document(str(user_id)).collection("habits")

    if active_only:
        query = query.where("status", "==", STATUS_ACTIVE)

    docs = query.stream()
    habits = []
    for doc in docs:
        habit = doc.to_dict()
        habit["id"] = doc.id
        habits.append(habit)

    return habits


def get_habit(user_id: str, habit_name: str) -> dict | None:
    """Get a specific habit by name."""
    db = get_db()
    habit_id = habit_name.lower().strip().replace(" ", "_")
    doc_ref = db.collection("users").document(str(user_id)) \
                .collection("habits").document(habit_id)

    doc = doc_ref.get()
    if doc.exists:
        habit = doc.to_dict()
        habit["id"] = doc.id
        return habit
    return None


def delete_habit(user_id: str, habit_name: str) -> bool:
    """Delete a habit. Returns True if deleted, False if not found."""
    db = get_db()
    habit_id = habit_name.lower().strip().replace(" ", "_")
    doc_ref = db.collection("users").document(str(user_id)) \
                .collection("habits").document(habit_id)

    if not doc_ref.get().exists:
        return False

    doc_ref.delete()
    return True


# ─── Progress Updates ────────────────────────────────────────────────

def record_response(user_id: str, habit_id: str, response: str) -> dict:
    """
    Record a user's daily response to a habit poll.

    Args:
        user_id: Discord user ID
        habit_id: Habit document ID
        response: 'yes' or 'no'

    Returns:
        Updated habit data with a 'result' key describing what happened
    """
    db = get_db()
    doc_ref = db.collection("users").document(str(user_id)) \
                .collection("habits").document(habit_id)

    doc = doc_ref.get()
    if not doc.exists:
        return None

    habit = doc.to_dict()
    habit["id"] = habit_id
    today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")

    # Determine outcome based on habit type
    if habit["type"] == GOOD_HABIT:
        if response == "yes":
            # Good habit done — streak continues
            habit["current_streak"] += 1
            habit["total_days_completed"] += 1
            if habit["current_streak"] > habit["best_streak"]:
                habit["best_streak"] = habit["current_streak"]
            habit["daily_log"][today] = "yes"
            habit["result"] = "success"
        else:
            # Good habit missed — reset streak
            habit["current_streak"] = 0
            habit["resets"] += 1
            habit["daily_log"][today] = "no"
            habit["result"] = "reset"
    else:  # BAD_HABIT
        if response == "yes":
            # Bad habit relapsed — penalty + reset
            habit["total_penalties"] += 1
            habit["current_streak"] = 0
            habit["resets"] += 1
            habit["daily_log"][today] = "yes"
            habit["result"] = "penalty"
        else:
            # Bad habit resisted — streak continues
            habit["current_streak"] += 1
            habit["total_days_completed"] += 1
            if habit["current_streak"] > habit["best_streak"]:
                habit["best_streak"] = habit["current_streak"]
            habit["daily_log"][today] = "no"
            habit["result"] = "success"

    habit["last_poll_date"] = today

    # Check if challenge is complete (30 days elapsed)
    now = datetime.now(TIMEZONE)
    created_at = habit["created_at"]
    if hasattr(created_at, 'tzinfo') and created_at.tzinfo is None:
        created_at = TIMEZONE.localize(created_at)
    days_elapsed = (now - created_at).days

    if days_elapsed >= CHALLENGE_DURATION:
        habit["status"] = STATUS_COMPLETED
        habit["result"] = "completed_" + habit["result"]

    # Update Firestore
    update_data = {
        "current_streak": habit["current_streak"],
        "best_streak": habit["best_streak"],
        "total_days_completed": habit["total_days_completed"],
        "total_penalties": habit["total_penalties"],
        "resets": habit["resets"],
        f"daily_log.{today}": habit["daily_log"][today],
        "status": habit["status"],
        "last_poll_date": today,
    }
    doc_ref.update(update_data)

    return habit


def record_missed_response(user_id: str, habit_id: str) -> dict:
    """
    Record a missed response (no interaction with poll).
    Good habits: treated as 'no' (missed).
    Bad habits: treated as 'yes' (relapsed).
    """
    db = get_db()
    doc_ref = db.collection("users").document(str(user_id)) \
                .collection("habits").document(habit_id)

    doc = doc_ref.get()
    if not doc.exists:
        return None

    habit = doc.to_dict()

    if habit["type"] == GOOD_HABIT:
        return record_response(user_id, habit_id, "no")
    else:
        return record_response(user_id, habit_id, "yes")


# ─── Queries for Scheduling ─────────────────────────────────────────

def get_all_active_users_with_habits() -> dict:
    """
    Get all users who have active habits.

    Returns:
        Dict of {user_id: [list of active habits]}
    """
    db = get_db()
    users_ref = db.collection("users")
    users = {}

    for user_doc in users_ref.stream():
        user_id = user_doc.id
        habits = get_all_habits(user_id, active_only=True)
        if habits:
            users[user_id] = habits

    return users


def get_habits_needing_poll(user_id: str) -> list:
    """Get habits for a user that haven't been polled today."""
    today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    habits = get_all_habits(user_id, active_only=True)

    return [h for h in habits if h.get("last_poll_date") != today]


def get_expired_habits() -> list:
    """
    Get all habits across all users that have reached 30 days
    and are still marked active (need final report).
    """
    db = get_db()
    now = datetime.now(TIMEZONE)
    expired = []

    for user_doc in db.collection("users").stream():
        user_id = user_doc.id
        habits = get_all_habits(user_id, active_only=True)
        for habit in habits:
            created_at = habit["created_at"]
            if hasattr(created_at, 'tzinfo') and created_at.tzinfo is None:
                created_at = TIMEZONE.localize(created_at)
            days_elapsed = (now - created_at).days
            if days_elapsed >= CHALLENGE_DURATION:
                habit["user_id"] = user_id
                expired.append(habit)

    return expired


def mark_habit_completed(user_id: str, habit_id: str):
    """Mark a habit as completed after the 30-day report is sent."""
    db = get_db()
    doc_ref = db.collection("users").document(str(user_id)) \
                .collection("habits").document(habit_id)
    doc_ref.update({"status": STATUS_COMPLETED})
