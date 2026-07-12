from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter("aiii_http_requests_total", "HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("aiii_http_request_duration_seconds", "HTTP request latency", ["method", "path"])
ERROR_COUNT = Counter("aiii_errors_total", "Application errors", ["operation", "error_type"])
EVIDENCE_INGESTION_COUNT = Counter("aiii_evidence_ingested_total", "Evidence ingestion count", ["type"])
PARSING_FAILURES = Counter("aiii_parsing_failures_total", "Evidence parsing failures", ["type"])
ANALYSIS_DURATION = Histogram("aiii_analysis_duration_seconds", "Analysis duration")
LLM_DURATION = Histogram("aiii_llm_request_duration_seconds", "LLM request duration", ["provider"])
LLM_FAILURES = Counter("aiii_llm_failures_total", "LLM request failures", ["provider"])
HYPOTHESIS_GENERATION_COUNT = Counter("aiii_hypotheses_generated_total", "Hypotheses generated", ["provider"])


def prometheus_payload() -> bytes:
    return generate_latest()

