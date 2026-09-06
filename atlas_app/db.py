"""
ATLAS — Member 4: Database & iGOT Layer
SIH26101 One-Day Prototype

SQLite database + mock iGOT course catalogue.
This is the SINGLE SOURCE OF TRUTH for learner, competency, course and
assessment data. atlas_app/data.py wraps these functions so the rest of
the app (pages/, streamlit_app.py) never talks to SQLite directly.

Vocabulary note:
    Profile codes ("P001", "P002", "P003"), roles and competency names
    below are kept IDENTICAL to the original mock data used across the
    team (Data Analyst / Financial Analyst / Statistical Officer) so
    that swapping mock -> DB does not break Member 2/3/5's logic.

Usage:
    from db import init_db, seed_demo_data
    init_db()
    seed_demo_data()
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).with_name("atlas.db")


# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    # check_same_thread=False: Streamlit can touch this from more than
    # one internal thread during a rerun, so a strict single-thread
    # check would occasionally raise a spurious ProgrammingError.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ============================================================
# SCHEMA
# ============================================================

def init_db():
    """Create all core SQLite tables if they do not already exist."""
    conn = get_connection()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS learners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_code TEXT NOT NULL UNIQUE,   -- e.g. "P001" (matches old MOCK_PROFILES keys)
        name TEXT NOT NULL,
        designation TEXT,
        department TEXT,
        role TEXT NOT NULL,
        qualifications TEXT,
        experience TEXT,
        training_history TEXT,               -- JSON-encoded list of strings
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
    -- NOTE: gap/priority are intentionally NOT stored here. They are
    -- derived values (Member 2's formula), so we compute them on read
    -- in data.py. Storing them too would let the two go out of sync.

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
    """)
    conn.commit()
    conn.close()


# ============================================================
# SEED DATA
# (Same 3 profiles + same competency names as the original
#  MOCK_PROFILES / MOCK_COMPETENCIES in data.py, so nothing else
#  in the app has to change its vocabulary.)
# ============================================================

def seed_demo_data():
    conn = get_connection()
    cur = conn.cursor()

    learners = [
        ("P001", "Ananya Sharma", "Assistant Section Officer", "Rural Development",
         "Data Analyst", "B.Tech (CSE)", "3 years",
         json.dumps(["Basics of Data Analytics (2024)", "MS Excel Advanced (2023)"]), "🧑‍💼"),
        ("P002", "Rohit Verma", "Section Officer", "Finance",
         "Financial Analyst", "MBA (Finance)", "6 years",
         json.dumps(["Public Financial Management (2022)"]), "👨‍💼"),
        ("P003", "Rahul Sharma", "Statistical Officer", "Statistics & Programme Implementation",
         "Statistical Officer", "M.Sc (Statistics)", "4 years",
         json.dumps(["Applied Statistics for Policy (2023)", "Python for Data Analysis (2024)"]), "📊"),
    ]
    cur.executemany("""
        INSERT OR IGNORE INTO learners
        (profile_code, name, designation, department, role, qualifications,
         experience, training_history, avatar)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, learners)

    # Every competency name that appears anywhere in the app.
    competencies = [
        "Data Visualization", "SQL / Data Querying", "Statistical Analysis", "Report Writing",
        "Budgeting & Forecasting", "Financial Reporting", "Risk Assessment", "Regulatory Compliance",
        "Statistics", "Python", "SQL", "Data Analysis",
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO competencies (name) VALUES (?)",
        [(c,) for c in competencies],
    )

    # One mock iGOT course per competency, so every role always has
    # something to recommend (this was the bug in the earlier version:
    # Statistical Officer's Python/SQL/Statistics/Data Analysis gaps had
    # no matching course at all).
    courses = [
        ("IGOT-DV-101", "Data Visualization with Power BI",
         "Build clear, decision-ready dashboards and charts.",
         "Data Visualization", "Intermediate", 6),
        ("IGOT-SQL-101", "SQL for Data Analysts",
         "Queries, joins, aggregation for day-to-day reporting.",
         "SQL / Data Querying", "Intermediate", 6),
        ("IGOT-STA-201", "Advanced Statistical Analysis",
         "Hypothesis testing and applied statistical methods.",
         "Statistical Analysis", "Advanced", 10),
        ("IGOT-RW-101", "Professional Report Writing",
         "Structuring and writing clear official reports.",
         "Report Writing", "Intermediate", 5),
        ("IGOT-BF-201", "Budgeting & Forecasting Essentials",
         "Building and validating departmental budgets.",
         "Budgeting & Forecasting", "Advanced", 7),
        ("IGOT-FR-101", "Financial Reporting Fundamentals",
         "Preparing accurate, compliant financial reports.",
         "Financial Reporting", "Intermediate", 6),
        ("IGOT-RA-101", "Risk Assessment Frameworks",
         "Identifying and scoring operational/financial risk.",
         "Risk Assessment", "Intermediate", 8),
        ("IGOT-RC-101", "Regulatory Compliance Basics",
         "Core compliance obligations for government finance roles.",
         "Regulatory Compliance", "Beginner", 4),
        ("IGOT-STAT-101", "Applied Statistics for Officers",
         "Statistical foundations for policy and programme work.",
         "Statistics", "Advanced", 10),
        ("IGOT-PY-101", "Python for Data Analysis",
         "Core Python + pandas for everyday data work.",
         "Python", "Intermediate", 8),
        ("IGOT-SQL-102", "SQL for Data Management",
         "Managing and querying departmental data stores.",
         "SQL", "Intermediate", 6),
        ("IGOT-DA-201", "Data Analysis Fundamentals",
         "End-to-end analysis: clean, explore, interpret.",
         "Data Analysis", "Intermediate", 7),
    ]
    cur.executemany("""
        INSERT OR IGNORE INTO courses
        (course_code, title, description, skill, level, duration_hours)
        VALUES (?, ?, ?, ?, ?, ?)
    """, courses)

    conn.commit()

    # Per-learner current/required competency levels
    # (0-5 scale for Data Analyst / Financial Analyst, 0-100 scale for
    #  Statistical Officer — matches the original mock data exactly).
    learner_rows = {r["profile_code"]: r["id"] for r in cur.execute("SELECT id, profile_code FROM learners")}
    comp_rows = {r["name"]: r["id"] for r in cur.execute("SELECT id, name FROM competencies")}

    demo_levels = {
        "P001": {  # Ananya Sharma — Data Analyst (0-5 scale)
            "Data Visualization": (2, 4),
            "SQL / Data Querying": (3, 4),
            "Statistical Analysis": (2, 5),
            "Report Writing": (4, 4),
        },
        "P002": {  # Rohit Verma — Financial Analyst (0-5 scale)
            "Budgeting & Forecasting": (3, 5),
            "Financial Reporting": (4, 4),
            "Risk Assessment": (2, 4),
            "Regulatory Compliance": (3, 3),
        },
        "P003": {  # Rahul Sharma — Statistical Officer (0-100 scale)
            "Statistics": (65, 80),
            "Python": (40, 75),
            "SQL": (55, 70),
            "Data Analysis": (60, 80),
            "Data Visualization": (45, 70),
        },
    }

    for profile_code, levels in demo_levels.items():
        learner_id = learner_rows[profile_code]
        for comp_name, (current, required) in levels.items():
            cur.execute("""
                INSERT OR REPLACE INTO learner_competencies
                (learner_id, competency_id, current_level, required_level)
                VALUES (?, ?, ?, ?)
            """, (learner_id, comp_rows[comp_name], current, required))

    conn.commit()
    conn.close()


def reset_db():
    """Wipe and recreate everything. Handy while iterating during the day."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
    seed_demo_data()


# ============================================================
# READ HELPERS — return shapes match what atlas_app/data.py expects
# ============================================================

def get_all_profile_codes() -> List[str]:
    conn = get_connection()
    rows = conn.execute("SELECT profile_code FROM learners ORDER BY id").fetchall()
    conn.close()
    return [r["profile_code"] for r in rows]


def get_learner_row(profile_code: str) -> Optional[sqlite3.Row]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM learners WHERE profile_code = ?", (profile_code,)
    ).fetchone()
    conn.close()
    return row


def get_profile(profile_code: str) -> Optional[Dict[str, Any]]:
    """Same shape as the old MOCK_PROFILES[profile_id] dict."""
    row = get_learner_row(profile_code)
    if row is None:
        return None
    return {
        "id": row["profile_code"],
        "name": row["name"],
        "designation": row["designation"],
        "department": row["department"],
        "role": row["role"],
        "qualifications": row["qualifications"],
        "experience": row["experience"],
        "training_history": json.loads(row["training_history"] or "[]"),
        "avatar": row["avatar"],
    }


def get_competency_profile(profile_code: str) -> List[Dict[str, Any]]:
    """
    Same shape as the old MOCK_COMPETENCIES[role] list:
    [{"competency": ..., "current": ..., "required": ...}, ...]

    Keyed by the individual learner (profile_code), not just role,
    since real learners of the same role can be at different levels.
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM learners WHERE profile_code = ?", (profile_code,)
    ).fetchone()
    if row is None:
        conn.close()
        return []

    rows = conn.execute("""
        SELECT c.name AS competency, lc.current_level AS current, lc.required_level AS required
        FROM learner_competencies lc
        JOIN competencies c ON c.id = lc.competency_id
        WHERE lc.learner_id = ?
        ORDER BY c.name
    """, (row["id"],)).fetchall()
    conn.close()

    return [
        {"competency": r["competency"], "current": r["current"], "required": r["required"]}
        for r in rows
    ]


def get_courses(skill: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    if skill:
        rows = conn.execute(
            "SELECT * FROM courses WHERE skill = ? ORDER BY level, title", (skill,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM courses ORDER BY skill, level, title").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# WRITE HELPERS — assessments / progress
# ============================================================

def save_assessment(
    profile_code: str,
    score: float,
    total_questions: int,
    quiz_title: str = "ATLAS Quiz",
    answers: Optional[List[Dict[str, Any]]] = None,
) -> Optional[int]:
    conn = get_connection()
    cur = conn.cursor()

    learner = cur.execute(
        "SELECT id FROM learners WHERE profile_code = ?", (profile_code,)
    ).fetchone()
    if learner is None:
        conn.close()
        return None

    cur.execute("""
        INSERT INTO assessments (learner_id, quiz_title, score, total_questions)
        VALUES (?, ?, ?, ?)
    """, (learner["id"], quiz_title, score, total_questions))
    assessment_id = cur.lastrowid

    for a in (answers or []):
        cur.execute("""
            INSERT INTO assessment_answers
            (assessment_id, question, selected_answer, correct_answer, is_correct)
            VALUES (?, ?, ?, ?, ?)
        """, (
            assessment_id,
            a.get("question", ""),
            a.get("selected_answer", ""),
            a.get("correct_answer", ""),
            int(a.get("is_correct", False)),
        ))

    conn.commit()
    conn.close()
    return assessment_id


def get_assessments(profile_code: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    learner = conn.execute(
        "SELECT id FROM learners WHERE profile_code = ?", (profile_code,)
    ).fetchone()
    if learner is None:
        conn.close()
        return []

    rows = conn.execute("""
        SELECT * FROM assessments
        WHERE learner_id = ?
        ORDER BY attempted_at ASC, id ASC
    """, (learner["id"],)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    reset_db()
    print(f"ATLAS database ready: {DB_PATH}")
    print(f"Learners: {get_all_profile_codes()}")
    print(f"Courses: {len(get_courses())}")