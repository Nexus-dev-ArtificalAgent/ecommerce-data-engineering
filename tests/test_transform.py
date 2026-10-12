import pytest
import pandas as pd
from src.extract_files import extract_file
from src.transform import normalize
from src.config import SETTINGS

TEST_DATA_DIR = SETTINGS.root / "data" / "incremental" / "day_2026-07-01"

def test_normalize_raw_immutability():
    """6. test_normalize_raw_immutability: Xác nhận DataFrame nguồn không bị thay đổi sau khi chuẩn hóa."""
    file_path = TEST_DATA_DIR / "customers_daily.csv"
    raw_df = extract_file(file_path)
    
    # Sao chép bản sao thô để đối chiếu
    raw_copy = raw_df.copy(deep=True)
    
    # Thực hiện chuẩn hóa
    _ = normalize(raw_df)
    
    # Kiểm tra dữ liệu gốc tuyệt đối không thay đổi
    pd.testing.assert_frame_equal(raw_df, raw_copy)

def test_normalize_strings_and_enums():
    """7. test_normalize_strings_and_enums: Xác nhận trim khoảng trắng và lowercase các cột string/enum."""
    # Tạo dữ liệu giả lập có khoảng trắng và chữ hoa chữ thường lẫn lộn
    data = {
        "email": ["  TEST@Example.com ", "USER@domain.COM"],
        "status": [" ACTIVE ", "pending"],
        "payment_method": [" CREDIT_CARD ", "paypal"],
        "channel": [" WEB ", "mobile"]
    }
    df = pd.DataFrame(data)
    clean_df = normalize(df)
    
    assert clean_df["email"].iloc[0] == "test@example.com"
    assert clean_df["status"].iloc[0] == "active"
    assert clean_df["payment_method"].iloc[0] == "credit_card"
    assert clean_df["channel"].iloc[0] == "web"

def test_normalize_numeric_and_datetime():
    """8. test_normalize_numeric_and_datetime: Xác nhận ép kiểu số và parse ISO/UTC datetime."""
    data = {
        "amount": ["100.5", "abc", None],
        "created_at": ["2026-07-01 12:00:00", "invalid_date", None]
    }
    df = pd.DataFrame(data)
    clean_df = normalize(df)
    
    # Kiểm tra cột số đã được ép kiểu numeric (coerce lỗi thành NaN)
    assert pd.api.types.is_numeric_dtype(clean_df["amount"])
    # Kiểm tra cột thời gian đã được chuẩn hóa kiểu datetime
    assert pd.api.types.is_datetime64_any_dtype(clean_df["created_at"])