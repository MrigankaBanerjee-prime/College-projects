
import sqlite3
from pathlib import Path

# Database location
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_NAME = DATA_DIR / "expenses.db"


# Connect to database
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# Create database tables
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            expense_date TEXT NOT NULL,
            payment_method TEXT,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            month TEXT PRIMARY KEY,
            amount REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Add a new expense
def add_expense(title, amount, category, expense_date,
                payment_method="", description=""):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses
        (title, amount, category, expense_date,
         payment_method, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, amount, category, expense_date,
          payment_method, description))

    conn.commit()
    conn.close()


# Get all expenses
def get_expenses():
    conn = connect_db()

    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM expenses
        ORDER BY expense_date DESC, id DESC
    """)

    records = cursor.fetchall()
    conn.close()

    return records


# Delete an expense
def delete_expense(expense_id):
    conn = connect_db()

    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()


# Update an existing expense
def update_expense(expense_id, title, amount, category,
                   expense_date, payment_method, description):

    conn = connect_db()

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE expenses
        SET title=?, amount=?, category=?,
            expense_date=?, payment_method=?, description=?
        WHERE id=?
    """, (title, amount, category, expense_date,
          payment_method, description, expense_id))

    conn.commit()
    conn.close()


# Calculate total expenses
def get_total_expenses():
    conn = connect_db()

    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")

    result = cursor.fetchone()[0]
    conn.close()

    return result if result is not None else 0


# Save monthly budget
def set_budget(month, amount):
    conn = connect_db()

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (month, amount)
        VALUES (?, ?)
        ON CONFLICT(month)
        DO UPDATE SET amount=excluded.amount
    """, (month, amount))

    conn.commit()
    conn.close()


# Get monthly budget
def get_budget(month):
    conn = connect_db()

    cursor = conn.cursor()
    cursor.execute(
        "SELECT amount FROM budgets WHERE month=?",
        (month,)
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else 0


# Calculate monthly expenses
def get_monthly_expenses(month):
    conn = connect_db()

    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE substr(expense_date, 1, 7) = ?
    """, (month,))

    result = cursor.fetchone()[0]
    conn.close()

    return result if result is not None else 0
