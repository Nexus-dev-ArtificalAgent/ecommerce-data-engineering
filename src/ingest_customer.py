# Save as ingest_customers.py or run via pipeline
from src.pipeline import ingest_api_raw

# Ingest toàn bộ danh sách khách hàng mới nhất từ API
ingest_api_raw("customers")