import re
from enum import StrEnum

critical_patterns = [
    re.compile(r"(API|KEY|SECRET|TOKEN)", re.IGNORECASE),
    re.compile(r"PASS(WORD)?$", re.IGNORECASE),
    re.compile(r"WEBHOOK", re.IGNORECASE),
    re.compile(r"PRIVATE", re.IGNORECASE),
    re.compile(r"MONGO.*_UR(I|L)", re.IGNORECASE),
    re.compile(r"BINANCE", re.IGNORECASE),
]

sensitive_patterns = [
    re.compile(r"(SMTP|MAIL)_USER", re.IGNORECASE),
    re.compile(r"MAIL$", re.IGNORECASE),
    re.compile(r"CHAT_ID$", re.IGNORECASE),
    re.compile(r"JWT", re.IGNORECASE),
    re.compile(r"URL", re.IGNORECASE),
    re.compile(r"PUBLIC", re.IGNORECASE)
]

noise_patterns = [
    # re.compile(r"^VITE.*", re.IGNORECASE),
    re.compile(r"^NODE", re.IGNORECASE),
    re.compile(r"PORT$", re.IGNORECASE),
    re.compile(r"HOST$", re.IGNORECASE),
    re.compile(r"^\s*$")  # empty/whitespace-only strings
]

value_noise_patterns = [
    re.compile(r"(sample|example)", re.IGNORECASE),
    re.compile(r"your", re.IGNORECASE),
    re.compile(r"company.com", re.IGNORECASE),
    re.compile(r"(localhost|127.0.0.1)", re.IGNORECASE),
    re.compile(r"(true|false)", re.IGNORECASE),
    re.compile(r"^[xX]+$"),   # only upper/lowercase 'x'
    re.compile(r"^\s*$")  # empty/whitespace-only strings
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
    lines = [line.strip() for line in content.splitlines() if line and "=" in line and not line.startswith("#")]

    result = []

    for line in lines:
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

