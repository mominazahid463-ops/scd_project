import sqlite3
from datetime import datetime

DB_NAME = 'finance_tk.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            is_default INTEGER DEFAULT 0,
            budget_limit REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "transaction" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            note TEXT,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES category (id)
        )
    ''')
    
    # Insert default categories if empty
    cursor.execute('SELECT COUNT(*) FROM category')
    if cursor.fetchone()[0] == 0:
        default_cats = [
            ('Food', 'expense', 1), ('Rent', 'expense', 1), ('Transport', 'expense', 1),
            ('Salary', 'income', 1), ('Entertainment', 'expense', 1), ('Health', 'expense', 1),
            ('Other', 'expense', 1)
        ]
        cursor.executemany('''
            INSERT INTO category (name, type, is_default)
            VALUES (?, ?, ?)
        ''', default_cats)
        
    conn.commit()
    conn.close()

def get_all_categories():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cats = conn.execute('SELECT * FROM category ORDER BY name').fetchall()
    conn.close()
    return cats

def add_category(name, type_, budget_limit=None):
    conn = get_connection()
    conn.execute('''
        INSERT INTO category (name, type, is_default, budget_limit)
        VALUES (?, ?, 0, ?)
    ''', (name, type_, budget_limit))
    conn.commit()
    conn.close()

def delete_category(cat_id):
    conn = get_connection()
    conn.execute('DELETE FROM category WHERE id = ?', (cat_id,))
    conn.commit()
    conn.close()

def add_transaction(amount, date, type_, category_id, note):
    conn = get_connection()
    conn.execute('''
        INSERT INTO "transaction" (amount, date, type, category_id, note)
        VALUES (?, ?, ?, ?, ?)
    ''', (amount, date, type_, category_id, note))
    conn.commit()
    conn.close()

def update_transaction(tx_id, amount, date, type_, category_id, note):
    conn = get_connection()
    conn.execute('''
        UPDATE "transaction" 
        SET amount=?, date=?, type=?, category_id=?, note=?
        WHERE id=?
    ''', (amount, date, type_, category_id, note, tx_id))
    conn.commit()
    conn.close()

def delete_transaction(tx_id):
    conn = get_connection()
    conn.execute('DELETE FROM "transaction" WHERE id = ?', (tx_id,))
    conn.commit()
    conn.close()

def get_all_transactions():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    txs = conn.execute('''
        SELECT t.id, t.date, c.name as category, t.type, t.amount, t.note, t.category_id
        FROM "transaction" t
        JOIN category c ON t.category_id = c.id
        ORDER BY t.date DESC
    ''').fetchall()
    conn.close()
    return txs

def get_monthly_transactions(year, month):
    month_str = f"{year}-{month:02d}"
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    txs = conn.execute('''
        SELECT * FROM "transaction"
        WHERE date LIKE ?
    ''', (f'{month_str}%',)).fetchall()
    conn.close()
    return txs
