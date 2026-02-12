import re
from fastapi import HTTPException

def validate_password_strength(password: str):
    if len(password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        raise HTTPException(400, "Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        raise HTTPException(400, "Password must contain at least one lowercase letter")

    if not re.search(r"[0-9]", password):
        raise HTTPException(400, "Password must contain at least one number")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(400, "Password must contain at least one special character")
