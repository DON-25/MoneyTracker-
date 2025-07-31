import click
from views.chart import plot_category_spending
from views.report import display_tabular_summary
from utils.pdf_exporter import export_summary_to_pdf
# Chart visualization command
@click.command()
@click.option('--user-id', type=str, required=True, help='User ID')
@click.option('--start-date', type=str, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', type=str, help='End date (YYYY-MM-DD)')
def plot(user_id, start_date=None, end_date=None):
    """Show category-wise spending chart for a user."""
    plot_category_spending(user_id, start_date, end_date)

# Tabular report command
@click.command()
@click.option('--user-id', type=str, required=True, help='User ID')
@click.option('--start-date', type=str, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', type=str, help='End date (YYYY-MM-DD)')
@click.option('--month', type=str, help='Specify month (e.g. 2025-07), takes precedence over start/end-date')
def report(user_id, start_date=None, end_date=None, month=None):
    """Show tabular summary report for a user."""
    # Month option logic (same as summary)
    if month:
        import re
        if not re.match(r'^\d{4}-\d{2}$', month):
            click.echo('Invalid month format, should be YYYY-MM')
            return
        start_date = f"{month}-01"
        from calendar import monthrange
        last_day = monthrange(int(month[:4]), int(month[5:]))[1]
        end_date = f"{month}-{last_day:02d}"
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        if end_date > today:
            end_date = today
    display_tabular_summary(user_id, start_date, end_date)

# PDF report export command
@click.command()
@click.option('--user-id', type=str, required=True, help='User ID')
@click.option('--start-date', type=str, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', type=str, help='End date (YYYY-MM-DD)')
@click.option('--output', type=str, default=None, help='Output PDF file path')
def report_pdf(user_id, start_date=None, end_date=None, output=None):
    """Export summary report as PDF for a user."""
    try:
        db = get_db()
        # Validate user and dates
        validate_user_id(user_id)
        if start_date:
            validate_date(start_date)
        if end_date:
            validate_date(end_date)
        if start_date and end_date:
            validate_date_range(start_date, end_date)
        transactions = db.read_all(user_id, start_date, end_date)
        if not transactions:
            click.echo(f"No transactions found for user {user_id}")
            return
        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expense = sum(t.amount for t in transactions if t.type == 'expense')
        balance = total_income - total_expense
        category_summary = {}
        for t in transactions:
            category_summary[t.category] = category_summary.get(t.category, 0) + t.amount
        summary_data = {
            'transaction_count': len(transactions),
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'category_summary': category_summary
        }
        pdf_path = export_summary_to_pdf(summary_data, output)
        click.echo(f"PDF report exported to: {pdf_path}")
    except Exception as e:
        click.echo(str(e), err=True)
        raise click.ClickException(str(e))
import click
from datetime import datetime
from models.transaction import TransactionModel, Transaction
from utils.logger import setup_logger
from models.record import RecordModel
from utils.validators import (
    validate_amount, validate_user_id,
    validate_category, validate_date,
    validate_date_range,ValidationError
)

import os
logger = setup_logger()


def get_db():
    db_path = os.getenv("MONEYTRACKER_DB", "moneytracker.db")
    return TransactionModel(db_name=db_path)
     
@click.command()
@click.option('--amount', type=float, required=True, help='Transaction amount')
@click.option('--type', type=click.Choice(['income', 'expense']), required=True, help='Transaction type')
@click.option('--category', type=str, required=True, help='Transaction category')
@click.option('--date', type=str, default=datetime.now().strftime('%Y-%m-%d'), help='Transaction date (YYYY-MM-DD)')
@click.option('--user-id', type=str, default='default_user', help='User ID')
def add(amount, type, category, date, user_id):
    """Add a new income or expense transaction."""
    try:
        db = get_db()

        # Validate date format
        validate_amount(amount)
        validate_user_id(user_id)
        validate_category(category)
        validate_date(date)

        transaction = Transaction(
            amount=amount,
            type=type,
            category=category,
            date=date,
            user_id=user_id
        )
        transaction_id = db.create(transaction)
        click.echo(f"Transaction added successfully with ID {transaction_id}")
        logger.info(f"Added transaction: {amount} {type} in {category} for user {user_id}")


    except ValidationError as e:
        click.echo(f"Error: {e}")
        logger.error(f"Failed to add transaction: {e}")
    except Exception as e:
        click.echo(f"Error: {e}")
        logger.error(f"Failed to add transaction: {e}")

@click.command()
@click.option('--user-id', type=str, default='default_user', help='User ID')
@click.option('--start-date', type=str, help='Start date for filtering (YYYY-MM-DD)')
@click.option('--end-date', type=str, help='End date for filtering (YYYY-MM-DD)')
def list(user_id, start_date, end_date):
    """List transactions for a user, optionally filtered by date range."""
    try:
        db = get_db()

        # Validate date formats if provided
        validate_user_id(user_id)
        if start_date:
            validate_date(start_date)
        if end_date:
            validate_date(end_date)
        if start_date and end_date:
            validate_date_range(start_date, end_date)    
        
        transactions = db.read_all(user_id, start_date, end_date)
        if not transactions:
            click.echo(f"No transactions found for user {user_id}")
            logger.info(f"No transactions found for user {user_id}")
            return

        click.echo(f"\nTransactions for user {user_id}:")
        click.echo("-" * 50)
        for idx, t in enumerate(transactions, start=1):
            click.echo(f"ID: {idx}, Amount: {t.amount:.2f}, Type: {t.type}, "
                      f"Category: {t.category}, Date: {t.date}")
        click.echo("-" * 50)
        logger.info(f"Listed {len(transactions)} transactions for user {user_id}")
    except ValueError as e:
        click.echo(f"Error: {e}")
        logger.error(f"Failed to list transactions: {e}")
    except Exception as e:
        click.echo(f"Error: {e}")
        logger.error(f"Failed to list transactions: {e}")

@click.command()
@click.option('--user-id', type=str, default='default_user', help='User ID')
@click.option('--start-date', type=str, help='Start date for summary (YYYY-MM-DD)')
@click.option('--end-date', type=str, help='End date for summary (YYYY-MM-DD)')
@click.option('--month', type=str, help='Specify month (e.g. 2025-07), takes precedence over start/end-date')
def summary(user_id, start_date, end_date, month):
    """Display basic statistics for a user's transactions."""
    try:
        db = get_db()

        # Validate date formats if provided
        validate_user_id(user_id)
        if month:
            # Month format validation
            import re
            if not re.match(r'^\d{4}-\d{2}$', month):
                click.echo('Invalid month format, should be YYYY-MM')
                return
            start_date = f"{month}-01"
            from calendar import monthrange
            # Get last day of the month
            last_day = monthrange(int(month[:4]), int(month[5:]))[1]
            end_date = f"{month}-{last_day:02d}"
            # If end_date is in the future, set to today
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            if end_date > today:
                end_date = today
        if start_date:
            validate_date(start_date)
        if end_date:
            validate_date(end_date)
        if start_date and end_date:
            validate_date_range(start_date, end_date)

        transactions = db.read_all(user_id, start_date, end_date)
        if not transactions:
            click.echo(f"No transactions found for user {user_id}")
            logger.info(f"No transactions found for summary for user {user_id}")
            return

        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expense = sum(t.amount for t in transactions if t.type == 'expense')
        balance = total_income - total_expense
        category_summary = {}
        for t in transactions:
            category_summary[t.category] = category_summary.get(t.category, 0) + t.amount

        click.echo(f"\nSummary for user {user_id}:")
        click.echo("-" * 50)
        click.echo(f"Total Income: {total_income:.2f}")
        click.echo(f"Total Expense: {total_expense:.2f}")
        click.echo(f"Balance: {balance:.2f}")
        click.echo("\nCategory Breakdown:")
        for category, amount in category_summary.items():
            click.echo(f"{category}: {amount:.2f}")
        click.echo("-" * 50)
        logger.info(f"Generated summary for user {user_id}: Income={total_income}, Expense={total_expense}")
    except ValueError as e:
        click.echo(f"Error: {e}")
        logger.error(f"Failed to generate summary: {e}")
    except Exception as e:
        click.echo(f"Error: {e}")
        logger.error(f"Failed to generate summary: {e}")
    except ValidationError as e:
        click.echo(f"Error: {e}")
        logger.error(f"Failed to generate summary: {e}")


    db_path = os.getenv("MONEYTRACKER_DB", "moneytracker.db")
    return TransactionModel(db_name=db_path)
     