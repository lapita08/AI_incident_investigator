#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/frontend"

if ! command -v pnpm >/dev/null 2>&1; then
  if command -v corepack >/dev/null 2>&1; then
    corepack enable
  else
    echo "pnpm is required. Install Node with Corepack or install pnpm directly." >&2
    exit 1
  fi
fi

exec pnpm run dev -- --host 0.0.0.0 --port "${PORT:-5173}"

