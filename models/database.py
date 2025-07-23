import sqlite3
import os

def init_database(db_name='moneytracker.db'):
    """Initialize SQLite database with transactions table."""
    # Ensure database directory exists
    db_dir = os.path.dirname(db_name)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # Connect to SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create transactions table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            user_id TEXT NOT NULL
        )
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()

    if __name__ == "__main__":
        init_database()
