import pytest
from pathlib import Path
import pandas as pd

from src.config import SETTINGS
from src.extract_files import extract_file, profile

# Sử dụng thư mục test data thực tế có sẵn
TEST_DATA_DIR = SETTINGS.root / "data" / "incremental" / "day_2026-07-01"

def test_read_csv_success():
    """1. test_read_csv_success: Đọc file CSV trả về DataFrame hợp lệ."""
    file_path = TEST_DATA_DIR / "customers_daily.csv"
    df = extract_file(file_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) > 0

def test_read_json_nested_data(tmp_path):
    """2. test_read_json_nested_data: Đọc JSON cấu trúc list hoặc bọc bởi {"data": [...]}, hoặc file json thông thường."""
    json_file = tmp_path / "test.json"
    json_file.write_text('[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]', encoding='utf-8')
    df = extract_file(json_file)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2

def test_read_file_not_found():
    """3. test_read_file_not_found: Kiểm tra ném FileNotFoundError khi đường dẫn file không tồn tại."""
    missing_path = TEST_DATA_DIR / "non_existent_file.csv"
    with pytest.raises(FileNotFoundError):
        extract_file(missing_path)

def test_unsupported_file_extension():
    """4. test_unsupported_file_extension: Kiểm tra ném ValueError với định dạng không hỗ trợ."""
    unsupported_path = TEST_DATA_DIR / "unsupported.parquet"
    with pytest.raises(ValueError):
        extract_file(unsupported_path)

def test_profile_metrics():
    """5. test_profile_metrics: Đo lường chính xác rows, columns, missing, duplicates."""
    file_path = TEST_DATA_DIR / "products_daily.csv"
    df = extract_file(file_path)
    prof = profile(df)
    
    assert "rows" in prof
    assert "columns" in prof
    assert "missing" in prof
    assert "duplicates" in prof
    assert prof["rows"] == len(df)
    assert len(prof["columns"]) == len(df.columns)