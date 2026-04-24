import re
from enum import StrEnum


critical_patterns = [
    re.compile(r"(API|KEY|SECRET|TOKEN)", re.IGNORECASE),
    re.compile(r"PASS(WORD)?$", re.IGNORECASE),
    re.compile(r"WEBHOOK", re.IGNORECASE),
    re.compile(r"PRIVATE_KEY", re.IGNORECASE),
    re.compile(r"MONGO.*_URI", re.IGNORECASE),
]

sensitive_patterns = [
    re.compile(r"(SMTP|MAIL)_USER", re.IGNORECASE),
    re.compile(r"MAIL$", re.IGNORECASE),
    re.compile(r"CHAT_ID$", re.IGNORECASE),
]

noise_patterns = [
    # re.compile(r"^VITE.*", re.IGNORECASE),
    re.compile(r"^NODE", re.IGNORECASE),
    re.compile(r"PORT$", re.IGNORECASE),
    re.compile(r"HOST$", re.IGNORECASE),
    re.compile(r"^\s*$")  # empty/whitespace-only strings
]

value_noise_patterns = [
    re.compile(r"sample", re.IGNORECASE),
    re.compile(r"your", re.IGNORECASE)
]



class Severity(StrEnum):
    CRITICAL = "critical"
    SENSITIVE = "sensitive"
    NOISE = "noise"
    UNKNOWN = "unknown"


def classify_env_key(key: str) -> Severity:
    key = key.strip().upper()

    for pattern in critical_patterns:
        if pattern.search(key):
            return Severity.CRITICAL
    for pattern in sensitive_patterns:
        if pattern.search(key):
            return Severity.SENSITIVE
    for pattern in noise_patterns:
        if pattern.search(key):
            return Severity.NOISE

    return Severity.UNKNOWN


def analyze_env_file(content: str):
    lines = [line.strip() for line in content.splitlines() if line and "=" in line and not line.startswith("#")]

    result = []

    for line in lines:
        line = line.strip()

        k, v = line.split("=", 1)

        k = k.strip().upper()
        v = v.strip()

        if not v: continue

        if any(noise_pattern.search(v) for noise_pattern in value_noise_patterns):
            result.append({
                "severity": Severity.NOISE,
                "key": k,
                "value": v
            })
            continue

        result.append({
            "severity": classify_env_key(k),
            "key": k,
            "value": v
        })

    return result

