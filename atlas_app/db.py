"""ATLAS SQLite data layer."""

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).with_name("atlas.db")
PBKDF2_ITERATIONS = 200_000


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _add_column_if_missing(conn, table: str, column: str, definition: str):
    columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    conn = get_connection()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS learners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_code TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        designation TEXT,
        department TEXT,
        role TEXT NOT NULL,
        qualifications TEXT,
        experience TEXT,
        training_history TEXT,
        avatar TEXT DEFAULT '🎓'
    );

    CREATE TABLE IF NOT EXISTS competencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS learner_competencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learner_id INTEGER NOT NULL,
        competency_id INTEGER NOT NULL,
        current_level REAL NOT NULL DEFAULT 0,
        required_level REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE,
        FOREIGN KEY (competency_id) REFERENCES competencies(id) ON DELETE CASCADE,
        UNIQUE(learner_id, competency_id)
    );

    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT UNIQUE,
        title TEXT NOT NULL,
        description TEXT,
        skill TEXT NOT NULL,
        level TEXT,
        duration_hours REAL,
        source TEXT DEFAULT 'iGOT (mock)'
    );

    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learner_id INTEGER NOT NULL,
        quiz_title TEXT,
        score REAL NOT NULL,
        total_questions INTEGER,
        attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS assessment_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER NOT NULL,
        question TEXT,
        selected_answer TEXT,
        correct_answer TEXT,
        is_correct INTEGER DEFAULT 0,
        FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_salt TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Migration for databases created by the older ATLAS version.
    _add_column_if_missing(conn, "users", "profile_code", "TEXT")
    conn.commit()

    # Automatically repair old accounts such as "ananya" that were created
    # before users were linked to learner profiles.
    rows = conn.execute("SELECT id, username FROM users WHERE profile_code IS NULL OR profile_code = ''").fetchall()
    for row in rows:
        key = row["username"].strip().lower().replace(" ", "")
        match = conn.execute(
            "SELECT profile_code FROM learners WHERE lower(replace(name, ' ', '')) = ? OR lower(profile_code) = ?",
            (key, key),
        ).fetchone()
        if match:
            conn.execute("UPDATE users SET profile_code = ? WHERE id = ?", (match["profile_code"], row["id"]))

    conn.commit()
    conn.close()


def seed_demo_data():
    conn = get_connection()
    cur = conn.cursor()

    learners = [
        ("P001", "Ananya Sharma", "Assistant Section Officer", "Rural Development", "Data Analyst", "B.Tech (CSE)", "3 years", json.dumps(["Basics of Data Analytics (2024)", "MS Excel Advanced (2023)"]), "🧑‍💼"),
        ("P002", "Rohit Verma", "Section Officer", "Finance", "Financial Analyst", "MBA (Finance)", "6 years", json.dumps(["Public Financial Management (2022)" ]), "👨‍💼"),
        ("P003", "Rahul Sharma", "Statistical Officer", "Statistics & Programme Implementation", "Statistical Officer", "M.Sc (Statistics)", "4 years", json.dumps(["Applied Statistics for Policy (2023)", "Python for Data Analysis (2024)" ]), "📊"),
    ]
    cur.executemany("""
        INSERT OR IGNORE INTO learners
        (profile_code, name, designation, department, role, qualifications, experience, training_history, avatar)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, learners)

    competencies = [
        "Data Visualization", "SQL / Data Querying", "Statistical Analysis", "Report Writing",
        "Budgeting & Forecasting", "Financial Reporting", "Risk Assessment", "Regulatory Compliance",
        "Statistics", "Python", "SQL", "Data Analysis",
    ]
    cur.executemany("INSERT OR IGNORE INTO competencies (name) VALUES (?)", [(c,) for c in competencies])

    courses = [
        ("IGOT-DV-101", "Data Visualization with Power BI", "Build clear, decision-ready dashboards and charts.", "Data Visualization", "Intermediate", 6),
        ("IGOT-SQL-101", "SQL for Data Analysts", "Queries, joins, aggregation for day-to-day reporting.", "SQL / Data Querying", "Intermediate", 6),
        ("IGOT-STA-201", "Advanced Statistical Analysis", "Hypothesis testing and applied statistical methods.", "Statistical Analysis", "Advanced", 10),
        ("IGOT-RW-101", "Professional Report Writing", "Structuring and writing clear official reports.", "Report Writing", "Intermediate", 5),
        ("IGOT-BF-201", "Budgeting & Forecasting Essentials", "Building and validating departmental budgets.", "Budgeting & Forecasting", "Advanced", 7),
        ("IGOT-FR-101", "Financial Reporting Fundamentals", "Preparing accurate, compliant financial reports.", "Financial Reporting", "Intermediate", 6),
        ("IGOT-RA-101", "Risk Assessment Frameworks", "Identifying and scoring operational/financial risk.", "Risk Assessment", "Intermediate", 8),
        ("IGOT-RC-101", "Regulatory Compliance Basics", "Core compliance obligations for government finance roles.", "Regulatory Compliance", "Beginner", 4),
        ("IGOT-STAT-101", "Applied Statistics for Officers", "Statistical foundations for policy and programme work.", "Statistics", "Advanced", 10),
        ("IGOT-PY-101", "Python for Data Analysis", "Core Python + pandas for everyday data work.", "Python", "Intermediate", 8),
        ("IGOT-SQL-102", "SQL for Data Management", "Managing and querying departmental data stores.", "SQL", "Intermediate", 6),
        ("IGOT-DA-201", "Data Analysis Fundamentals", "End-to-end analysis: clean, explore, interpret.", "Data Analysis", "Intermediate", 7),
    ]
    cur.executemany("""
        INSERT OR IGNORE INTO courses
        (course_code, title, description, skill, level, duration_hours)
        VALUES (?, ?, ?, ?, ?, ?)
    """, courses)

    learner_rows = {r["profile_code"]: r["id"] for r in cur.execute("SELECT id, profile_code FROM learners")}
    comp_rows = {r["name"]: r["id"] for r in cur.execute("SELECT id, name FROM competencies")}
    demo_levels = {
        "P001": {"Data Visualization": (2, 4), "SQL / Data Querying": (3, 4), "Statistical Analysis": (2, 5), "Report Writing": (4, 4)},
        "P002": {"Budgeting & Forecasting": (3, 5), "Financial Reporting": (4, 4), "Risk Assessment": (2, 4), "Regulatory Compliance": (3, 3)},
        "P003": {"Statistics": (65, 80), "Python": (40, 75), "SQL": (55, 70), "Data Analysis": (60, 80), "Data Visualization": (45, 70)},
    }
    for profile_code, levels in demo_levels.items():
        for comp_name, (current, required) in levels.items():
            cur.execute("""
                INSERT OR REPLACE INTO learner_competencies
                (learner_id, competency_id, current_level, required_level)
                VALUES (?, ?, ?, ?)
            """, (learner_rows[profile_code], comp_rows[comp_name], current, required))

    conn.commit()
    conn.close()


def _demo_password_hash(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS).hex()


def seed_demo_users():
    """Create predictable demo accounts only when they do not already exist."""
    conn = get_connection()
    accounts = [("ananya", "P001"), ("rohit", "P002"), ("rahul", "P003")]
    for username, profile_code in accounts:
        exists = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
        if exists:
            continue
        salt = hashlib.sha256((username + "-atlas-demo").encode()).digest()[:16]
        password_hash = _demo_password_hash("atlas123", salt)
        conn.execute(
            "INSERT INTO users (username, password_salt, password_hash, profile_code) VALUES (?, ?, ?, ?)",
            (username, salt.hex(), password_hash, profile_code),
        )
    conn.commit()
    conn.close()


def reset_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
    seed_demo_data()
    seed_demo_users()


def get_all_profile_codes() -> List[str]:
    conn = get_connection()
    rows = conn.execute("SELECT profile_code FROM learners ORDER BY id").fetchall()
    conn.close()
    return [r["profile_code"] for r in rows]


def get_learner_row(profile_code: str) -> Optional[sqlite3.Row]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM learners WHERE profile_code = ?", (profile_code,)).fetchone()
    conn.close()
    return row


def get_profile(profile_code: str) -> Optional[Dict[str, Any]]:
    row = get_learner_row(profile_code)
    if row is None:
        return None
    return {
        "id": row["profile_code"], "name": row["name"], "designation": row["designation"],
        "department": row["department"], "role": row["role"], "qualifications": row["qualifications"],
        "experience": row["experience"], "training_history": json.loads(row["training_history"] or "[]"),
        "avatar": row["avatar"],
    }


def get_competency_profile(profile_code: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    learner = conn.execute("SELECT id FROM learners WHERE profile_code = ?", (profile_code,)).fetchone()
    if learner is None:
        conn.close()
        return []
    rows = conn.execute("""
        SELECT c.name AS competency, lc.current_level AS current, lc.required_level AS required
        FROM learner_competencies lc
        JOIN competencies c ON c.id = lc.competency_id
        WHERE lc.learner_id = ? ORDER BY c.id
    """, (learner["id"],)).fetchall()
    conn.close()
    return [{"competency": r["competency"], "current": r["current"], "required": r["required"]} for r in rows]


def get_courses(skill: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    if skill:
        rows = conn.execute("SELECT * FROM courses WHERE skill = ? ORDER BY level, title", (skill,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM courses ORDER BY skill, level, title").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_assessment(profile_code: str, score: float, total_questions: int, quiz_title: str = "ATLAS Quiz", answers: Optional[List[Dict[str, Any]]] = None) -> Optional[int]:
    conn = get_connection()
    learner = conn.execute("SELECT id FROM learners WHERE profile_code = ?", (profile_code,)).fetchone()
    if learner is None:
        conn.close()
        return None
    cur = conn.cursor()
    cur.execute("INSERT INTO assessments (learner_id, quiz_title, score, total_questions) VALUES (?, ?, ?, ?)", (learner["id"], quiz_title, score, total_questions))
    assessment_id = cur.lastrowid
    for a in (answers or []):
        cur.execute("""
            INSERT INTO assessment_answers (assessment_id, question, selected_answer, correct_answer, is_correct)
            VALUES (?, ?, ?, ?, ?)
        """, (assessment_id, a.get("question", ""), a.get("selected_answer", ""), a.get("correct_answer", ""), int(a.get("is_correct", False))))
    conn.commit()
    conn.close()
    return assessment_id


def get_assessments(profile_code: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    learner = conn.execute("SELECT id FROM learners WHERE profile_code = ?", (profile_code,)).fetchone()
    if learner is None:
        conn.close()
        return []
    rows = conn.execute("SELECT * FROM assessments WHERE learner_id = ? ORDER BY attempted_at ASC, id ASC", (learner["id"],)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(username: str, password_salt: str, password_hash: str, profile_code: Optional[str] = None) -> None:
    conn = get_connection()
    conn.execute("INSERT INTO users (username, password_salt, password_hash, profile_code) VALUES (?, ?, ?, ?)", (username, password_salt, password_hash, profile_code))
    conn.commit()
    conn.close()


def get_user(username: str) -> Optional[sqlite3.Row]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE lower(username) = lower(?)", (username.strip(),)).fetchone()
    conn.close()
    return row


def get_user_by_profile(profile_code: str) -> Optional[sqlite3.Row]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE profile_code = ?", (profile_code,)).fetchone()
    conn.close()
    return row
