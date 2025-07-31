import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import sqlite3
from models.transaction import Transaction
from datetime import datetime
from models.record import RecordModel 

@pytest.fixture
def db():
    model = RecordModel("test.db")
    with sqlite3.connect(model.db_path) as conn:
        conn.execute("DELETE FROM transactions")
        conn.commit()
    return model



@pytest.fixture
def sample_transaction():
    """Create a sample transaction for testing."""
    return Transaction(
        amount=100.50,
        type="expense",
        category="Food",
        date=datetime.now().strftime("%Y-%m-%d"),
        user_id="user1"
    )

def test_create_transaction(db, sample_transaction):
    """Test creating a transaction."""
    transaction_id = db.create(sample_transaction)
    assert transaction_id is not None
    assert isinstance(transaction_id, int)
    
    # Verify the transaction was inserted
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        result = cursor.fetchone()
        assert result is not None
        assert result[1] == sample_transaction.amount
        assert result[2] == sample_transaction.type
        assert result[3] == sample_transaction.category
        assert result[4] == sample_transaction.date
        assert result[5] == sample_transaction.user_id

def test_read_transaction(db, sample_transaction):
    """Test reading a transaction by ID."""
    transaction_id = db.create(sample_transaction)
    retrieved = db.read(transaction_id, sample_transaction.user_id)
    assert retrieved is not None
    assert retrieved.id == transaction_id
    assert retrieved.amount == sample_transaction.amount
    assert retrieved.type == sample_transaction.type
    assert retrieved.category == sample_transaction.category
    assert retrieved.date == sample_transaction.date
    assert retrieved.user_id == sample_transaction.user_id

def test_read_nonexistent_transaction(db):
    """Test reading a nonexistent transaction."""
    retrieved = db.read(999, "user1")
    assert retrieved is None

def test_read_all_transactions(db, sample_transaction):
    """Test reading all transactions for a user."""
    # Create multiple transactions
    db.create(sample_transaction)
    second_transaction = Transaction(
        amount=200.75,
        type="income",
        category="Salary",
        date=datetime.now().strftime("%Y-%m-%d"),
        user_id="user1"
    )
    db.create(second_transaction)
    
    transactions = db.read_all("user1")
    assert len(transactions) == 2
    assert any(t.amount == sample_transaction.amount for t in transactions)
    assert any(t.amount == second_transaction.amount for t in transactions)

def test_read_all_with_date_range(db, sample_transaction):
    """Test reading transactions within a date range."""
    db.create(sample_transaction)
    transactions = db.read_all(
        user_id="user1",
        start_date=sample_transaction.date,
        end_date=sample_transaction.date
    )
    assert len(transactions) == 1
    assert transactions[0].amount == sample_transaction.amount

def test_update_transaction(db, sample_transaction):
    """Test updating a transaction."""
    transaction_id = db.create(sample_transaction)
    updated_transaction = Transaction(
        id=transaction_id,
        amount=150.25,
        type="income",
        category="Gift",
        date=sample_transaction.date,
        user_id=sample_transaction.user_id
    )
    success = db.update(
    record_id=transaction_id,
    record=updated_transaction,
    user_id=updated_transaction.user_id
    )

    assert success
    
    retrieved = db.read(transaction_id, sample_transaction.user_id)
    assert retrieved.amount == updated_transaction.amount
    assert retrieved.type == updated_transaction.type
    assert retrieved.category == updated_transaction.category

def test_delete_transaction(db, sample_transaction):
    """Test deleting a transaction."""
    transaction_id = db.create(sample_transaction)
    success = db.delete(transaction_id, sample_transaction.user_id)
    assert success
    
    retrieved = db.read(transaction_id, sample_transaction.user_id)
    assert retrieved is None

def test_delete_nonexistent_transaction(db):
    """Test deleting a nonexistent transaction."""
    success = db.delete(999, "user1")
    assert not success