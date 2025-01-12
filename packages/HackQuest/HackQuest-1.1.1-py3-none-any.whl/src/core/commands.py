def execute_command(command):
    """Simulate execution of hacking commands."""
    if command == "scan":
        return "Scanning target... Found open ports: 22, 80, 443."
    elif command == "decrypt":
        return "Decryption module activated."
    elif command.startswith("connect"):
        return f"Connecting to {command.split()[1]}... Connection established."
    else:
        return "Invalid command. Type 'help' for a list of commands."

