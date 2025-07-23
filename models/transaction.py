import sqlite3                     
from dataclasses import dataclass  
from datetime import datetime      
from typing import List, Optional  
from utils.logger import setup_logger  

logger = setup_logger()
@dataclass
class Transaction:
    """Data class for a financial transaction."""
    id: Optional[int] = None
    amount: float = 0.0
    type: str = 'expense'
    category: str = ""
    date: str = ""
    user_id: str = ""

class TransactionModel:
    """Model for handling transaction CRUD operations with SQLite."""
    def __init__(self, db_name: str = "moneytracker.db"):
        self.db_name = db_name
        self._ensure_table()

    def _ensure_table(self):
        """Ensure the transactions table exists."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        amount REAL NOT NULL,
                        type TEXT NOT NULL,
                        category TEXT NOT NULL,
                        date TEXT NOT NULL,
                        user_id TEXT NOT NULL
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Error ensuring transactions table: {e}")
        except sqlite3.Error as e:
                logger.error(f"Error creating table: {e}")
                raise
        
    def add_transaction(self, transaction: Transaction) -> int:
         """Create a new transaction and return its ID."""
         try:
                with sqlite3.connect(self.db_name) as conn:
                        cursor= conn.cursor()
                        cursor.execute("""
                            INSERT INTO transactions (amount, type, category, date, user_id)
                            VALUES (?, ?, ?, ?, ?)
                            """, (transaction.amount, transaction.type, transaction.category, transaction.date, transaction.user_id))
                        conn.commit()
                        transaction.id = cursor.lastrowid
                        logger.info(f"Transaction added with ID: {transaction.id}")
                        return transaction.id
         except sqlite3.Error as e:
                logger.error(f"Error adding transaction: {e}")
                raise

    def get_transaction(self, transaction_id: int, user_id: str) -> Optional[Transaction]:
        """Read a transaction by ID for a specific user."""
        try:
             with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                   SELECT id, amount, type, category, date, user_id
                   FROM transactions WHERE id = ? AND user_id = ?
                """, (transaction_id, user_id))
                result = cursor.fetchone()
                if result:
                     logger.info(f"Read transaction with ID: {transaction_id}")
                     return Transaction(*result)
                logger.warning(f"No transaction found with ID: {transaction_id} for user: {user_id}")
                return None
        except sqlite3.Error as e:
            logger.error(f"Error reading transaction: {e}")
            raise

    def read_all(self,user_id:str,start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Transaction]:
        """Read all transactions for a specific user, optionally filtered by date range."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = "SELECT id, amount, type, category, date, user_id FROM transactions WHERE user_id = ?"
                params = [user_id]

                if start_date and end_date:
                    query += " AND date BETWEEN ? AND ?"
                    params.extend([start_date, end_date])
                cursor.execute(query, params)
                results = cursor.fetchall()
                transactions = [Transaction(*row) for row in results]
                logger.info(f"Read {len(transactions)} transactions for user: {user_id}")
                return transactions
        except sqlite3.Error as e:
            logger.error(f"Error reading transactions: {e}")
            raise

    def update(self, transaction: Transaction) -> bool:
        """Update an existing transaction."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE transactions
                    SET amount = ?, type = ?, category = ?, date = ?, user_id = ?
                    WHERE id = ?
                """, (transaction.amount, transaction.type, transaction.category,
                      transaction.date, transaction.user_id, transaction.id))
                conn.commit()
                if cursor.rowcount > 0:
                    logger.info(f"Updated transaction with ID {transaction.id}")
                    return True
                logger.warning(f"No transaction found with ID {transaction.id}")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error updating transaction: {e}")
            raise    

    def delete(self, transaction_id: int, user_id: str) -> bool:
        """Delete a transaction by ID for a specific user."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?",
                              (transaction_id, user_id))
                conn.commit()
                if cursor.rowcount > 0:
                    logger.info(f"Deleted transaction with ID {transaction_id}")
                    return True
                logger.warning(f"No transaction found with ID {transaction_id} for user {user_id}")
                return False
        except sqlite3.Error as e:
            logger.error(f"Error deleting transaction: {e}")
            raise
            


                  
