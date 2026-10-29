# If you want to monitor in terminal, remove the -d parameter
docker run -d \
  --name lapagent-redis \
  -p 127.0.0.1:6379:6379 \
  redis:7-alpine