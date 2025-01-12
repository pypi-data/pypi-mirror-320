import random
from time import sleep
from config.settings import COLORS
from utils.ui import fancy_print

def level3():
    fancy_print("Welcome to Level 3: Log Analysis Challenge", COLORS['info'])
    fancy_print("Objective: Identify the anomaly in the server logs.", COLORS['hint'])

    # Generate fake logs and inject an anomaly
    log_entries = [f"192.168.1.{random.randint(1, 100)} - OK" for _ in range(10)]
    anomaly_ip = f"10.0.0.{random.randint(1, 100)}"
    log_entries.insert(random.randint(0, len(log_entries) - 1), f"{anomaly_ip} - MALICIOUS")

    # Display the logs
    fancy_print("\nServer Logs:", COLORS['info'])
    for log in log_entries:
        fancy_print(log, COLORS['log'])
        sleep(0.5)

    # Prompt user to identify the anomaly
    attempts = 3
    while attempts > 0:
        fancy_print(f"\nAttempts remaining: {attempts}", COLORS['warning'])
        user_input = input("Which IP address is malicious? ").strip()
        if user_input == anomaly_ip:
            fancy_print("Correct! You've identified the anomaly.", COLORS['success'])
            return True
        else:
            fancy_print("Incorrect IP address.", COLORS['error'])
            attempts -= 1

    fancy_print("Game Over! Better luck next time.", COLORS['error'])
    return False
    
