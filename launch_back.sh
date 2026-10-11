# running the backend
cd backend
uvicorn app.main:app --reload --port 8000
# running the frontend
cd ../frontend/sources
python -m http.server 8080