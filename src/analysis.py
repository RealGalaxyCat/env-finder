import re
from enum import StrEnum

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
    # re.compile(r"^VITE.*", re.IGNORECASE),
    re.compile(r"^NODE.*", re.IGNORECASE),
    re.compile(r".*PORT$", re.IGNORECASE),
    re.compile(r".*HOST$", re.IGNORECASE),
    re.compile(r" *", re.IGNORECASE)
]


class Severity(StrEnum):
    CRITICAL = "critical"
    SENSITIVE = "sensitive"
    NOISE = "noise"
    UNKNOWN = "unknown"


def classify_env_key(key: str) -> Severity:
    key = key.strip().upper()

    for pattern in critical_patterns:
        if pattern.match(key):
            return Severity.CRITICAL
    for pattern in sensitive_patterns:
        if pattern.match(key):
            return Severity.SENSITIVE
    for pattern in noise_patterns:
        if pattern.match(key):
            return Severity.NOISE

    return Severity.UNKNOWN


def analyze_env_file(content: str):
    result = []

    for line in content.splitlines():
        line = line.strip()

        if not line: continue
        if line.startswith("#"): continue
        if "=" not in line: continue

        k, v = line.split("=", 1)

        k = k.strip().upper()
        v = v.strip()

        if not v: continue

        result.append({
            "severity": classify_env_key(k),
            "key": k,
            "value": v
        })

    return result

