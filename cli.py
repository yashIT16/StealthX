import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich.progress import track
from colorama import init
import time
import os
import getpass

# Initialize colorama and rich console
init()
console = Console()

from stealthx_core.strength import analyze_password
from stealthx_core.generator import generate_password
from stealthx_core.simulation import create_hash, run_jtr_attack
from stealthx_core.hibp_checker import check_pwned_online, check_pwned_offline
from stealthx_core.history import save_to_history, get_history

BANNER = r"""[bold bright_green]
  ___________________              .__    __  .__      ____  ___
 /   _____/|__\__    /____ _____  |  | _/  |_|  |__   \   \/  /
 \_____  \ |  | |    |/     \\__  \ |  | \   __\  |  \   \     / 
 /        \|  | |    |  Y Y  \/ __ \|  |__|  | |   Y  \  /     \ 
/_______  /|__| |____|__|_|  (____  /____/|__| |___|  / /___/\  \
        \/                 \/     \/                \/        \_/
[/bold bright_green]
[bold bright_blue]   Cybersecurity Toolkit | Password Auditing & Simulation System   [/]
"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    console.print(Panel(BANNER, border_style="bright_blue", expand=False))

def menu_strength():
    console.print("\n[bold cyan]--- Password Strength Analysis ---[/]")
    password = getpass.getpass("Enter password to analyze (input hidden): ")
    if not password:
        return
        
    analysis = analyze_password(password)
    
    # Visual Strength Bar
    colors = ["red", "dark_orange", "yellow", "green_yellow", "bright_green"]
    labels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"]
    score = analysis["score"]
    
    bar = f"[{colors[score]}]{'▓' * (score + 1)}{'░' * (4 - score)}[/] [bold {colors[score]}]{labels[score]}[/]"
    
    table = Table(title="Analysis Results", border_style="bright_blue")
    table.add_column("Metric", style="cyan")
    table.add_column("Value / Status", style="bright_white")
    
    table.add_row("Entropy", f"{analysis['entropy']} bits")
    table.add_row("Strength Score", f"{score}/4 - {bar}")
    table.add_row("Regex Length >= 8", "[green]Pass[/]" if analysis["regex_checks"]["length_8"] else "[red]Fail[/]")
    table.add_row("Regex Uppercase", "[green]Pass[/]" if analysis["regex_checks"]["uppercase"] else "[red]Fail[/]")
    table.add_row("Regex Lowercase", "[green]Pass[/]" if analysis["regex_checks"]["lowercase"] else "[red]Fail[/]")
    table.add_row("Regex Digits", "[green]Pass[/]" if analysis["regex_checks"]["digits"] else "[red]Fail[/]")
    table.add_row("Regex Special", "[green]Pass[/]" if analysis["regex_checks"]["special"] else "[red]Fail[/]")
    
    console.print(table)
    
    crack_table = Table(title="Estimated Crack Times", border_style="bright_magenta")
    crack_table.add_column("Scenario", style="bright_yellow")
    crack_table.add_column("Time", style="bright_red")
    
    ct = analysis["crack_times"]
    crack_table.add_row("Online (100/hr)", ct.get("online_throttled", "N/A"))
    crack_table.add_row("Online Fast (10/sec)", ct.get("online_fast", "N/A"))
    crack_table.add_row("Offline Slow (1e4/sec)", ct.get("offline_slow", "N/A"))
    crack_table.add_row("Offline Fast (1e10/sec)", ct.get("offline_fast", "N/A"))
    
    console.print(crack_table)
    
    if analysis["feedback"]["warning"]:
        console.print(f"[bold red]Warning:[/] {analysis['feedback']['warning']}")
    if analysis["feedback"]["suggestions"]:
        for sug in analysis["feedback"]["suggestions"]:
            console.print(f"  [bright_yellow]* {sug}[/]")
            
    # Check breaches
    if Confirm.ask("Check if this password has been in a data breach? (via HIBP API)"):
        with console.status("[bold cyan]Checking databases..."):
            breaches = check_pwned_online(password)
        if breaches > 0:
            console.print(f"[bold red]DANGER: Password has been seen {breaches} times in known data breaches![/]")
        elif breaches == 0:
            console.print("[bold bright_green]GOOD: Password not found in known breaches.[/]")
        else:
            console.print("[dim red]Error contacting HIBP API.[/]")
            
    # Save to history without the sensitive password
    save_to_history("Strength Analysis", {
        "entropy": analysis['entropy'],
        "score": score,
        "breaches_found": breaches if 'breaches' in locals() else None
    })
    
    Prompt.ask("\nPress Enter to return")

def menu_generator():
    console.print("\n[bold cyan]--- Secure Password Generator ---[/]")
    length = IntPrompt.ask("Password Length", default=16)
    use_upper = Confirm.ask("Include Uppercase?", default=True)
    use_lower = Confirm.ask("Include Lowercase?", default=True)
    use_nums = Confirm.ask("Include Numbers?", default=True)
    use_spec = Confirm.ask("Include Special Characters?", default=True)
    
    pwd = generate_password(length, use_upper, use_lower, use_nums, use_spec)
    
    console.print(Panel(f"[bold bright_green]{pwd}[/]", title="Generated Password", border_style="cyan"))
    
    save_to_history("Password Generated", {"length": length})
    Prompt.ask("\nPress Enter to return")

def menu_attack():
    console.print("\n[bold cyan]--- Attack Simulation ---[/]")
    console.print("Demonstrating password hashing and cracking techniques.")
    password = Prompt.ask("Enter a password to act as the target")
    
    console.print("[dim]Hashing target password using passlib (MD5Crypt)...[/]")
    p_hash = create_hash(password)
    console.print(f"Target Hash: [bright_magenta]{p_hash}[/]")
    
    wordlist = "rockyou.txt"
    if not os.path.exists(wordlist):
        console.print("[red]Warning: rockyou.txt not found in current directory. Dictionary attack may fail.[/]")
    
    console.print("\nSelect Attack Mode:")
    console.print("1. Dictionary Attack (using rockyou.txt)")
    console.print("2. Hybrid Attack (Dictionary + Digits)")
    console.print("3. Brute-Force Output Only (No JtR needed for UI demo)")
    
    choice = Prompt.ask("Mode", choices=["1", "2", "3"])
    
    if choice == "1":
        with console.status("[bold bright_red]Running attack simulation...[/]"):
            result = run_jtr_attack(p_hash, "dictionary", wordlist_path=wordlist)
    elif choice == "2":
        with console.status("[bold bright_red]Running hybrid simulation (Max 4.5s)...[/]"):
            result = run_jtr_attack(p_hash, "hybrid", wordlist_path=wordlist)
    else:
        # Just simulate time passage for brute force since true CPU brute forcing is complex natively
        for _ in track(range(100), description="[red]Simulating Incremental Brute-Force...[/]"):
            time.sleep(0.02)
        result = {"success": False, "mode": "Simulated Brute-Force"}
        
    console.print("\n[bold]Attack Summary:[/]")
    if result.get("success"):
        console.print(f"[bold bright_green]CRACKED![/] Password: '{result['password']}'")
        console.print(f"Time Taken: {result['time_taken']}s | Mode: {result['mode']}")
    else:
        console.print(f"[bold bright_red]NOT CRACKED.[/]")
        console.print(f"Error: {result.get('error', 'Password too complex or not in dictionary.')}")
        
    save_to_history("Attack Simulation", {
        "success": result.get("success", False),
        "mode": result.get("mode", "Unknown")
    })
    
    Prompt.ask("\nPress Enter to return")

def menu_history():
    console.print("\n[bold cyan]--- Session History ---[/]")
    records = get_history()
    
    if not records:
        console.print("[dim]No history records found.[/]")
    else:
        table = Table(title="Recent Actions", border_style="dim")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Type", style="bright_blue")
        table.add_column("Details", justify="left")
        
        for r in reversed(records[-10:]): # Show last 10
            details_str = str(r["details"])
            table.add_row(r["timestamp"][:19].replace("T", " "), r["type"], details_str)
            
        console.print(table)
        
    Prompt.ask("\nPress Enter to return")

def main():
    while True:
        print_banner()
        console.print("1. [cyan]Password Strength Analysis[/]")
        console.print("2. [cyan]Secure Password Generator[/]")
        console.print("3. [cyan]Attack Simulation (JtR / Native)[/]")
        console.print("4. [cyan]View Session History[/]")
        console.print("5. [cyan]Exit[/]")
        
        choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            menu_strength()
        elif choice == "2":
            menu_generator()
        elif choice == "3":
            menu_attack()
        elif choice == "4":
            menu_history()
        elif choice == "5":
            console.print("[bold bright_green]Exiting StealthX. Stay secure![/]")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold bright_green]Exiting StealthX. Stay secure![/]")
        sys.exit(0)
