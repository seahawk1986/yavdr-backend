#!/usr/bin/bash
# pushd app
exec .venv-3.12/bin/uvicorn app.main:app --reload --host=0.0.0.0 --port=8000 --root-path /api --forwarded-allow-ips "*"
