FROM python:3.13-slim

WORKDIR /app

# Keep Python output unbuffered and avoid .pyc writes in containers.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install dependencies first for better layer cache reuse.
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend source after dependency install.
COPY . .

# Runtime defaults (can be overridden at docker run time).
ENV LAPAGENT_HOST=0.0.0.0 \
    LAPAGENT_PORT=8000 \
    LAPAGENT_RELOAD=false \
    LAPAGENT_ENV=production

EXPOSE 8000

RUN chmod +x /app/docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]
