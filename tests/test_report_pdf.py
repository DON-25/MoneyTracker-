import pytest
from click.testing import CliRunner
from cli.commands import report_pdf
from unittest.mock import patch, MagicMock

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def sample_transactions():
    return [
        MagicMock(amount=1000, type='income', category='Salary'),
        MagicMock(amount=300, type='expense', category='Food'),
        MagicMock(amount=200, type='expense', category='Transport'),
    ]

@patch("cli.commands.get_db")
@patch("cli.commands.export_summary_to_pdf")
@patch("cli.commands.validate_user_id")
@patch("cli.commands.validate_date")
@patch("cli.commands.validate_date_range")
def test_report_pdf_success(mock_validate_range, mock_validate_date, mock_validate_user, mock_export_pdf, mock_get_db, runner, sample_transactions):
    # 模拟数据库返回交易数据
    mock_db = MagicMock()
    mock_db.read_all.return_value = sample_transactions
    mock_get_db.return_value = mock_db

    # 模拟导出函数返回路径
    mock_export_pdf.return_value = "output.pdf"

    result = runner.invoke(report_pdf, [
        "--user-id", "user123",
        "--start-date", "2025-01-01",
        "--end-date", "2025-01-31",
        "--output", "output.pdf"
    ])

    assert result.exit_code == 0
    assert "PDF report exported to: output.pdf" in result.output

    # 验证调用情况
    mock_validate_user.assert_called_once_with("user123")
    mock_validate_date.assert_any_call("2025-01-01")
    mock_validate_date.assert_any_call("2025-01-31")
    mock_validate_range.assert_called_once_with("2025-01-01", "2025-01-31")
    mock_db.read_all.assert_called_once()
    mock_export_pdf.assert_called_once()

@patch("cli.commands.get_db")
@patch("cli.commands.validate_user_id")
def test_report_pdf_no_transactions(mock_validate_user, mock_get_db, runner):
    mock_db = MagicMock()
    mock_db.read_all.return_value = []
    mock_get_db.return_value = mock_db

    result = runner.invoke(report_pdf, [
        "--user-id", "user123"
    ])

    assert result.exit_code == 0
    assert "No transactions found for user user123" in result.output

@patch("cli.commands.validate_date")
def test_report_pdf_invalid_date(mock_validate_date, runner):
    # 模拟日期验证失败抛出异常
    mock_validate_date.side_effect = Exception("Invalid date")

    result = runner.invoke(report_pdf, [
        "--user-id", "user123",
        "--start-date", "invalid-date"
    ])

    assert result.exit_code != 0
    assert "Invalid date" in result.output
