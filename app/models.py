from app import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matrix_size = db.Column(db.Integer)
    status = db.Column(db.String(50), default='pending')
    progress = db.Column(db.Integer, default=0)
    report_path = db.Column(db.String(150))
