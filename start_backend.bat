@echo off

echo Starting PostgreSQL...
docker compose up -d

echo Starting FastAPI backend...
cd backend
call .venv\Scripts\activate
uvicorn main:app --reload

