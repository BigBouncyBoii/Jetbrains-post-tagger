# Pi Calculator with Celery and Flask

A Python application that calculates π (pi) to n decimal places using Celery for asynchronous processing with Redis as the message broker and Flask for HTTP API endpoints.

## Features

- **Asynchronous pi calculation** using the Leibniz formula with high precision
- **Progress tracking** with real-time updates
- **Flask REST API** with two endpoints:
  - `GET /calculate_pi?n=<decimal_places>` - Start calculation
  - `GET /check_progress?task_id=<task_id>` - Check progress and get results
- **Docker Compose** setup for easy deployment
- **High precision arithmetic** using Python's decimal module

## Prerequisites

- **Docker** and **Docker Compose**

## Quick Start with Docker Compose

1. **Build and start all services:**
```bash
docker-compose up --build
```

2. **Test the API:**
```bash
curl "http://localhost:5000/calculate_pi?n=10"
```

3. **Stop services:**
```bash
docker-compose down
```

## Docker Compose Services

The application includes these services:
- **redis**: Redis server for message broker and result backend
- **celery-worker**: Celery worker for processing pi calculations
- **flask-api**: Flask web API (available at http://localhost:5000)
- **celery-flower**: Optional monitoring UI (available at http://localhost:5555)

### Optional: Start with Celery monitoring
```bash
docker-compose --profile monitoring up --build
```

## Manual Installation (Alternative)

If you prefer to run without Docker:

### Prerequisites
1. **Redis** - Must be running on localhost:6379
2. **Python 3.7+** with pip

### Installation
1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running Manually
1. **Start Redis**: `redis-server`
2. **Start Celery Worker**: `celery -A endpoints worker --loglevel=info`
3. **Start Flask API**: `python app.py`

## API Documentation

### Start Pi Calculation
```
GET http://localhost:5000/calculate_pi?n=<decimal_places>
```
**Response:**
```json
{
  "task_id": "abc-123-def-456",
  "message": "Started calculating pi to 123 decimal places",
  "status": "started",
  "check_progress_url": "http://localhost:5000/check_progress?task_id=abc-123-def-456"
}
```

### Check Progress
```
GET http://localhost:5000/check_progress?task_id=abc-123-def-456
```

**Response (In Progress):**
```json
{
  "state": "PROGRESS",
  "progress": 0.25,
  "result": null
}
```
**Response (Finished):**
```json
{
  "state": "FINISHED",
  "progress": 1.0,
  "result": "3.1415926535897932384626433832795028841971693993751..."
}
```

## Example Usage

### Using curl:
```bash
# Start calculation for 50 decimal places
curl "http://localhost:5000/calculate_pi?n=50"

# Check progress (replace with actual task_id from above response)
curl "http://localhost:5000/check_progress?task_id=your-task-id-here"
```

### Using a web browser:
1. Go to http://localhost:5000/ for API documentation
2. Start calculation: http://localhost:5000/calculate_pi?n=10
3. Copy the task_id from the response
4. Check progress: http://localhost:5000/check_progress?task_id=YOUR_TASK_ID

## Docker Compose Commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Build and start
docker-compose up --build

# View logs
docker-compose logs

# View logs for specific service
docker-compose logs flask-api

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Start with monitoring (Flower)
docker-compose --profile monitoring up
```

## Architecture

- **endpoints.py**: Contains Celery tasks and Flask routes
- **app.py**: Flask application runner
- **docker-compose.yaml**: Docker Compose configuration
- **Dockerfile**: Python application container
- **Redis**: Message broker and result backend
- **Celery**: Task queue and worker process
- **Flask**: HTTP API server