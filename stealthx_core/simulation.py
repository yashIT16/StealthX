import subprocess
import time
import os
from passlib.hash import md5_crypt

def create_hash(password: str) -> str:
    """Hashes the password using passlib MD5Crypt."""
    return md5_crypt.hash(password)

def native_dictionary_attack(hashed_pwd: str, wordlist_path: str, limit_seconds: float = 4.5) -> dict:
    """A pure python fallback for dictionary attack."""
    start_time = time.time()
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for word in f:
                word = word.strip()
                
                # Enforce sub-5-second limit
                if time.time() - start_time >= limit_seconds:
                    return {"success": False, "error": f"Dictionary Attack timed out at {limit_seconds}s limit", "time_taken": round(time.time() - start_time, 2), "mode": "Python Native Dictionary (Timed Out)"}
                    
                if md5_crypt.verify(word, hashed_pwd):
                    return {
                        "success": True,
                        "password": word,
                        "time_taken": round(time.time() - start_time, 2),
                        "mode": "Python Native Dictionary"
                    }
    except FileNotFoundError:
        return {"success": False, "error": "Wordlist not found", "time_taken": 0, "mode": "Python Native Dictionary"}
    
    return {"success": False, "time_taken": round(time.time() - start_time, 2), "mode": "Python Native Dictionary"}


def native_hybrid_attack(hashed_pwd: str, wordlist_path: str, limit_seconds: float = 4.5) -> dict:
    """A pure python fallback for hybrid attack (Dictionary + Append Numbers).
    Times out aggressively at `limit_seconds` to ensure rapid response.
    """
    start_time = time.time()
    
    # Common numeric suffixes to try appending to dictionary words
    suffixes = ["123", "1", "12", "1234", "12345", "69", "2023", "2024", "420", "666"]
    
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for word in f:
                word = word.strip()
                
                # Check timeout before inner loop
                if time.time() - start_time >= limit_seconds:
                    return {"success": False, "error": f"Hybrid Attack timed out at {limit_seconds}s limit", "time_taken": round(time.time() - start_time, 2), "mode": "Python Native Hybrid (Timed Out)"}
                    
                for suffix in suffixes:
                    hybrid_word = f"{word}{suffix}"
                    if md5_crypt.verify(hybrid_word, hashed_pwd):
                        return {
                            "success": True,
                            "password": hybrid_word,
                            "time_taken": round(time.time() - start_time, 2),
                            "mode": "Python Native Hybrid"
                        }
    except FileNotFoundError:
        return {"success": False, "error": "Wordlist not found", "time_taken": 0, "mode": "Python Native Hybrid"}
    
    return {"success": False, "time_taken": round(time.time() - start_time, 2), "mode": "Python Native Hybrid"}


def run_jtr_attack(hashed_pwd: str, mode: str, wordlist_path: str = None) -> dict:
    """Attempts to run John the Ripper via subprocess. Falls back to native."""
    hash_file = "temp_hash.txt"
    with open(hash_file, "w") as f:
        f.write(hashed_pwd)
    
    # Check if John is installed
    try:
        subprocess.run(["john", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        jtr_available = True
    except (FileNotFoundError, subprocess.CalledProcessError):
        jtr_available = False
        
    if not jtr_available:
        os.remove(hash_file)
        if mode == "dictionary" and wordlist_path:
            return native_dictionary_attack(hashed_pwd, wordlist_path)
        elif mode == "hybrid" and wordlist_path:
            return native_hybrid_attack(hashed_pwd, wordlist_path)
        else:
            return {
                "success": False, 
                "error": "JtR not found and native fallback requires a wordlist for dictionary mode.",
                "mode": "Fallback Failed"
            }
            
    # Try running JtR
    start_time = time.time()
    cmd = ["john", f"--format=md5crypt"]
    if mode == "dictionary" and wordlist_path:
        cmd.append(f"--wordlist={wordlist_path}")
    elif mode == "hybrid" and wordlist_path:
        cmd.append(f"--wordlist={wordlist_path}")
        # Note: JtR handles rules differently, but --rules handles hybrid. Native is preferred for strict 5s.
        cmd.append("--rules")
        
    cmd.append(hash_file)
    
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        
        # Read the result
        show_cmd = ["john", "--show", hash_file]
        res = subprocess.run(show_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Parse output for cracked password
        cracked = None
        for line in res.stdout.splitlines():
            if ":" in line and hashed_pwd in line:
                # John output format: hash:password
                parts = line.split(":")
                if len(parts) > 1:
                    cracked = parts[1]
                    break
        
        # Clean up john pot file to discard cache if needed
        # (ignoring for now as it's just a simulation)
    except subprocess.TimeoutExpired:
        os.remove(hash_file)
        return {"success": False, "error": "Attack timed out", "time_taken": 60, "mode": f"JtR {mode}"}
    finally:
        if os.path.exists(hash_file):
            os.remove(hash_file)
            
    if cracked:
        return {
            "success": True,
            "password": cracked,
            "time_taken": round(time.time() - start_time, 2),
            "mode": f"JtR {mode}"
        }
    
    return {
        "success": False,
        "time_taken": round(time.time() - start_time, 2),
        "mode": f"JtR {mode}"
    }
