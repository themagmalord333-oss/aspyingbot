import os

def load_cookies(filepath=".cookies.txt"):
    """Reads simple key=value cookies from file for Fragment auth."""
    cookies = {}
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    cookies[key] = val
    return cookies