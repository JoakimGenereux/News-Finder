@echo off
REM Start the FastAPI backend in its own window
start "NewsFinder Backend" cmd /k "venv\Scripts\activate && uvicorn fast_api:app --reload"

REM Start the React frontend in its own window
start "NewsFinder Frontend" cmd /k "cd news-aggregator && npm start"
