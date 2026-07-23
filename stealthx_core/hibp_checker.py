import hashlib
import requests
import sqlite3
import os

def check_pwned_online(password: str) -> int:
    """Checks the HIBP online K-anonymity API."""
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1_hash[:5], sha1_hash[5:]
    
    try:
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return -1 # Error
        
        hashes = (line.split(':') for line in response.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                return int(count)
        return 0
    except requests.RequestException:
        return -1


def setup_mock_offline_db():
    """Sets up a mock offline breach database for demonstration."""
    db_path = "mock_breaches.db"
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE breaches (hash TEXT PRIMARY KEY)")
        
        # Insert a few common hashes (e.g., password, 123456)
        mock_passwords = ["password", "123456", "qwerty", "admin"]
        for p in mock_passwords:
            h = hashlib.sha1(p.encode('utf-8')).hexdigest().upper()
            cursor.execute("INSERT OR IGNORE INTO breaches (hash) VALUES (?)", (h,))
        
        conn.commit()
        conn.close()

def check_pwned_offline(password: str) -> bool:
    """Checks against a local mock database (simulating a 20GB HIBP DB)."""
    setup_mock_offline_db()
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    
    conn = sqlite3.connect("mock_breaches.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM breaches WHERE hash=?", (sha1_hash,))
    found = cursor.fetchone() is not None
    conn.close()
    
    return found
