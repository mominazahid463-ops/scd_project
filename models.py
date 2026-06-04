from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False) # 'income' or 'expense'
    is_default = db.Column(db.Boolean, default=False)
    budget_limit = db.Column(db.Float, nullable=True) # Only for expenses
    
    transactions = db.relationship('Transaction', backref='category', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(20), nullable=False, default=datetime.utcnow().strftime('%Y-%m-%d'))
    type = db.Column(db.String(10), nullable=False) # 'income' or 'expense'
    note = db.Column(db.String(200), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
