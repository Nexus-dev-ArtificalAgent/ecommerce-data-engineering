import argparse
from pathlib import Path
import pandas as pd

from src.config import SETTINGS
from src.logger import get_logger
from src.extract_files import extract_file, profile
from src.transform import normalize

# Khởi tạo logger cho pipeline runner
logger = get_logger("file_pipeline_runner")

def run_pipeline(input_dir: str):
    """
    Chạy batch pipeline tự động hóa từ RAW sang STAGING cho 5 dataset:
    - Đọc file (extract)
    - Phân tích kỹ thuật (profile)
    - Chuẩn hóa dữ liệu (normalize)
    - Xuất file sạch vào thư mục data/staging/
    """
    input_path = SETTINGS.root / input_dir
    staging_path = SETTINGS.root / "data" / "staging"
    
    # 1. Tự động tạo thư mục staging nếu chưa tồn tại
    staging_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"=== Bắt đầu chạy File Ingestion Batch Runner cho thư mục: {input_path.as_posix()} ===")
    
    # Danh sách 5 datasets cần xử lý tuần tự
    datasets = [
        ("customers_daily.csv", "customers"),
        ("products_daily.csv", "products"),
        ("orders_daily.csv", "orders"),
        ("order_items_daily.csv", "order_items"),
        ("payments_daily.json", "payments")
    ]
    
    for file_name, dataset_name in datasets:
        file_path = input_path / file_name
        try:
            logger.info(f"Đang xử lý dataset: {dataset_name} (File: {file_name})")
            
            # 2. Đọc dữ liệu thô (giữ nguyên file gốc tuyệt đối)
            raw_df = extract_file(file_path)
            in_rows, in_cols = raw_df.shape
            
            # 3. Chạy profile baseline ghi nhận thông số
            prof_stats = profile(raw_df)
            logger.info(f"[{dataset_name}] Profiling -> Rows: {prof_stats['rows']}, Cols: {len(prof_stats['columns'])}, Duplicates: {prof_stats['duplicates']}")
            
            # 4. Chuẩn hóa kỹ thuật (Normalization)
            clean_df = normalize(raw_df)
            out_rows, out_cols = clean_df.shape
            
            # 5. Xuất dữ liệu đã chuẩn hóa vào vùng STAGING dưới dạng CSV
            output_file = staging_path / f"{dataset_name}_clean.csv"
            clean_df.to_csv(output_file, index=False, encoding='utf-8')
            
            logger.info(f"[SUCCESS] {dataset_name} -> Input rows: {in_rows} | Output rows: {out_rows} | Đã lưu tại: {output_file.as_posix()}")
            
        except Exception as e:
            logger.error(f"[ERROR] Thất bại khi xử lý dataset {dataset_name} tại đường dẫn {file_path.as_posix()}: {e}")
            raise
            
    logger.info("=== Hoàn tất toàn bộ chuỗi Pipeline RAW -> STAGING thành công rực rỡ! ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File Ingestion Batch Runner (RAW -> STAGING Pipeline)")
    parser.add_argument(
        "--input-dir", 
        type=str, 
        default="data/incremental/day_2026-07-01", 
        help="Đường dẫn thư mục chứa dữ liệu thô đầu vào"
    )
    args = parser.parse_args()
    run_pipeline(args.input_dir)