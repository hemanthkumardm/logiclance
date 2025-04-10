import csv
import hashlib

def authenticate_user(username, password):
    try:
        with open("employee_details.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["name"].strip().lower() == username.lower():
                    return row["password"] == hashlib.sha256(password.encode()).hexdigest()
    except Exception as e:
        print(f"⚠️ Auth error: {e}")
    return False
