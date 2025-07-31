import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import sqlite3
from click.testing import CliRunner
from cli.commands import add, list as list_command, summary
from models.transaction import TransactionModel, Transaction
from datetime import datetime, timedelta

@pytest.fixture
def runner():
    """Create a Click CLI runner for testing."""
    return CliRunner()

@pytest.fixture
def db(tmp_path):
    """Create a temporary SQLite database for testing."""
    db_path = tmp_path / "test_moneytracker.db"
    model = TransactionModel(db_name=str(db_path))
    model.initialize()
    yield model
    # Cleanup is handled by tmp_path fixture

def test_add_command_valid_input(runner, db):
    """Test the 'add' command with valid input."""
    result = runner.invoke(add, [
        '--amount', '100.50',
        '--type', 'expense',
        '--category', 'Food',
        '--date', '2025-07-24',
        '--user-id', 'test_user'
    ],env={'MONEYTRACKER_DB': db.db_name})

    assert result.exit_code == 0
    assert "Transaction added successfully with ID" in result.output
    
    # Verify the transaction was added to the database
    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE user_id = ?", ('test_user',))
        transaction = cursor.fetchone()
        assert transaction is not None
        assert transaction[1] == 100.50
        assert transaction[2] == 'expense'
        assert transaction[3] == 'Food'
        assert transaction[4] == '2025-07-24'
        assert transaction[5] == 'test_user'

def test_add_command_invalid_amount(runner, db):
    """Test the 'add' command with invalid (negative) amount."""
    result = runner.invoke(add, [
        '--amount', '-10',
        '--type', 'expense',
        '--category', 'Food',
        '--date', '2025-07-24',
        '--user-id', 'test_user'
    ], env={'MONEYTRACKER_DB': db.db_name})
    assert result.exit_code == 0
    assert "Error: Amount must be a positive number" in result.output

def test_add_command_invalid_date(runner, db):
    """Test the 'add' command with invalid date format."""
    result = runner.invoke(add, [
        '--amount', '100',
        '--type', 'income',
        '--category', 'Salary',
        '--date', '2025-13-01',  # Invalid month
        '--user-id', 'test_user'
    ], env={'MONEYTRACKER_DB': db.db_name})
    assert result.exit_code == 0
    assert "Error: Invalid date format. Expected YYYY-MM-DD." in result.output
    print(result.output)

def test_add_command_future_date(runner, db):
    """Test the 'add' command with a future date."""
    future_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    result = runner.invoke(add, [
        '--amount', '100',
        '--type', 'income',
        '--category', 'Salary',
        '--date', future_date,
        '--user-id', 'test_user'
    ], env={'MONEYTRACKER_DB': db.db_name})
    assert result.exit_code == 0
    assert "Error: Date cannot be in the future." in result.output

def test_add_command_empty_category(runner, db):
    """Test the 'add' command with an empty category."""
    result = runner.invoke(add, [
        '--amount', '100',
        '--type', 'expense',
        '--category', '',
        '--date', '2025-07-24',
        '--user-id', 'test_user'
    ], env={'MONEYTRACKER_DB': db.db_name})
    assert result.exit_code == 0
    assert "Error: Category must be between 1 and 20 characters long." in result.output

def test_list_command_no_transactions(runner, db):
    """Test the 'list' command when no transactions exist."""
    result = runner.invoke(list_command, ['--user-id', 'test_user'], env={'MONEYTRACKER_DB': db.db_name})
    assert result.exit_code == 0
    assert "No transactions found for user test_user" in result.output

def test_list_command_with_transactions(runner, db):
    """Test the 'list' command with existing transactions."""
    # Add a sample transaction
    db.create(Transaction(
        amount=100.50,
        type="expense",
        category="Food",
        date="2025-07-24",
        user_id="test_user"
    ))

    result = runner.invoke(list_command, ['--user-id', 'test_user'], env={'MONEYTRACKER_DB': db.db_name})
    assert result.exit_code == 0
    assert "Transactions for user test_user" in result.output
    assert "ID: 1, Amount: 100.50, Type: expense, Category: Food, Date: 2025-07-24" in result.output

def test_list_command_date_range(runner, db):
    """Test the 'list' command with a date range filter."""
    # Add transactions
    db.create(Transaction(
        amount=100.50,
        type="expense",
        category="Food",
        date="2025-07-24",
        user_id="test_user"
    ))
    db.create(Transaction(
        amount=200.00,
        type="income",
        category="Salary",
        date="2025-07-23",
        user_id="test_user"
    ))
    
    result = runner.invoke(list_command, [
        '--user-id', 'test_user',
        '--start-date', '2025-07-24',
        '--end-date', '2025-07-24'
    ], env={'MONEYTRACKER_DB': db.db_name})
    assert result.exit_code == 0
    assert "ID: 1, Amount: 100.50, Type: expense, Category: Food, Date: 2025-07-24" in result.output
    assert "Salary" not in result.output  # Transaction on 2025-07-23 should be filtered out

def test_list_command_invalid_date(runner, db):
    """Test the 'list' command with an invalid date format."""
    result = runner.invoke(list_command, [
        '--user-id', 'test_user',
        '--start-date', '2025-13-01'
    ], env={'MONEYTRACKER_DB': db.db_name})
    assert result.exit_code == 0
    assert "Error: Invalid date format. Expected YYYY-MM-DD." in result.output

def test_summary_command_no_transactions(runner, db):
    """Test the 'summary' command when no transactions exist."""
    result = runner.invoke(summary, ['--user-id', 'test_user'], env={'MONEYTRACKER_DB': db.db_name})
    assert result.exit_code == 0
    assert "No transactions found for user test_user" in result.output

def test_summary_command_with_transactions(runner, db):
    """Test the 'summary' command with existing transactions."""
    # Add transactions
    db.create(Transaction(
        amount=100.50,
        type="expense",
        category="Food",
        date="2025-07-24",
        user_id="test_user"
    ))
    db.create(Transaction(
        amount=200.00,
        type="income",
        category="Salary",
        date="2025-07-24",
        user_id="test_user"
    ))

    result = runner.invoke(summary, ['--user-id', 'test_user'], env={'MONEYTRACKER_DB': db.db_name})
    assert result.exit_code == 0
    assert "Summary for user test_user" in result.output
    assert "Total Income: 200.00" in result.output
    assert "Total Expense: 100.50" in result.output
    assert "Balance: 99.50" in result.output
    assert "Food: 100.50" in result.output
    assert "Salary: 200.00" in result.output

def test_summary_command_invalid_date_range(runner, db):
    """Test the 'summary' command with invalid date range."""
    result = runner.invoke(summary, [
        '--user-id', 'test_user',
        '--start-date', '2025-07-25',
        '--end-date', '2025-07-24'
    ], env={'MONEYTRACKER_DB': db.db_name})
    assert result.exit_code == 0
    assert "Error: Start date cannot be after end date" in result.output