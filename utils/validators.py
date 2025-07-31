# utils/validators.py
from datetime import datetime

class ValidationError(Exception):
    """Custom validation error."""
    pass

def validate_amount(amount: float):
    if amount <= 0:
        raise ValidationError("Amount must be a positive number")
    if amount > 1_000_000:
        raise ValidationError("Amount must be less than or equal to 1,000,000.")

def validate_user_id(user_id: str):
    if not (1 <= len(user_id) <= 30):
        raise ValidationError("User ID must be between 1 and 30 characters long.")

def validate_category(category: str):
    if not (1 <= len(category) <= 20):
        raise ValidationError("Category must be between 1 and 20 characters long.")

def validate_date(date_str: str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        if dt > datetime.now():
            raise ValidationError("Date cannot be in the future.")
    except ValueError:
        raise ValidationError("Invalid date format. Expected YYYY-MM-DD.")

def validate_date_range(start: str, end: str):
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
        if start_dt > end_dt:
            raise ValidationError("Start date cannot be after end date")
    except ValueError:
        raise ValidationError("Invalid date format. Expected YYYY-MM-DD.")
