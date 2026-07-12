import re

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
API_KEY_RE = re.compile(r"\b(?:sk|pk|api|key|token)_[A-Za-z0-9_\-]{16,}\b", re.IGNORECASE)
BEARER_RE = re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE)
PASSWORD_RE = re.compile(r"(?i)(password|passwd|pwd|secret)\s*[:=]\s*([^\s,;]+)")
CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
DB_URL_RE = re.compile(r"\b(?:postgres|postgresql|mysql|mongodb|redis)://[^\s]+", re.IGNORECASE)


def redact_sensitive_text(value: str, *, redact_ips: bool = False) -> str:
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", value)
    redacted = API_KEY_RE.sub("[REDACTED_API_KEY]", redacted)
    redacted = BEARER_RE.sub("Bearer [REDACTED_TOKEN]", redacted)
    redacted = PASSWORD_RE.sub(lambda m: f"{m.group(1)}=[REDACTED_SECRET]", redacted)
    redacted = CARD_RE.sub("[REDACTED_CARD]", redacted)
    redacted = DB_URL_RE.sub("[REDACTED_DB_URL]", redacted)
    if redact_ips:
        redacted = IP_RE.sub("[REDACTED_IP]", redacted)
    return redacted


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", name).strip("._")
    return cleaned[:120] or "upload.txt"
