from flask import jsonify, request, render_template, send_file
from app import app, db
from models import Task
import numpy as np
import os

REPORT_DIR = 'reports'  # Directory where reports will be saved

@app.route('/submit_task', methods=['POST'])
def submit_task():
    matrix_size = request.json['matrix_size']
    task = Task(matrix_size=matrix_size, status='pending')
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Task added', 'task_id': task.id}), 200

@app.route('/process_tasks', methods=['POST'])
def process_tasks():
    task = Task.query.filter_by(status='pending').first()
    if task:
        task.status = 'in_progress'
        db.session.commit()

        # Perform the matrix calculation directly
        matrix_size = task.matrix_size
        result = calculate_matrix(matrix_size)

        # Update task status and result
        task.status = 'completed'
        task.result = result  # Assuming you have a result field in your Task model
        
        # Generate report and save to file
        report_path = generate_report(task.id, result)
        task.report_path = report_path
        db.session.commit()

        return jsonify({'message': 'Task has been processed', 'result': result}), 200

    return jsonify({'message': 'No pending tasks'}), 200

def calculate_matrix(size):
    # Example calculation (replace with actual logic)
    matrix = np.random.rand(size, size)
    return matrix.tolist()

def generate_report(task_id, result):
    # Generate a report (e.g., save to a text file or create a CSV)
    report_path = os.path.join(REPORT_DIR, f'report_{task_id}.txt')
    with open(report_path, 'w') as f:
        f.write('Task ID: {}\n'.format(task_id))
        f.write('Result:\n')
        for row in result:
            f.write(', '.join(map(str, row)) + '\n')
    return report_path

@app.route('/download_report/<int:task_id>', methods=['GET'])
def download_report(task_id):
    task = Task.query.get(task_id)
    if task and task.report_path and os.path.exists(task.report_path):
        return send_file(task.report_path, as_attachment=True)
    return jsonify({'message': 'Report not found'}), 404

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)
