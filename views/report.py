from rich.console import Console
from rich.table import Table
from services.tracker import TrackerService
from utils.logger import setup_logger
from typing import Optional

logger = setup_logger()
console = Console()
tracker = TrackerService()

def display_tabular_summary(user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> None:
    """Display a tabular summary of transactions in the terminal using rich."""
    try:
        # Get summary data from TrackerService
        summary_data = tracker.get_summary(user_id, start_date, end_date)
        if summary_data['transaction_count'] == 0:
            console.print(f"[yellow]No transactions found for user {user_id}[/yellow]")
            logger.info(f"No transactions found for user {user_id} to display in tabular summary")
            return

        # Create summary table
        summary_table = Table(title=f"Summary for User {user_id}", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", justify="right", style="green")
        summary_table.add_row("Total Income", f"{summary_data['total_income']:.2f}")
        summary_table.add_row("Total Expense", f"{summary_data['total_expense']:.2f}")
        summary_table.add_row("Balance", f"{summary_data['balance']:.2f}")
        summary_table.add_row("Transaction Count", str(summary_data['transaction_count']))

        # Create category breakdown table
        category_table = Table(title="Category Breakdown", show_header=True, header_style="bold magenta")
        category_table.add_column("Category", style="cyan")
        category_table.add_column("Amount", justify="right", style="green")
        for category, amount in summary_data['category_summary'].items():
            category_table.add_row(category, f"{amount:.2f}")

        # Display tables
        console.print(summary_table)
        console.print("\n")  # Add spacing between tables
        console.print(category_table)
        logger.info(f"Displayed tabular summary for user {user_id}")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.error(f"Failed to display tabular summary: {e}")
    except Exception as e:
        console.print(f"[red]Error displaying summary: {e}[/red]")
        logger.error(f"Unexpected error displaying tabular summary: {e}")

if __name__ == "__main__":
    # Example usage for testing
    display_tabular_summary("test_user", "2025-07-01", "2025-07-31")