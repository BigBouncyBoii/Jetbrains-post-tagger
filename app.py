#!/usr/bin/env python3
"""
Flask app runner for Pi Calculator API
"""

from endpoints import flask_app

if __name__ == '__main__':
    print("Starting Pi Calculator Flask API...")
    print("Available endpoints:")
    print("  GET /                          - API documentation")
    print("  GET /calculate_pi?n=<digits>   - Start pi calculation")
    print("  GET /check_progress?task_id=<> - Check calculation progress")
    print()
    print("Make sure to:")
    print("1. Start Redis: redis-server")
    print("2. Start Celery worker: celery -A endpoints worker --loglevel=info")
    print("3. Then access the API at http://localhost:5000")
    
    flask_app.run(debug=True, host='0.0.0.0', port=5000)