import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

random.seed(42)
OUT = Path("employee_management_data")
OUT.mkdir(exist_ok=True)

first_names = ["Maya", "Oliver", "Amelia", "George", "Isla", "Harry", "Ava", "Noah",
               "Emily", "Leo", "Grace", "Jack", "Lily", "Charlie", "Sophia", "Oscar",
               "Ella", "Thomas", "Freya", "James", "Evie", "William", "Poppy", "Arthur",
               "Mia", "Henry", "Florence", "Theodore", "Sophie", "Lucas", "Ruby", "Archie"]
last_names = ["Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson",
              "Davies", "Patel", "Robinson", "Wright", "Thompson", "Evans", "Walker",
              "White", "Roberts", "Green", "Hall", "Wood", "Jackson", "Clarke", "Lewis"]
cities = [("Birmingham", "B9 2P"), ("London", "E1 6AN"), ("Manchester", "M1 1AE"),
          ("Leeds", "LS1 4AP"), ("Bristol", "BS1 5TR"), ("Glasgow", "G1 1XQ")]
streets = ["High Street", "Church Road", "Station Road", "Victoria Road", "Park Lane",
           "King Street", "Queen Street", "Mill Road", "Bridge Street"]

departments = [
    {"department_id": "DEPT001", "name": "Information Technology",
     "description": "Manages company systems and software", "manager_id": "EMP0001"},
    {"department_id": "DEPT002", "name": "Human Resources",
     "description": "Manages recruitment and employee records", "manager_id": "EMP0002"},
    {"department_id": "DEPT003", "name": "Finance",
     "description": "Manages budgets and financial reporting", "manager_id": "EMP0003"},
    {"department_id": "DEPT004", "name": "Marketing",
     "description": "Manages campaigns and communications", "manager_id": "EMP0004"},
    {"department_id": "DEPT005", "name": "Operations",
     "description": "Coordinates daily business operations", "manager_id": "EMP0005"}
]

roles = [
    {"role_id": "ROLE001", "name": "Software Developer",
     "description": "Develops and maintains software applications",
     "salary_range": {"minimum": 28000, "maximum": 45000, "currency": "GBP"}},
    {"role_id": "ROLE002", "name": "IT Support Analyst",
     "description": "Supports users and business systems",
     "salary_range": {"minimum": 24000, "maximum": 35000, "currency": "GBP"}},
    {"role_id": "ROLE003", "name": "HR Officer",
     "description": "Supports recruitment and HR administration",
     "salary_range": {"minimum": 25000, "maximum": 38000, "currency": "GBP"}},
    {"role_id": "ROLE004", "name": "Accountant",
     "description": "Maintains financial records and reports",
     "salary_range": {"minimum": 28000, "maximum": 42000, "currency": "GBP"}},
    {"role_id": "ROLE005", "name": "Marketing Executive",
     "description": "Plans and delivers marketing activities",
     "salary_range": {"minimum": 25000, "maximum": 38000, "currency": "GBP"}},
    {"role_id": "ROLE006", "name": "Operations Coordinator",
     "description": "Coordinates operational tasks and schedules",
     "salary_range": {"minimum": 26000, "maximum": 39000, "currency": "GBP"}},
    {"role_id": "ROLE007", "name": "Project Manager",
     "description": "Plans projects and coordinates delivery",
     "salary_range": {"minimum": 35000, "maximum": 55000, "currency": "GBP"}},
    {"role_id": "ROLE008", "name": "Department Manager",
     "description": "Leads a team and oversees department performance",
     "salary_range": {"minimum": 40000, "maximum": 60000, "currency": "GBP"}}
]

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def save(filename, records):
    with (OUT / filename).open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

employees = []
for n in range(1, 101):
    first, last = random.choice(first_names), random.choice(last_names)
    dept = departments[(n - 1) % 5]
    role = random.choice(roles)
    city, postcode = random.choice(cities)
    hire_date = random_date(date(2018, 1, 1), date(2026, 9, 30))
    salary = random.randrange(role["salary_range"]["minimum"],
                              role["salary_range"]["maximum"] + 1, 500)
    reviews = []
    if random.random() < 0.25:
        previous = max(role["salary_range"]["minimum"], salary - random.choice([1000, 1500, 2000]))
        reviews.append({"review_id": f"REV{n:04d}", "previous_salary": previous,
                        "new_salary": salary, "reason": "Annual salary review"})
    employees.append({
        "employee_id": f"EMP{n:04d}",
        "personal_details": {
            "first_name": first, "last_name": last,
            "date_of_birth": random_date(date(1965, 1, 1), date(2003, 12, 31)).isoformat(),
            "contact": {
                "email": f"{first.lower()}.{last.lower()}.{n}@example.com",
                "phone": f"07{random.randint(100000000, 999999999)}",
                "address": {
                    "street": f"{random.randint(1, 180)} {random.choice(streets)}",
                    "city": city, "postcode": postcode, "country": "United Kingdom"
                }
            }
        },
        "department_id": dept["department_id"],
        "role_id": role["role_id"],
        "status": random.choices(["Active", "Inactive"], weights=[92, 8])[0],
        "employment": {
            "hire_date": hire_date.isoformat(),
            "employment_type": random.choices(
                ["Permanent", "Fixed-term", "Part-time"], weights=[75, 15, 10])[0],
            "compensation": {
                "current_salary": salary, "currency": "GBP", "salary_reviews": reviews
            }
        }
    })

users = []
for n, employee in enumerate(employees, start=1):
    first = employee["personal_details"]["first_name"]
    last = employee["personal_details"]["last_name"]
    if n == 1:
        user_role = "admin"
    elif n in (2, 3):
        user_role = "hr_staff"
    elif n in (4, 5):
        user_role = "manager"
    else:
        user_role = "employee"
    created = datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=random.randint(0, 900))
    updated = min(created + timedelta(days=random.randint(0, 300)),
                  datetime(2026, 10, 19, tzinfo=timezone.utc))
    users.append({
        "user_id": f"USR{n:04d}",
        "username": f"{first.lower()}.{last.lower()}.{n}",
        "email": f"user{n}@example.com",
        # Placeholder only. Replace with real hashes when testing authentication.
        "password_hash": "PLACEHOLDER_NOT_A_REAL_PASSWORD_HASH",
        "role": user_role, "employee_id": employee["employee_id"],
        "account_status": random.choices(["active", "inactive"], weights=[95, 5])[0],
        "created_at": created.isoformat(), "updated_at": updated.isoformat()
    })

# 150 records, no duplicate employee/date combinations; weekdays from the previous 90 days.
workdays = [date(2026, 10, 18) - timedelta(days=d) for d in range(1, 91)
            if (date(2026, 10, 18) - timedelta(days=d)).weekday() < 5]
attendance, used = [], set()
while len(attendance) < 150:
    employee_no, day = random.randint(1, 100), random.choice(workdays)
    if (employee_no, day) in used:
        continue
    used.add((employee_no, day))
    status = random.choices(["Present", "Late", "Absent"], weights=[82, 10, 8])[0]
    check_in = check_out = None
    if status != "Absent":
        check_in = f"{random.choice([8, 9] if status == 'Late' else [8, 8, 8, 9]):02d}:{random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]):02d}"
        check_out = f"{random.choice([16, 17, 18]):02d}:{random.choice([0, 10, 20, 30, 40, 50]):02d}"
    attendance.append({
        "attendance_id": f"ATT{len(attendance) + 1:04d}",
        "employee_id": f"EMP{employee_no:04d}", "date": day.isoformat(),
        "status": status, "check_in": check_in, "check_out": check_out
    })

leave_requests = []
for n in range(1, 26):
    requested = random_date(date(2026, 7, 1), date(2026, 10, 18))
    start = requested + timedelta(days=random.randint(1, 60))
    end = start + timedelta(days=random.randint(0, 4))
    leave_requests.append({
        "leave_id": f"LEV{n:04d}",
        "employee_id": f"EMP{random.randint(1, 100):04d}",
        "leave_type": random.choice(["Annual Leave", "Sick Leave", "Personal Leave", "Unpaid Leave"]),
        "period": {"start_date": start.isoformat(), "end_date": end.isoformat()},
        "reason": random.choice(["Family holiday", "Medical appointment", "Personal reasons",
                                 "Family commitment", "Rest and recovery"]),
        "status": random.choices(["Pending", "Approved", "Rejected"], weights=[35, 55, 10])[0],
        "requested_at": datetime(requested.year, requested.month, requested.day,
                                 random.randint(8, 17), random.choice([0, 15, 30, 45])).isoformat()
    })

for filename, records in [
    ("users.json", users), ("employees.json", employees),
    ("departments.json", departments), ("job_roles.json", roles),
    ("attendance.json", attendance), ("leave_requests.json", leave_requests)
]:
    save(filename, records)
    print(f"Created {OUT / filename}: {len(records)} records")

print(f"\nDone. JSON files are in: {OUT.resolve()}")
print("Important: password_hash values are placeholders, not valid authentication hashes.")
