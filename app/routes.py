from flask import jsonify, request, render_template, send_file
from app import app, db
from models import Task
import numpy as np
import os
import time

REPORT_DIR = 'reports'  # Directory where reports will be saved


@app.route('/submit_task', methods=['POST'])
def submit_task():
    matrix_size = request.json['matrix_size']
    task = Task(matrix_size=matrix_size, status='pending')
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Task added', 'task_id': task.id}), 200

@app.route('/process_task/<int:task_id>', methods=['POST'])
def process_task(task_id):
    task = Task.query.get(task_id)
    if task and task.status == 'pending':
        task.status = 'in_progress'
        db.session.commit()

        # Perform the matrix calculation
        matrix_size = task.matrix_size
        result = calculate_matrix(matrix_size, task.id)

        # Update task status and result
        task.status = 'completed'
        task.result = result  # Assuming you have a result field in your Task model
        
        # Generate report and save to file
        report_path = generate_report(task.id, result)
        task.report_path = report_path
        db.session.commit()

        return jsonify({'message': 'Task has been processed', 'result': result}), 200

    return jsonify({'message': 'Task not found or already processed'}), 404

@app.route('/get_progress/<int:task_id>', methods=['GET'])
def get_progress_endpoint(task_id):
    task = Task.query.get(task_id)
    if task:
        return jsonify({'progress': task.progress}), 200
    return jsonify({'progress': 0}), 404  # Return 0 if task not found


def calculate_matrix(size, task_id):
    task = Task.query.get(task_id)
    if not task:
        return None

    # Generate two random matrices
    matrix_a = np.random.rand(size, size)
    matrix_b = np.random.rand(size, size)

    # Perform matrix multiplication with progress tracking
    result = np.zeros((size, size))
    total_operations = size * size * size  # Total number of operations (i * j * k)
    completed_operations = 0

    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]
                completed_operations += 1
            # Update progress after every 5% of operations
            if size > 20 and completed_operations % (total_operations // 20) == 0:
                task.progress = (completed_operations / total_operations) * 100
                db.session.commit()  # Save progress to the database

    task.progress = 100  # Mark task as complete
    db.session.commit()
    print(f"Task {task_id} completed.")
    return result.tolist()


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

@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'}), 200
    return jsonify({'message': 'Task not found'}), 404

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)
