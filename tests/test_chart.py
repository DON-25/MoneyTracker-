import pytest
from unittest.mock import patch, MagicMock
from views.chart import plot_category_spending

class TestChart:
    @patch("views.chart.plt")  # Mock matplotlib.pyplot
    @patch("services.tracker.TrackerService.list_transactions")
    @patch("services.tracker.TrackerService.get_summary")
    def test_plot_category_spending_success(self, mock_get_summary, mock_list_transactions, mock_plt):
        mock_plt.bar = MagicMock()
        mock_plt.savefig = MagicMock()
        mock_plt.show = MagicMock()
        # Mock summary data
        mock_get_summary.return_value = {
            "transaction_count": 3,
            "total_income": 1000.0,
            "total_expense": 500.0,
            "balance": 500.0,
            "category_summary": {"Food": 200.0, "Rent": 300.0}
        }

        # Mock list_transactions returns Transaction objects
        Transaction = MagicMock()
        Transaction.type = "expense"
        Transaction.category = "Food"
        mock_list_transactions.return_value = [Transaction, Transaction]

        plot_category_spending("test_user", "2025-07-01", "2025-07-31", plt_module=mock_plt)

        # Check if the chart was saved and displayed
        assert mock_plt.savefig.called
        assert mock_plt.bar.called
        assert mock_plt.show.called

    @patch("views.chart.plt")
    @patch("services.tracker.TrackerService.get_summary")
    def test_plot_category_spending_no_data(self, mock_get_summary, mock_plt):
        mock_get_summary.return_value = {"transaction_count": 0}
        result = plot_category_spending("test_user", plt_module=mock_plt)
        assert result is None
