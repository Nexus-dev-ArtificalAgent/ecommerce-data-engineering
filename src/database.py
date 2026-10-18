from sqlalchemy import create_engine
from src.config import SETTINGS

# Khởi tạo SQLAlchemy Engine kết nối tới PostgreSQL
engine = create_engine(SETTINGS.database_url)