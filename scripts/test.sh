#!/usr/bin/env bash
set -euo pipefail

python -m pytest backend/tests -q
npm --prefix frontend test
npm --prefix frontend run build
