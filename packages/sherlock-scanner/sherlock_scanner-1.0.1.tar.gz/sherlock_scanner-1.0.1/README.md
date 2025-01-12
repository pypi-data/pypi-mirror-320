# Sherlock Scanner

Sherlock is a Python-based security scanner designed to detect hardcoded secrets and API keys in files and directories.

## Features
- ✅ Scans for API keys, passwords, and secrets in codebases.
- ✅ CLI-based tool for easy use in CI/CD pipelines.
- ✅ Recursively scans files and directories.

## Installation
### You can install Sherlock directly from PyPI:
```
pip install sherlock-scanner
```

### Scan the current directory for secrets
```
sherlock .
```

### Scan a specific folder
```
sherlock /path/to/code
```

## Example Output:
```
⚠️ Security issues found:
[
  {
    "file": "example.py",
    "issue": "API Key found",
    "severity": "HIGH"
  }
]
```