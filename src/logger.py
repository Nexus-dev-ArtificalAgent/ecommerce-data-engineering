import logging
import sys
from pathlib import Path

def get_logger(name: str = 'pipeline') -> logging.Logger:
    """
    Tạo và cấu hình logger chuẩn cho pipeline:
    - Ghi đồng thời ra console (StreamHandler) và file logs/pipeline.log (FileHandler).
    - Tránh bị trùng lặp handlers nếu gọi nhiều lần.
    - Định dạng log tiêu chuẩn: %(asctime)s | %(levelname)s | %(name)s | %(message)s
    """
    # 1. Tự động kiểm tra và tạo thư mục logs/ nếu chưa tồn tại
    log_dir = Path('logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 3. Tránh duplicate handlers khi gọi nhiều lần
    if logger.handlers:
        return logger
        
    log_format = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    
    # 2. Cấu hình File Handler (ghi vào logs/pipeline.log với utf-8)
    file_handler = logging.FileHandler(log_dir / 'pipeline.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    
    # 2. Cấu hình Stream Handler (xuất ra console)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(log_format)
    
    # Thêm handlers vào logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger

# Khởi tạo logger dùng riêng cho việc chạy kiểm thử
logger = get_logger("pipeline_test")

if __name__ == "__main__":
    logger.info("Bắt đầu khởi động hệ thống kiểm tra Pipeline Logging...")
    
    # Giả lập một kịch bản bắt lỗi cụ thể
    missing_file = Path("data/incremental/day_2026-07-01/non_existent.csv")
    try:
        if not missing_file.exists():
            raise FileNotFoundError(f"Không tìm thấy file dataset: {missing_file.as_posix()}")
    except FileNotFoundError as e:
        # Ghi log ở mức ERROR kèm ngữ cảnh rõ ràng trước khi raise
        logger.error(f"Lỗi thao tác dữ liệu -> Dataset: non_existent.csv | Path: {missing_file.as_posix()} | Chi tiết: {e}")
        
    logger.info("Hoàn tất quy trình kiểm tra logging thành công!")