import pytest
from unittest.mock import patch, MagicMock
from views.report import display_tabular_summary

@patch("views.report.tracker.get_summary")
@patch("views.report.console.print")
def test_display_tabular_summary_success(mock_console_print, mock_get_summary):
    # 模拟交易摘要
    mock_get_summary.return_value = {
        "transaction_count": 4,
        "total_income": 1000.0,
        "total_expense": 400.0,
        "balance": 600.0,
        "category_summary": {"Food": 200.0, "Books": 200.0}
    }

    display_tabular_summary("test_user", "2025-07-01", "2025-07-31")

    # 应该输出至少 2 次表格
    assert mock_console_print.call_count >= 2

@patch("views.report.tracker.get_summary")
@patch("views.report.console.print")
def test_display_tabular_summary_no_data(mock_console_print, mock_get_summary):
    mock_get_summary.return_value = {"transaction_count": 0}
    display_tabular_summary("test_user")
    mock_console_print.assert_called_with("[yellow]No transactions found for user test_user[/yellow]")
