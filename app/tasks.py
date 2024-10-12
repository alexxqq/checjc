from app import db
from models import Task
import time

def execute_task(task_id):
    task = Task.query.get(task_id)
    matrix_size = task.matrix_size
    
    for i in range(matrix_size):
        time.sleep(1)  # Симуляція ітерацій
        task.progress = (i + 1) * 100 // matrix_size
        db.session.commit()

    task.status = 'completed'
    task.report_path = f'reports/report_{task_id}.txt'
    with open(task.report_path, 'w') as f:
        f.write('Floyd-Warshall algorithm results...')
    
    db.session.commit()
