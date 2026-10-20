docker run -p 8000:8000 \
-v "$(pwd)/../backend/public:/app/public" \
-v "$(pwd)/../backend/Database:/app/Database" \
lapagent-backend:latest