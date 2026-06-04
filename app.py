from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from models import db, Category, Transaction
from datetime import datetime, timedelta
import csv
import io
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-finance'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()
    # Populate default categories if empty
    if not Category.query.first():
        default_categories = [
            ('Food', 'expense'), ('Rent', 'expense'), ('Transport', 'expense'),
            ('Salary', 'income'), ('Entertainment', 'expense'), ('Health', 'expense'),
            ('Other', 'expense')
        ]
        for name, type_ in default_categories:
            cat = Category(name=name, type=type_, is_default=True)
            db.session.add(cat)
        db.session.commit()

@app.route('/')
def dashboard():
    # Calculate current month stats
    today = datetime.today()
    start_of_month = today.replace(day=1)
    
    transactions = Transaction.query.filter(Transaction.date >= start_of_month.strftime('%Y-%m-%d')).all()
    
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    net_balance = total_income - total_expense
    
    # Expense by category for pie chart
    expenses = [t for t in transactions if t.type == 'expense']
    expense_by_cat = {}
    for exp in expenses:
        cat_name = exp.category.name if exp.category else 'Unknown'
        expense_by_cat[cat_name] = expense_by_cat.get(cat_name, 0) + exp.amount
        
    # Calculate 6-month history for bar chart
    six_months_data = {'labels': [], 'income': [], 'expense': []}
    for i in range(5, -1, -1):
        # Rough calculation for months
        month_date = today - timedelta(days=30*i)
        month_str = month_date.strftime('%Y-%m')
        six_months_data['labels'].append(month_date.strftime('%b %Y'))
        
        m_tx = Transaction.query.filter(Transaction.date.startswith(month_str)).all()
        six_months_data['income'].append(sum(t.amount for t in m_tx if t.type == 'income'))
        six_months_data['expense'].append(sum(t.amount for t in m_tx if t.type == 'expense'))
        
    return render_template('dashboard.html', 
                           total_income=total_income, 
                           total_expense=total_expense, 
                           net_balance=net_balance,
                           expense_by_cat=expense_by_cat,
                           six_months_data=six_months_data)

@app.route('/transactions', methods=['GET', 'POST'])
def manage_transactions():
    if request.method == 'POST':
        amount = request.form.get('amount')
        date = request.form.get('date')
        category_id = request.form.get('category_id')
        type_ = request.form.get('type')
        note = request.form.get('note')
        
        try:
            amount = float(amount)
            if amount < 0:
                raise ValueError("Amount cannot be negative")
            
            new_tx = Transaction(amount=amount, date=date, category_id=category_id, type=type_, note=note)
            db.session.add(new_tx)
            db.session.commit()
            flash('Transaction added successfully!', 'success')
        except ValueError as e:
            flash(f'Invalid input: {e}', 'danger')
            
        return redirect(url_for('manage_transactions'))
        
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    categories = Category.query.all()
    return render_template('transactions.html', transactions=transactions, categories=categories)

@app.route('/transactions/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    tx = Transaction.query.get_or_404(id)
    db.session.delete(tx)
    db.session.commit()
    flash('Transaction deleted.', 'success')
    return redirect(url_for('manage_transactions'))

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        type_ = request.form.get('type')
        budget_limit = request.form.get('budget_limit', type=float)
        
        new_cat = Category(name=name, type=type_, budget_limit=budget_limit, is_default=False)
        db.session.add(new_cat)
        db.session.commit()
        flash('Category created!', 'success')
        return redirect(url_for('manage_categories'))
        
    categories = Category.query.all()
    
    # Calculate current spending per category for budget tracking
    today = datetime.today()
    start_of_month = today.replace(day=1)
    
    for cat in categories:
        if cat.type == 'expense' and cat.budget_limit:
            spending = sum(t.amount for t in cat.transactions if t.date >= start_of_month.strftime('%Y-%m-%d'))
            cat.current_spending = spending
            cat.progress = min((spending / cat.budget_limit) * 100, 100) if cat.budget_limit else 0
        else:
            cat.current_spending = 0
            cat.progress = 0
            
    return render_template('categories.html', categories=categories)

@app.route('/export')
def export_csv():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Date', 'Type', 'Category', 'Amount', 'Note'])
    
    for tx in transactions:
        cat_name = tx.category.name if tx.category else 'N/A'
        cw.writerow([tx.date, tx.type, cat_name, tx.amount, tx.note])
        
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='transactions.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)
