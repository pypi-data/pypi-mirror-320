import time
from config.settings import COLORS

def fancy_print(text, color="reset"):
    """
    Print text with the specified color from COLORS.
    
    Args:
        text (str): The text to print.
        color (str): The color key from COLORS dictionary.
    """
    print(f"{COLORS.get(color, COLORS['reset'])}{text}{COLORS['reset']}")

def draw_separator():
    """Print a separator line."""
    print(COLORS['log'] + "-" * 50 + COLORS['reset'])

def typewriter_effect(text, delay=0.05):
    """
    Print text with a typewriter effect.
    
    Args:
        text (str): The text to print.
        delay (float): The delay between each character.
    """
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def animated_loading(message, duration=3):
    """
    Display an animated loading message.
    
    Args:
        message (str): The message to display.
        duration (int): The duration of the animation in seconds.
    """
    spinner = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    while time.time() < end_time:
        for frame in spinner:
            print(f"\r{message} {frame}", end='', flush=True)
            time.sleep(0.1)
    print("\r" + " " * len(message) + "\r", end='')  # Clear the line

def welcome_animation():
    """
    Display a dynamic welcome animation.
    """
    welcome_message = "Welcome to HackQuest!"
    for i in range(len(welcome_message) + 1):
        print("\r" + COLORS['info'] + welcome_message[:i] + COLORS['reset'], end='', flush=True)
        time.sleep(0.1)
    print()
