@echo off
echo Starting Space360 Backend...
cd F:\Space360\backend
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload --port 8000
pause
