from skill_gap import calculate_skill_gap


current_skills = {
    "Statistics": 65,
    "Python": 40,
    "SQL": 55,
    "Data Analysis": 60,
    "Data Visualization": 45
}


results = calculate_skill_gap(
    "Statistical Officer",
    current_skills
)


for result in results:
    print(
        f"{result['skill']}: "
        f"Current={result['current']}, "
        f"Required={result['required']}, "
        f"Gap={result['gap']}, "
        f"Priority={result['priority']}"
    )