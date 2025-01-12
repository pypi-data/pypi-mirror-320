import random
from time import sleep
from config.settings import COLORS
from utils.ui import fancy_print

def level2():
    fancy_print("Welcome to Level 2: File Decryption Challenge", COLORS['info'])
    fancy_print("Objective: Decrypt the file contents using the provided key.", COLORS['hint'])

    # Simulate an encrypted file and a decryption key
    original_message = "HACKQUESTROCKS"
    encryption_key = random.randint(1, 9)
    encrypted_message = "".join([chr(ord(char) + encryption_key) for char in original_message])

    # Display encrypted message
    fancy_print("\nEncrypted Message:", COLORS['info'])
    fancy_print(encrypted_message, COLORS['success'])

    # Decrypting process
    attempts = 3
    while attempts > 0:
        fancy_print(f"\nAttempts remaining: {attempts}", COLORS['warning'])
        try:
            user_key = int(input("Enter the decryption key (1-9): ").strip())
            if user_key == encryption_key:
                fancy_print("Decryption successful!", COLORS['success'])
                fancy_print(f"The original message was: {original_message}", COLORS['success'])
                return True
            else:
                fancy_print("Incorrect key.", COLORS['error'])
                attempts -= 1
        except ValueError:
            fancy_print("Invalid input. Please enter a number.", COLORS['error'])

    fancy_print("Game Over! Better luck next time.", COLORS['error'])
    return False
    
