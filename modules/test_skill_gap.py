from skill_gap import calculate_skill_gap, load_employee_skills


employee_name = "Rahul Sharma"

employee = load_employee_skills(employee_name)

if employee is None:
    print("Employee not found.")
else:
    role = employee["role"]
    current_skills = employee["skills"]

    print(f"\nEmployee: {employee_name}")
    print(f"Role: {role}")
    print("\nSkill Gap Analysis:")

    results = calculate_skill_gap(role, current_skills)

    for result in results:
        print(
            f"{result['skill']}: "
            f"Current={result['current']}, "
            f"Required={result['required']}, "
            f"Gap={result['gap']}, "
            f"Priority={result['priority']}"
        )