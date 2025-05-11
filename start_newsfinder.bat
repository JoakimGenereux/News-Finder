@echo off
REM Start the FastAPI backend in its own window
start "NewsFinder Backend" cmd /k "uvicorn fast_api:app --reload"

REM Start the React frontend in its own window
start "NewsFinder Frontend" cmd /k "cd news_aggregator && npm start"
