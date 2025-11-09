from celery import Celery
import json
import os
from decimal import Decimal, getcontext
from flask import Flask, request, jsonify

# Get Redis URL from environment variables, fallback to localhost
REDIS_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
REDIS_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Initialize Celery
celery_app = Celery('endpoints', broker=REDIS_URL, backend=REDIS_BACKEND)

# Initialize Flask
flask_app = Flask(__name__)

# Calculate pi to n decimal places using the Leibniz formula with progress tracking
@celery_app.task(bind=True)
def calculate_pi(self, n):
    getcontext().prec = n + 50  # Extra precision for intermediate calculations
    
    self.update_state(state='PROGRESS', meta={'progress': 0.0, 'result': None})
    total_terms = max(10000000, n * 10000)  # More terms for higher precision
    pi_over_4 = Decimal(0)
    
    update_frequency = max(1, total_terms // 100)
    
    for k in range(total_terms):
        term = Decimal((-1) ** k) / Decimal(2 * k + 1)
        pi_over_4 += term

        if k % update_frequency == 0:
            progress = k / total_terms
            self.update_state(
                state='PROGRESS',
                meta={'progress': progress, 'result': None}
            )
    
    pi_value = pi_over_4 * 4
    
    format_string = f"{{:.{n}f}}"
    result = format_string.format(pi_value)
    
    self.update_state(state='FINISHED', meta=result)

    return result

# Flask Routes
@flask_app.route('/calculate_pi')
def calculate_pi_endpoint():
    """Flask endpoint to start pi calculation"""
    n = request.args.get('n', type=int)
    
    if n is None:
        return jsonify({'error': 'Please provide a valid integer for n parameter'}), 400
    
    if n < 0:
        return jsonify({'error': 'n must be a non-negative integer'}), 400
    
    if n > 1000:  # Reduced from 10000 for reasonable response times
        return jsonify({'error': 'Maximum decimal places is 1000'}), 400
    
    # Start the Celery task
    task = calculate_pi.delay(n)
    
    return jsonify({
        'task_id': task.id,
        'message': f'Started calculating pi to {n} decimal places',
        'status': 'started',
        'check_progress_url': f'http://localhost:5000/check_progress?task_id={task.id}'
    })

@flask_app.route('/check_progress')
def check_progress_endpoint():
    """Flask endpoint to check calculation progress"""
    task_id = request.args.get('task_id')
    
    if not task_id:
        return jsonify({'error': 'Please provide task_id parameter'}), 400
    
    # Get task result
    task = celery_app.AsyncResult(task_id)
    
    print(f"Task state: {task.state}, Task info: {task.info}")
    
    if task.state == 'PROGRESS':
        progress_info = task.info or {}
        response = {
            'state': 'PROGRESS',
            'progress': progress_info.get('progress', 0.0),
            'result': None
        }
    elif task.state == 'FINISHED' or task.state == 'SUCCESS':
        progress_info = task.info or {}
        response = {
              'state': 'FINISHED',
              'progress': 1.0,
              'result': task.info
        }
    elif task.state == 'FAILURE':
        # Task failed
        response = {
            'state': 'FAILED',
            'progress': 0.0,
            'result': None,
            'error': str(task.info)
        }
    else:
        print(f"Unhandled task state: {task.state}")
        response = {
            'state': 'PROGRESS',
            'progress': 0.0,
            'result': None
        }
    
    return jsonify(response)

@flask_app.route('/')
def home():

    return jsonify({
        'message': 'Pi Calculator API',
        'endpoints': {
            'calculate_pi': {
                'url': '/calculate_pi?n=<decimal_places>',
                'method': 'GET',
                'description': 'Start calculating pi to n decimal places',
                'example': '/calculate_pi?n=10'
            },
            'check_progress': {
                'url': '/check_progress?task_id=<task_id>',
                'method': 'GET', 
                'description': 'Check progress of calculation task',
                'example': '/check_progress?task_id=abc-123-def'
            }
        }
    })

if __name__ == '__main__':
    flask_app.run(debug=True, host='0.0.0.0', port=5000)