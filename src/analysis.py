import re

critical_patterns = [
    re.compile(r".*API_KEY$", re.IGNORECASE),
    re.compile(r".*SECRET.*", re.IGNORECASE),
    re.compile(r".*TOKEN$", re.IGNORECASE),
    re.compile(r".*PASS$", re.IGNORECASE),
    re.compile(r".*PASSWORD$", re.IGNORECASE),
    re.compile(r".*WEBHOOK.*", re.IGNORECASE),
    re.compile(r"PRIVATE_KEY", re.IGNORECASE),
    re.compile(r"MONGO.*_URI", re.IGNORECASE),
]

sensitive_patterns = [
    re.compile(r"SMTP_USER", re.IGNORECASE),
    re.compile(r"MAIL_USER", re.IGNORECASE),
    re.compile(r".*MAIL$", re.IGNORECASE),
    re.compile(r".*CHAT_ID$", re.IGNORECASE),
]

noise_patterns = [
    re.compile(r"^VITE.*", re.IGNORECASE),
    re.compile(r"^NODE.*", re.IGNORECASE),
    re.compile(r".*PORT$", re.IGNORECASE),
    re.compile(r".*HOST$", re.IGNORECASE),
    re.compile(r" *", re.IGNORECASE)
]

def classify_env_key(key: str):
    key = key.strip().upper()

    for pattern in critical_patterns:
        if pattern.match(key):
            return "critical"
    for pattern in sensitive_patterns:
        if pattern.match(key):
            return "sensitive"
    for pattern in noise_patterns:
        if pattern.match(key):
            return "noise"

    return "unknown"

def analyze_env_file(content: str):
    result = []

    for line in content.split("\n"):
        line = line.strip()

        if not len(line): continue

        if line.startswith("#"): continue
        if "=" not in line: continue

        key, value = line.split("=", 1)

        key = key.strip().upper()
        value = value.strip()

        if not value: continue

        result.append({
            "severity": classify_env_key(key),
            "key": key,
            "value": value
        })

    return result

