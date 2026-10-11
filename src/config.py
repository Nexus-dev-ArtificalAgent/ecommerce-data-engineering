import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load các biến môi trường từ file .env
load_dotenv()

@dataclass(frozen=True)
class Settings:
    # Xác định thư mục gốc của project (lùi lên 2 cấp từ file hiện tại src/config.py)
    root: Path = Path(__file__).resolve().parents[1]
    
    # Đọc cấu hình từ biến môi trường
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ecommerce")
    mock_api_url: str = os.getenv("MOCK_API_URL", "")
    mock_api_key: str = os.getenv("MOCK_API_KEY", "")
    
    # Định nghĩa các đường dẫn thư mục chuẩn dạng Path theo cấu trúc project
    raw_dir: Path = root / "data" / "raw"
    staging_dir: Path = root / "data" / "staging"
    reject_dir: Path = root / "data" / "reject"
    metadata_dir: Path = root / "metadata"
    report_dir: Path = root / "reports"

# Khởi tạo đối tượng toàn cục dùng chung cho toàn bộ pipeline
SETTINGS = Settings()

if __name__ == "__main__":
    # Test in cấu hình ra màn hình để kiểm tra
    print(SETTINGS)