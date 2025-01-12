def read_file(file_path):
    """Read content from a file."""
    with open(file_path, "r") as file:
        return file.read()

def write_to_log(log_path, content):
    """Write log entries to a file."""
    with open(log_path, "a") as log_file:
        log_file.write(content + "\n")
