from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import os
import uvicorn
import webbrowser
import threading
import time

from stealthx_core.strength import analyze_password
from stealthx_core.generator import generate_password
from stealthx_core.simulation import create_hash, run_jtr_attack

from stealthx_core.hibp_checker import check_pwned_online
from stealthx_core.history import save_to_history, get_history

app = FastAPI(title="StealthX API")

# Ensure static directory exists (it will once we write those files)
os.makedirs("static", exist_ok=True)

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

class AnalyzeRequest(BaseModel):
    password: str

class GenerateRequest(BaseModel):
    length: int
    uppercase: bool
    lowercase: bool
    numbers: bool
    special: bool

class AttackRequest(BaseModel):
    password: str
    mode: str

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/analyze")
async def api_analyze(req: AnalyzeRequest):
    result = analyze_password(req.password)
    breaches = check_pwned_online(req.password)
    result["breaches"] = breaches
    
    save_to_history("Web GUI Analysis", {"score": result["score"], "breaches": breaches})
    return JSONResponse(result)

@app.post("/api/generate")
async def api_generate(req: GenerateRequest):
    pwd = generate_password(req.length, req.uppercase, req.lowercase, req.numbers, req.special)
    save_to_history("Web GUI Generation", {"length": req.length})
    return {"password": pwd}

@app.post("/api/attack")
async def api_attack(req: AttackRequest):
    hashed_pwd = create_hash(req.password)
    wordlist = "rockyou.txt"
    if req.mode == "dictionary":
        result = run_jtr_attack(hashed_pwd, "dictionary", wordlist)
    elif req.mode == "hybrid":
        result = run_jtr_attack(hashed_pwd, "hybrid", wordlist)
    else:
        # Simulate brute force delay
        time.sleep(2)
        result = {"success": False, "mode": "Simulated Web Brute-Force", "time_taken": 2.0}
        
    save_to_history("Web GUI Attack", {"mode": req.mode, "success": result.get("success")})
    return JSONResponse({"hash": hashed_pwd, "result": result})

class PwnedRequest(BaseModel):
    password: str

@app.post("/api/check-pwned")
async def api_check_pwned(req: PwnedRequest):
    breaches = check_pwned_online(req.password)
    save_to_history("Standalone Pwned Check", {"breaches": breaches})
    return JSONResponse({"breaches": breaches})

@app.get("/api/history")
async def api_history():
    return JSONResponse(get_history()[-15:])

def run_gui():
    print("Starting StealthX Web GUI on http://127.0.0.1:8000")
    
    # Auto-open browser
    def open_browser():
        time.sleep(1)
        webbrowser.open("http://127.0.0.1:8000")
        
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

if __name__ == "__main__":
    run_gui()
