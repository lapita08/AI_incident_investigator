#!/usr/bin/env python3
"""Load a bundled demo incident into a running local backend."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
SCENARIOS = ("db-latency-incident", "memory-leak-incident")


def post_json(url: str) -> dict:
    request = urllib.request.Request(url, data=b"", method="POST")
    request.add_header("Accept", "application/json")
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Load a sample incident into the local AI Incident Investigator backend.")
    parser.add_argument("scenario", nargs="?", default="db-latency-incident", choices=SCENARIOS)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"Backend base URL. Default: {DEFAULT_BASE_URL}")
    parser.add_argument("--analyze", action="store_true", help="Run investigation analysis after loading the sample.")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    try:
        incident = post_json(f"{base_url}/api/v1/incidents/sample/{args.scenario}")
        print(f"Loaded {args.scenario}")
        print(f"Incident: {incident['title']}")
        print(f"Incident ID: {incident['id']}")
        print(f"API: {base_url}/api/v1/incidents/{incident['id']}")

        if args.analyze:
            result = post_json(f"{base_url}/api/v1/incidents/{incident['id']}/analyze")
            print(f"Analysis status: {result['status']}")

        return 0
    except urllib.error.URLError as exc:
        print(f"Could not reach backend at {base_url}: {exc}", file=sys.stderr)
        print("Start it first with: make backend-dev", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

