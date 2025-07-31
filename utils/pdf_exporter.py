from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from typing import Dict, Optional
import os

def export_summary_to_pdf(summary_data: Dict, output_path: Optional[str] = None):
    """
    Generate a PDF report for transaction summary using reportlab.
    :param summary_data: dict with keys: transaction_count, total_income, total_expense, balance, category_summary
    :param output_path: output PDF file path
    """
    if output_path is None:
        output_path = os.path.join(os.getcwd(), "transaction_summary.pdf")
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Transaction Summary Report")
    y -= 40
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Total Transactions: {summary_data.get('transaction_count', 0)}")
    y -= 20
    c.drawString(50, y, f"Total Income: {summary_data.get('total_income', 0):.2f}")
    y -= 20
    c.drawString(50, y, f"Total Expense: {summary_data.get('total_expense', 0):.2f}")
    y -= 20
    c.drawString(50, y, f"Balance: {summary_data.get('balance', 0):.2f}")
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Category Breakdown:")
    y -= 20
    c.setFont("Helvetica", 12)
    for category, amount in summary_data.get('category_summary', {}).items():
        c.drawString(60, y, f"{category}: {amount:.2f}")
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()
    return output_path
