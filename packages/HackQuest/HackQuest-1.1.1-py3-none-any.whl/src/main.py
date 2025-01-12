import sys
import os
from time import sleep
from random import choice

# Add the root directory of the project to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import COLORS, GAME_NAME, VERSION
from src.core.commands import execute_command
from src.levels.level1 import level1
from src.levels.level2 import level2
from src.levels.level3 import level3


def print_hack_animation():
    """Display a hacking animation."""
    os.system("clear")
    print(f"{COLORS['success']}Initializing HackQuest System...\n{COLORS['reset']}")
    for i in range(3):
        for char in "|/-\\":
            print(f"\r{COLORS['info']}Hacking in progress {char}{COLORS['reset']}", end="", flush=True)
            sleep(0.2)
    print(f"\r{COLORS['success']}HackQuest System Ready!{COLORS['reset']}\n")


def print_ascii_art():
    """Display cool ASCII art for the game."""
    ascii_art = f"""
{COLORS['warning']} 
██   ██  █████   ██████ ██   ██  ██████  ██    ██ ███████ ███████ ████████ 
██   ██ ██   ██ ██      ██  ██  ██    ██ ██    ██ ██      ██         ██    
███████ ███████ ██      █████   ██    ██ ██    ██ █████   ███████    ██    
██   ██ ██   ██ ██      ██  ██  ██ ▄▄ ██ ██    ██ ██           ██    ██    
██   ██ ██   ██  ██████ ██   ██  ██████   ██████  ███████ ███████    ██    
                                    ▀▀                                     
                                                                           
    {COLORS['reset']}
"""
    print(ascii_art)


def print_separator(style="-", length=60):
    """Print a stylish separator."""
    print(f"{COLORS['warning']}{style * length}{COLORS['reset']}")


def fancy_print(message, color, delay=0.04):
    """Print text with a typewriter effect."""
    for char in message:
        print(f"{color}{char}{COLORS['reset']}", end="", flush=True)
        sleep(delay)
    print()


def display_dynamic_quote():
    """Display a random hacking-related quote."""
    quotes = [
        "“Hack the planet!”",
        "“The quieter you become, the more you are able to hear.”",
        "“Every great hacker started as a script kiddie.”",
        "“Code is like humor. When you have to explain it, it’s bad.”",
        "“Knowledge is power, especially when it’s in the wrong hands”",
        "“The best hackers are the ones who solve problems without creating chaos.”",
        "“The true hacker is not the one who writes malicious code, but the one who finds elegant solutions to complex problems.”",
        "“Security through obscurity is not security—it's just obscurity.”",
        "“The only way to truly protect yourself is to understand your enemy.”",
        "“A master hacker isn’t measured by how many systems they break into, but by how many systems they leave secure.”",
        "“The lines between hacker, security expert, and criminal are often blurred.”",
        "“Hacking is not about breaking things; it’s about understanding how things work.”",
        "“In the world of cybercrime, knowledge is the key, but power is knowing when and how to use it.”",
        "“Hacking is an art, not a crime—until you use it to do harm.”",
        "“Hack the system, not the law.”",
        "“Hack smarter, not harder.”",
        "“Security is a process, not a product.”",
        "“Code is the new weapon.”",
        "“Break it to fix it.”",
        "“Hacking is thinking outside the code.”",
        "“Every lock has a key.”",
        "“In hacking, silence is golden.”",
        "“Knowledge is the ultimate exploit.”",
    ]
    fancy_print(choice(quotes), COLORS['info'])


def print_welcome_screen():
    """Display the dynamic welcome screen."""
    print_hack_animation()
    print_ascii_art()
    fancy_print(f"Welcome to {GAME_NAME} - Version {VERSION}", COLORS['success'])
    print_separator("=")
    fancy_print(
        "Embark on an epic journey to become the ultimate hacker! Solve challenges, "
        "decrypt files, and outsmart the system!", COLORS['warning']
    )
    print_separator("=")
    sleep(1)
    display_dynamic_quote()
    print()
    fancy_print("Type 'help' to view the available commands.", COLORS['info'])
    print_separator()


def display_help():
    """Show a polished help menu."""
    print_separator("=")
    fancy_print("Available Commands:", COLORS['success'])
    commands = [
        {"cmd": "help", "desc": "Show this help menu"},
        {"cmd": "level1", "desc": "Start Level 1 (Password Retrieval)"},
        {"cmd": "level2", "desc": "Start Level 2 (File Decryption)"},
        {"cmd": "level3", "desc": "Start Level 3 (Log Analysis)"},
        {"cmd": "exit", "desc": "Exit the game"},
        {"cmd": "scan / decrypt", "desc": "Simulate hacking tools"},
    ]
    for command in commands:
        fancy_print(f"- {command['cmd']:12}: {command['desc']}", COLORS['warning'])
    print_separator("=")


def display_loading(message, duration=2):
    """Show a loading animation with a custom message."""
    fancy_print(message, COLORS['info'])
    for _ in range(duration):
        print(f"{COLORS['info']}.", end="", flush=True)
        sleep(0.5)
    print(f"{COLORS['success']} Done!{COLORS['reset']}")


def main():
    """Main game loop."""
    print_welcome_screen()

    while True:
        try:
            command = input(f"{COLORS['success']}HackQuest >> {COLORS['reset']}").strip().lower()

            if command == "exit":
                print(f"{COLORS['success']}Exiting HackQuest. See you next time!{COLORS['reset']}")
                print_separator()
                break
            elif command == "help":
                display_help()
            elif command == "level1":
                display_loading("Loading Level 1...")
                level1()
            elif command == "level2":
                display_loading("Loading Level 2...")
                level2()
            elif command == "level3":
                display_loading("Loading Level 3...")
                level3()
            elif command in ["scan", "decrypt"]:
                print(f"{COLORS['success']}Simulating '{command}' command...{COLORS['reset']}")
                sleep(1)
                print(f"{COLORS['warning']}Result: Operation completed successfully!{COLORS['reset']}")
            else:
                print(f"{COLORS['error']}Invalid command! Type 'help' to see available commands.{COLORS['reset']}")
        except KeyboardInterrupt:
            print(f"\n{COLORS['warning']}Exiting HackQuest. Goodbye!{COLORS['reset']}")
            break
        except Exception as e:
            print(f"{COLORS['error']}An error occurred: {e}{COLORS['reset']}")


if __name__ == "__main__":
    main()
    
