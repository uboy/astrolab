from datetime import datetime

def validate_birthdate(date_text: str):
    try:
        birthdate = datetime.strptime(date_text, "%d.%m.%Y")
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        if 5 <= age <= 120:
            return True, age
        return False, age
    except ValueError:
        return False, 0
