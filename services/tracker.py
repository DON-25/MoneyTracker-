from typing import List, Optional, Dict
from models.transaction import Transaction, TransactionModel
from utils.logger import setup_logger
from datetime import datetime

logger = setup_logger()

class TrackerService:
    """Service layer for handling business logic related to transactions."""
    def __init__(self, db_name: str = "moneytracker.db"):
        self.db = TransactionModel(db_name)

    def add_transaction(self, amount: float, type: str, category: str, date: str, user_id: str) -> int:
        """Add a new transaction and return its ID."""
        try:
            # Validate inputs
            if amount <= 0:
                raise ValueError("Amount must be positive")
            if type not in ['income', 'expense']:
                raise ValueError("Type must be 'income' or 'expense'")
            if not category:
                raise ValueError("Category cannot be empty")
            datetime.strptime(date, '%Y-%m-%d')  # Validate date format

            transaction = Transaction(
                amount=amount,
                type=type,
                category=category,
                date=date,
                user_id=user_id
            )
            transaction_id = self.db.create(transaction)
            logger.info(f"TrackerService: Added transaction ID {transaction_id} for user {user_id}")
            return transaction_id
        except ValueError as e:
            logger.error(f"TrackerService: Failed to add transaction - {e}")
            raise
        except Exception as e:
            logger.error(f"TrackerService: Unexpected error adding transaction - {e}")
            raise

    def list_transactions(self, user_id: str, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> List[Transaction]:
        """Retrieve transactions for a user, optionally filtered by date range."""
        try:
            # Validate date formats if provided
            if start_date:
                datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                datetime.strptime(end_date, '%Y-%m-%d')
                
            transactions = self.db.read_all(user_id, start_date, end_date)
            logger.info(f"TrackerService: Retrieved {len(transactions)} transactions for user {user_id}")
            return transactions
        except ValueError as e:
            logger.error(f"TrackerService: Failed to list transactions - Invalid date format: {e}")
            raise
        except Exception as e:
            logger.error(f"TrackerService: Unexpected error listing transactions - {e}")
            raise

    def get_summary(self, user_id: str, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None) -> Dict:
        """Generate summary statistics for a user's transactions."""
        try:
            # Validate date formats if provided
            if start_date:
                datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                datetime.strptime(end_date, '%Y-%m-%d')

            transactions = self.db.read_all(user_id, start_date, end_date)
            total_income = sum(t.amount for t in transactions if t.type == 'income')
            total_expense = sum(t.amount for t in transactions if t.type == 'expense')
            balance = total_income - total_expense
            category_summary = {}
            for t in transactions:
                category_summary[t.category] = category_summary.get(t.category, 0) + t.amount

            summary = {
                'total_income': total_income,
                'total_expense': total_expense,
                'balance': balance,
                'category_summary': category_summary,
                'transaction_count': len(transactions)
            }
            logger.info(f"TrackerService: Generated summary for user {user_id}: Income={total_income}, Expense={total_expense}")
            return summary
        except ValueError as e:
            logger.error(f"TrackerService: Failed to generate summary - Invalid date format: {e}")
            raise
        except Exception as e:
            logger.error(f"TrackerService: Unexpected error generating summary - {e}")
            raise