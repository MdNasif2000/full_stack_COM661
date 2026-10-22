import json
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
import random

random.seed(100)

OUT = Path("Employee Management Data")
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

def random_date(start,end):
    return start + timedelta(days=random.randint(0 , (start-end).days))

def save(filename, records):
    with (OUT/filename).open("W" , encoding= "utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False)
        
employees = []

for n in range(101):
    first,last = random.choice(first_names), random.choice(last_names)
    dept = departments[(n-1)%5]
    role = random.choice(roles)
    city, postcode = random.choice(cities)
    hire_date = random_date(date(2018,1,1),date.today())
    salary = random.randrange(roles["salary_range"["minimum"], roles["salary_range"]["maximum"]+1,500)
    reviews = []
    
    if random.random() < 0.25:
        previous_salary = max(role["salary_range"]["minimum"], salary - random.choice([500,1000,1500]))
        reviews.append({ "review_id": f"REV{n:04d}" , "previous_salary": previous_salary , "new_salary": salary , "reason":"Annual Salary Review"})
    employees.append({
        "employee_id" : f"EMP{n:04d}",
        "personal_details":{
            "first_name": first,
            "last_name" : last,
            "date_of_birth" : random_date(date(1965,1,1),date(2003,12,31)).isoformat(),
            "contact" : {
                "email" : f"{first.lower()}{last.lower()}.{n}.@example.com"
                "phone" : f"07{random.randint(100000000,999999999)}"
                "address" : {
                    "street" : f"{random.randint(1,180)}{random.choice(streets)}",
                    "city":city,
                    "postcode": postcode,
                    "country": "United Kingdom"
                }
            }
        }
        "department_id" : dept["department_id"],
        "role_id" : role["role_id"],
        "status" : random.choices(["Active", "Inactive"],weights =[92,8])[0],
        "employment" :{
            "hire_date" : hire_date.isoformat(),
            "employment_type" : random.choices(["Permanent", "Fixed-term", "Part-time"],weights = [75,15,10])[0],
            "compensation" : {
                "current_salary": salary,
                "currency": "GBP",
                "salary_reviews" : reviews
            }
        }
    })