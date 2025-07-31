__all__ = ["plot_category_spending"]
import matplotlib.pyplot as plt
from services.tracker import TrackerService
from utils.logger import setup_logger
from typing import Optional
from datetime import datetime

logger = setup_logger()
tracker = TrackerService()

def plot_category_spending(user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None, plt_module=None) -> None:
    """Generate a bar chart for category-wise spending using matplotlib."""
    try:
        if plt_module is None:
            import matplotlib.pyplot as plt_module
        # Get summary data from TrackerService
        summary_data = tracker.get_summary(user_id, start_date, end_date)
        if summary_data['transaction_count'] == 0:
            logger.info(f"No transactions found for user {user_id} to plot")
            print(f"No transactions found for user {user_id}")
            return

        # Extract category-wise expenses (filter out income)
        category_expenses = {
            category: amount for category, amount in summary_data['category_summary'].items()
            if any(t.type == 'expense' and t.category == category for t in tracker.list_transactions(user_id, start_date, end_date))
        }

        if not category_expenses:
            logger.info(f"No expense transactions found for user {user_id} to plot")
            print(f"No expense transactions found for user {user_id}")
            return

        # Prepare data for plotting
        categories = list(category_expenses.keys())
        amounts = list(category_expenses.values())

        # Create bar chart
        plt_module.figure(figsize=(10, 6))
        plt_module.bar(categories, amounts, color='skyblue')
        plt_module.xlabel('Category')
        plt_module.ylabel('Amount Spent')
        plt_module.title(f'Category-Wise Spending for User {user_id}')
        plt_module.xticks(rotation=45, ha='right')
        plt_module.tight_layout()

        # Save and display the plot
        output_file = f"category_spending_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt_module.savefig(output_file)
        logger.info(f"Saved category spending chart to {output_file}")
        plt_module.show()
        print(f"Chart saved as {output_file}")

    except ValueError as e:
        logger.error(f"Failed to generate chart: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error generating chart: {e}")
        print(f"Error generating chart: {e}")

if __name__ == "__main__":
    # Example usage for testing
    from datetime import datetime
    plot_category_spending("test_user", "2025-07-01", "2025-07-31")