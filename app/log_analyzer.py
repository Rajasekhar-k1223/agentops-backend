# log_analyzer.py - NLP Log Analyzer and AI Fix Recommender

import re
from typing import Dict

# Sample rule-based patterns (can expand with NLP/LLM)
ERROR_PATTERNS = {
    "permission denied": "Try running with elevated privileges (sudo/admin).",
    "command not found": "Check if the package is installed or available in PATH.",
    "unable to locate package": "Verify the package name or update apt sources.",
    "no module named": "Consider installing the missing Python module via pip."
}

def analyze_logs(stdout: str, stderr: str) -> Dict:
    """
    Simple rule-based NLP log analyzer. Returns interpretation and suggested fix.
    """
    combined_logs = f"{stdout}\n{stderr}".lower()
    result = {
        "category": "success" if not stderr else "error",
        "issues": [],
        "suggestions": []
    }

    for pattern, fix in ERROR_PATTERNS.items():
        if re.search(pattern, combined_logs):
            result["issues"].append(pattern)
            result["suggestions"].append(fix)

    return result

# ========== Test ==========
if __name__ == "__main__":
    out = analyze_logs("", "bash: nginx: command not found")
    print("\n=== Log Analysis ===")
    print(out)
