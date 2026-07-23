import re
import math
from zxcvbn import zxcvbn

def get_character_set_size(password: str) -> int:
    size = 0
    if any(c.islower() for c in password): size += 26
    if any(c.isupper() for c in password): size += 26
    if any(c.isdigit() for c in password): size += 10
    if any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?\\" for c in password): size += 32
    return max(size, 1)

def calculate_entropy(password: str) -> float:
    if not password:
        return 0.0
    char_set_size = get_character_set_size(password)
    return len(password) * math.log2(char_set_size)

def analyze_password(password: str) -> dict:
    if not password:
        return {
            "score": 0,
            "entropy": 0,
            "feedback": {"warning": "Empty password", "suggestions": []},
            "crack_times": {},
            "regex_checks": {}
        }
    
    # ZXCVBN Analysis
    results = zxcvbn(password)
    
    # Entropy calculation
    entropy = calculate_entropy(password)
    
    # Regex Validation Checks
    regex_checks = {
        "length_8": len(password) >= 8,
        "uppercase": bool(re.search(r'[A-Z]', password)),
        "lowercase": bool(re.search(r'[a-z]', password)),
        "digits": bool(re.search(r'\d', password)),
        "special": bool(re.search(r'[!@#$%^&*()_+\-=\[\]{}|;\':\",./<>?\\ ]', password))
    }
    
    crack_times = results.get('crack_times_display', {})
    
    return {
        "score": results["score"],
        "entropy": round(entropy, 2),
        "feedback": results["feedback"],
        "crack_times": {
            "online_throttled": crack_times.get("online_throttling_100_per_hour", "Unknown"),
            "online_fast": crack_times.get("online_no_throttling_10_per_second", "Unknown"),
            "offline_slow": crack_times.get("offline_slow_hashing_1e4_per_second", "Unknown"),
            "offline_fast": crack_times.get("offline_fast_hashing_1e10_per_second", "Unknown")
        },
        "regex_checks": regex_checks
    }
