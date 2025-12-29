#!/usr/bin/bash
# pushd yavdr_backend
exec uv run uvicorn yavdr_backend.main:app --reload \
 --host=0.0.0.0 --port=8000 \
 --root-path /api \
 --reload-exclude '**/node_modules/*' \
 --reload-exclude '**/.git/*' \
 --reload-exclude '**/venv/*' \
 --reload-exclude '**/__pycache__/*' \
 --reload-exclude '**/*.pyc' \
 --forwarded-allow-ips "*" \
