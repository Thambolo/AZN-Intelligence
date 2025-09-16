#!/usr/bin/env bash
# Use PORT environment variable provided by Render
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4