import json
from pathlib import Path


def load_competencies():
    file_path = Path(__file__).parent.parent / "data" / "competencies.json"

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_skill_gap(role, current_skills):
    competencies = load_competencies()

    if role not in competencies:
        return []

    required_skills = competencies[role]
    results = []

    for skill, required_level in required_skills.items():
        current_level = current_skills.get(skill, 0)

        gap = max(required_level - current_level, 0)

        if gap >= 31:
            priority = "High"
        elif gap >= 16:
            priority = "Medium"
        else:
            priority = "Low"

        results.append({
            "skill": skill,
            "current": current_level,
            "required": required_level,
            "gap": gap,
            "priority": priority
        })

    return results

def load_employee_skills(employee_name):
    file_path = Path(__file__).parent.parent / "data" / "current_skills.json"

    with open(file_path, "r", encoding="utf-8") as file:
        employees = json.load(file)

    if employee_name not in employees:
        return None

    return employees[employee_name]