import pandas as pd
from pathlib import Path
from src.config import SETTINGS
from src.extract_files import extract_file

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Thực hiện chuẩn hóa kỹ thuật cho DataFrame theo chuẩn Bài 1.4:
    1. Bảo toàn RAW (sử dụng copy()).
    2. Chuẩn hóa tên cột (strip và lowercase).
    3. Chuẩn hóa chuỗi (strip khoảng trắng thừa).
    4. Chuẩn hóa email và các cột enums về lowercase.
    5. Ép kiểu số (numeric) an toàn với errors='coerce'.
    6. Ép kiểu thời gian (timestamp/UTC) cho các cột có hậu tố _at hoặc _date.
    """
    # 1. Bảo toàn RAW Immutability
    out = df.copy()
    
    # 2. Chuẩn hóa tên cột
    out.columns = [str(c).strip().lower() for c in out.columns]
    
    # 3. Chuẩn hóa chuỗi (Strings): duyệt các cột object/string
    for col in out.select_dtypes(include=['object', 'string']).columns:
        out[col] = out[col].astype(str).str.strip()
        out.loc[out[col].isin(['nan', 'None', '']), col] = None

    # 4. Chuẩn hóa Email & Enums khớp ràng buộc Database
    enum_columns = ['status', 'payment_status', 'payment_method', 'channel']
    if 'email' in out.columns:
        out['email'] = out['email'].astype(str).str.lower().replace(['nan', 'none'], None)
        
    for col in enum_columns:
        if col in out.columns:
            out[col] = out[col].astype(str).str.lower().replace(['nan', 'none'], None)

    # 5. Ép kiểu số (Numerics)
    numeric_columns = ['unit_price', 'cost_price', 'order_total', 'discount_amount', 'amount', 'quantity']
    for col in numeric_columns:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors='coerce')

    # 6. Ép kiểu thời gian (Timestamps) chuẩn UTC cho các cột có _at hoặc _date
    for col in out.columns:
        if col.endswith('_at') or col.endswith('_date'):
            out[col] = pd.to_datetime(out[col], errors='coerce', utc=True)

    return out

def run_normalization_verification(day_folder: str = "day_2026-07-01"):
    """
    Kiểm tra quá trình chuẩn hóa trên 5 dataset thực tế và in ra kiểu dữ liệu (dtypes) sau khi transform.
    """
    target_dir = SETTINGS.root / "data" / "incremental" / day_folder
    
    files = [
        "customers_daily.csv",
        "products_daily.csv",
        "orders_daily.csv",
        "order_items_daily.csv",
        "payments_daily.json"
    ]
    
    print(f"=== Technical Data Normalization Verification ({day_folder}) ===")
    for file_name in files:
        file_path = target_dir / file_name
        try:
            # 1. Đọc dữ liệu thô bằng hàm extract đã viết ở bài trước
            raw_df = extract_file(file_path)
            
            # 2. Gọi hàm normalize
            clean_df = normalize(raw_df)
            
            dataset_name = file_name.split('.')[0]
            print(f"\n[SUCCESS] {dataset_name}:")
            print(f" - Before shape: {raw_df.shape} | After shape: {clean_df.shape}")
            print(f" - Columns: {list(clean_df.columns)}")
            print(" - Dtypes sau khi chuẩn hóa:")
            print(clean_df.dtypes)
        except Exception as e:
            print(f"\n[ERROR] {file_name} -> {e}")

if __name__ == "__main__":
    run_normalization_verification()