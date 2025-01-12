import os
import re

PATTERNS = {
    "API Key": r"(api_key\s*=\s*['\"]\w+['\"])",
    "Password": r"(password\s*=\s*['\"]\w+['\"])",
    "Secret Key": r"(secret_key\s*=\s*['\"]\w+['\"])"
}

def scan_file(file_path):
    """Scan a file for hardcoded secrets."""
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            for key, pattern in PATTERNS.items():
                matches = re.findall(pattern, content)
                if matches:
                    results.append({"file": file_path, "issue": f"{key} found", "severity": "HIGH"})
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return results

def scan_directory(directory="."):
    """Recursively scan all files in the given directory."""
    results = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".py", ".txt", ".env")):
                file_path = os.path.join(root, file)
                results.extend(scan_file(file_path))
    return results
