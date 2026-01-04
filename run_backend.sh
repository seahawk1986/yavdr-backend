#!/usr/bin/bash

exec uv run uvicorn yavdr_backend.main:app --reload \
 --host=0.0.0.0 --port=8000 \
 --reload-exclude '**/node_modules/*' \
 --reload-exclude '**/.git/*' \
 --reload-exclude '**/venv/*' \
 --reload-exclude '**/__pycache__/*' \
 --reload-exclude '**/*.pyc' \
 --forwarded-allow-ips "127.0.0.1" \
