import sqlite3
from dataclasses import dataclass
from typing import Optional, List
from utils.logger import setup_logger

logger = setup_logger()

@dataclass
class Record:
    """Data class to represent a transaction record."""
    id: Optional[int] = None
    amount: float = 0.0
    type: str = "expense"  # "income" or "expense"
    category: str = ""
    date: str = ""
    user_id: str = ""

class RecordModel:
    def __init__(self, db_path: str = "moneytracker.db"):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        """Create the transactions table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    user_id TEXT NOT NULL
                );
            """)
            conn.commit()

    def add_record(self, record: Record) -> int:
        """Add a new transaction record to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (amount, type, category, date, user_id)
                VALUES (:amount, :type, :category, :date, :user_id)
            """, {
                "amount": record.amount,
                "type": record.type,
                "category": record.category,
                "date": record.date,
                "user_id": record.user_id
            })
            conn.commit()
            new_id = cursor.lastrowid
            logger.info(f"Added new record with ID={new_id}")
            return new_id

    def get_record(self, record_id: int, user_id: str) -> Optional[Record]:
        """Retrieve a single record by ID and user ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, amount, type, category, date, user_id
                FROM transactions
                WHERE id = :id AND user_id = :user_id
            """, {"id": record_id, "user_id": user_id})
            row = cursor.fetchone()
            if row:
                return Record(*row)
            else:
                return None

    def get_all_records(self, user_id: str, start_date: str = None, end_date: str = None) -> List[Record]:
        """Retrieve all records for a user, optionally filtered by date range."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT id, amount, type, category, date, user_id
                FROM transactions
                WHERE user_id = :user_id
            """
            params = {"user_id": user_id}

            if start_date:
                query += " AND date >= :start_date"
                params["start_date"] = start_date
            if end_date:
                query += " AND date <= :end_date"
                params["end_date"] = end_date

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [Record(*row) for row in rows]

    def delete_record(self, record_id: int, user_id: str) -> bool:
        """Delete a record by ID and user ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM transactions
                WHERE id = :id AND user_id = :user_id
            """, {"id": record_id, "user_id": user_id})
            conn.commit()
            return cursor.rowcount > 0
        
    # --- The following methods are for compatibility with test calls ---

    def create(self, record: Record) -> int:
        """For testing compatibility: same as add_record"""
        return self.add_record(record)

    def read(self, record_id: int, user_id: str) -> Optional[Record]:
        """For testing compatibility: same as get_record"""
        return self.get_record(record_id, user_id)

    def read_all(self, user_id: str, start_date: str = None, end_date: str = None) -> List[Record]:
        """For testing compatibility: same as get_all_records"""
        return self.get_all_records(user_id, start_date, end_date)

    def delete(self, record_id: int, user_id: str) -> bool:
        """For testing compatibility: same as delete_record"""
        return self.delete_record(record_id, user_id)

    def update(self, record_id: int, record: Record, user_id: str) -> bool:
        """For testing compatibility: updates a record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions
                SET amount = :amount, type = :type, category = :category, date = :date
                WHERE id = :id AND user_id = :user_id
            """, {
                "amount": record.amount,
                "type": record.type,
                "category": record.category,
                "date": record.date,
                "id": record_id,
                "user_id": user_id
            })
            conn.commit()
            return cursor.rowcount > 0

