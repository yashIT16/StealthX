import secrets
import string

def generate_password(length: int = 16, use_uppercase: bool = True, use_lowercase: bool = True, use_numbers: bool = True, use_special: bool = True) -> str:
    if length < 4:
        length = 4 # Enforce minimum lengths
    
    chars = ""
    if use_lowercase:
        chars += string.ascii_lowercase
    if use_uppercase: 
        chars += string.ascii_uppercase
    if use_numbers: 
        chars += string.digits
    if use_special: 
        chars += "!@#$%^&*()_+-=[]{}|;':\",./<>?\\"
    
    if not chars:
        chars = string.ascii_lowercase
        use_lowercase = True
    
    # Ensure at least one of each requested type is present
    password = []
    if use_lowercase: password.append(secrets.choice(string.ascii_lowercase))
    if use_uppercase: password.append(secrets.choice(string.ascii_uppercase))
    if use_numbers: password.append(secrets.choice(string.digits))
    if use_special: password.append(secrets.choice("!@#$%^&*()_+-=[]{}|;':\",./<>?\\"))
    
    # Fill the rest
    while len(password) < length:
        password.append(secrets.choice(chars))
        
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)
