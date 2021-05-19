#!/usr/bin/bash
pushd app
exec ../.venv/bin/uvicorn main:app --reload --host=0.0.0.0 --port=8000