import random
from time import sleep
from config.settings import COLORS
from utils.ui import fancy_print

def level1():
    fancy_print("Welcome to Level 1: Password Retrieval Challenge", COLORS['info'])
    fancy_print("Objective: Identify the correct password from the hints provided.", COLORS['hint'])

    # Generate a random password and hints
    password = "".join(random.sample("abcdefghijklmnopqrstuvwxyz1234567890", 8))
    hint = f"The password contains {len(password)} characters and starts with '{password[0]}' and ends with '{password[-1]}'."

    # Display the hint
    fancy_print("Hint:", COLORS['info'])
    fancy_print(hint, COLORS['success'])

    # Allow 3 attempts
    attempts = 3
    while attempts > 0:
        fancy_print(f"\nAttempts remaining: {attempts}", COLORS['warning'])
        user_input = input("Enter the password: ").strip()
        if user_input == password:
            fancy_print("Correct! You've unlocked Level 1.", COLORS['success'])
            return True
        else:
            fancy_print("Incorrect password.", COLORS['error'])
            attempts -= 1

    fancy_print("Game Over! Better luck next time.", COLORS['error'])
    return False
    
