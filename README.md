# LAPAGENT

## Requirements:

### 1 Use the .sh scripts for testing

## The updation records

### 0.0.1 Realize the mini frontend and backend

### 0.0.2 Realize the mini database connection

### 0.0.3 Add in the cryptography security,realize mini AI-API connection

### 0.0.4 Fix the problem of API leakage, optimize the database

### 0.0.5 Work for conservation administration

### 0.0.6 Fix the existing bug, complete the basic conversation functions

### 0.0.7 Construct logging module

### 0.0.8 Make the key information embedded in environment variables and Docker configuration

This is the preparation for encapsulated distributtion

### 0.0.9 Add the Simple Redit Functions

## Backend Docker (Python 3.13 slim)

### Build

```bash
docker build -t lapagent-backend:latest ./backend
```

Docker build installs backend dependencies from [backend/requirements.txt](backend/requirements.txt).

### Run (production)

```bash
docker run --rm -p 8000:8000 \
	-e LAPAGENT_ENV=production \
	-e LAPAGENT_PORT=8000 \
	-e LAPAGENT_API_KEY="<your_api_key>" \
	-e LAPAGENT_API_PROVIDER="OpenAI" \
	-e LAPAGENT_API_MODEL="gpt-4o-mini" \
	lapagent-backend:latest
```

### Run (development with reload)

```bash
docker run --rm -p 8000:8000 \
	-e LAPAGENT_ENV=development \
	-e LAPAGENT_RELOAD=true \
	-e LAPAGENT_PORT=8000 \
	-e LAPAGENT_API_KEY="<your_api_key>" \
	-e LAPAGENT_API_PROVIDER="OpenAI" \
	-e LAPAGENT_API_MODEL="gpt-4o-mini" \
	lapagent-backend:latest
```

crpyography would deal ** dialogue data(DB) ** in database and ** API_KEY(AI) ** in .ini