import os
from utils.pdf_exporter import export_summary_to_pdf

def test_export_summary_to_pdf(tmp_path):
    summary = {
        "transaction_count": 3,
        "total_income": 2000.0,
        "total_expense": 1500.0,
        "balance": 500.0,
        "category_summary": {"Food": 800.0, "Rent": 700.0}
    }
    output = tmp_path / "report.pdf"
    result_path = export_summary_to_pdf(summary, str(output))
    
    # 检查是否生成了文件
    assert os.path.exists(result_path)
    assert result_path.endswith(".pdf")
    assert os.path.getsize(result_path) > 0
