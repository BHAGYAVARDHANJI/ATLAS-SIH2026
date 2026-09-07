# ATLAS — Adaptive Training & Learning Assistance System

SIH26101 prototype for AI-enabled competency-gap assessment, personalized learning recommendations, quiz generation and progress tracking.

## Run

1. Install Python 3.11+ (Python 3.13/3.14 are supported by the pinned prototype dependencies where available).
2. Double-click `setup.bat` once.
3. Double-click `run.bat` to start ATLAS.

Or from PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run atlas_app\Home.py
```

## Demo accounts

- `ananya` / `atlas123` → Ananya Sharma
- `rohit` / `atlas123` → Rohit Verma
- `rahul` / `atlas123` → Rahul Sharma

The account is permanently linked to its learner profile for the session, so one login cannot display another learner's data.

## AI quiz

The quiz works with a built-in fallback dataset. For optional Gemini generation, set `GEMINI_API_KEY` as an environment variable or add it to the local ignored `atlas_app/.streamlit/secrets.toml`.

## Production packaging

The local SQLite database is intentionally not committed or packaged. `Home.py` creates and seeds it on first run.
