#!/bin/bash

#alembic upgrade head

uvicorn main:app --host 127.0.0.1 --port 8000 --reload