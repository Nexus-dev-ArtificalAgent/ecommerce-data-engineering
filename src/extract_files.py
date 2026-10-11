import pandas as pd
from pathlib import Path
from src.config import SETTINGS

def extract_file(file_path: Path) -> pd.DataFrame:
    """
    Hàm đọc và kiểm tra tính hợp lệ của file (hỗ trợ CSV và JSON).
    Ném ra các ngoại lệ chuẩn nếu file lỗi hoặc không hợp lệ.
    """
    path = Path(file_path)
    
    # 1. Kiểm tra file có tồn tại không (Missing file test)
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path.as_posix()}")
        
    # 2. Kiểm tra định dạng phần mở rộng (Unsupported extension test)
    if path.suffix not in ['.csv', '.json']:
        raise ValueError(f"Unsupported file: {path.as_posix()}")
        
    # 3. Kiểm tra file có bị trống không (Empty file test)
    if path.stat().st_size == 0:
        raise ValueError(f"Empty dataset: {path.as_posix()}")
        
    # Đọc dữ liệu dựa vào định dạng file
    if path.suffix == '.csv':
        df = pd.read_csv(path)
    elif path.suffix == '.json':
        df = pd.read_json(path)
        
    # Đề phòng trường hợp file CSV/JSON có dung lượng nhưng không chứa dòng dữ liệu nào
    if df.empty:
        raise ValueError(f"Empty dataset: {path.as_posix()}")
        
    return df

def profile(df: pd.DataFrame) -> dict:
    """
    Thực hiện profiling kỹ thuật cho DataFrame theo yêu cầu Bài 1.3:
    - rows: tổng số dòng (len(df))
    - columns: danh sách tên cột (list(df.columns))
    - missing: số lượng giá trị thiếu theo từng cột (df.isna().sum().to_dict())
    - duplicates: số dòng trùng lặp toàn bộ bản ghi (int(df.duplicated().sum()))
    Trả về dictionary cấu trúc chuẩn.
    """
    return {
        'rows': int(len(df)),
        'columns': list(df.columns),
        'missing': df.isna().sum().to_dict(),
        'duplicates': int(df.duplicated().sum())
    }

def run_extraction_pipeline(day_folder: str = "day_2026-07-01"):
    """
    Thực hiện trích xuất dữ liệu hàng ngày và in ra log minh chứng thành công.
    """
    target_dir = SETTINGS.root / "data" / "incremental" / day_folder
    
    # In tiêu đề bám sát chuẩn minh chứng
    print(f"=== Extraction Verification (data/incremental/{day_folder}) ===")
    
    files = [
        "customers_daily.csv",
        "products_daily.csv",
        "orders_daily.csv",
        "order_items_daily.csv",
        "payments_daily.json"
    ]
    
    for file_name in files:
        file_path = target_dir / file_name
        try:
            df = extract_file(file_path)
            print(f" [SUCCESS] {file_name} -> {df.shape[0]} rows, {df.shape[1]} columns")
        except Exception as e:
            print(f" [ERROR] {file_name} -> {e}")

def run_profiling_pipeline(day_folder: str = "day_2026-07-01"):
    """
    Chạy profiling kỹ thuật cho từng dataset và in báo cáo.
    """
    target_dir = SETTINGS.root / "data" / "incremental" / day_folder
    
    print(f"\n=== Data Profiling Baseline (data/incremental/{day_folder}) ===")
    
    files = [
        "customers_daily.csv",
        "products_daily.csv",
        "orders_daily.csv",
        "order_items_daily.csv",
        "payments_daily.json"
    ]
    
    for file_name in files:
        file_path = target_dir / file_name
        try:
            df = extract_file(file_path)
            prof = profile(df)
            dataset_name = file_name.split('.')[0]
            print(f"dataset={dataset_name} rows={prof['rows']} cols={len(prof['columns'])} missing={prof['missing']} duplicates={prof['duplicates']}")
        except Exception as e:
            print(f" [ERROR] {file_name} -> {e}")

def run_exception_tests(day_folder: str = "day_2026-07-01"):
    """
    Kiểm thử các ngoại lệ để khớp với phần 2 của minh chứng.
    """
    target_dir = SETTINGS.root / "data" / "incremental" / day_folder
    
    print("\n=== Targeted Exception Handling Verification ===")
    
    # [TEST 1] Missing file test
    print("[TEST 1] Missing file test:")
    missing_path = target_dir / "missing.csv"
    print(f" path = {missing_path.relative_to(SETTINGS.root).as_posix()}")
    try:
        extract_file(missing_path)
    except Exception as e:
        print(f" result -> {type(e).__name__}: {e}")
        
    # [TEST 2] Unsupported extension test
    print("\n[TEST 2] Unsupported extension test:")
    unsupported_path = target_dir / "unsupported.parquet"
    print(f" path = {unsupported_path.relative_to(SETTINGS.root).as_posix()}")
    try:
        extract_file(unsupported_path)
    except Exception as e:
        print(f" result -> {type(e).__name__}: {e}")
        
    # [TEST 3] Empty file test
    print("\n[TEST 3] Empty file test:")
    empty_path = target_dir / "empty.csv"
    print(f" path = {empty_path.relative_to(SETTINGS.root).as_posix()}")
    try:
        extract_file(empty_path)
    except Exception as e:
        print(f" result -> {type(e).__name__}: {e}")

if __name__ == "__main__":
    run_extraction_pipeline()
    run_profiling_pipeline()
    run_exception_tests()