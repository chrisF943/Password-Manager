import re


def check_password_strength(password: str) -> dict:
    """
    Check the strength of a password and return details.

    Returns:
        dict with keys: strength (weak/medium/strong), score (0-4), color
    """
    if not password:
        return {"strength": "none", "score": 0, "color": "gray", "message": ""}

    score = 0
    feedback = []

    # Length checks
    if len(password) >= 8:
        score += 1
    elif len(password) >= 6:
        feedback.append("8+ characters")

    if len(password) >= 12:
        score += 1

    # Character variety checks
    if re.search(r'[a-z]', password):
        score += 1

    if re.search(r'[A-Z]', password):
        score += 1

    if re.search(r'[0-9]', password):
        score += 1

    if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:\'",.<>?]', password):
        score += 1

    # Determine strength level
    if score >= 5:
        return {"strength": "strong", "score": score, "color": "#4CAF50", "message": "Strong password"}
    elif score >= 3:
        return {"strength": "medium", "score": score, "color": "#FFC107", "message": "Medium strength"}
    else:
        return {"strength": "weak", "score": score, "color": "#F44336", "message": "Weak - add more characters"}
