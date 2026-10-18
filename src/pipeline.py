import json
import logging
from datetime import datetime
from pathlib import Path

from src.api_client import fetch_all_pages
from src.config import SETTINGS

logger = logging.getLogger(__name__)


def ingest_api_raw(resource_name: str, run_id: str | None = None) -> Path:
    """Thu thập toàn bộ dữ liệu của một resource từ API và lưu RAW Immutability."""
    if not run_id:
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    raw_dir = SETTINGS.raw_dir / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)

    api_endpoint = {
        'customers': 'customers',
        'products': 'products',
        'orders': 'orders',
        'order_items': 'order-items',
        'payments': 'payments',
    }.get(resource_name, resource_name)

    logger.info(f"Bắt đầu thu thập RAW cho resource: {resource_name} (Run ID: {run_id})")
    rows = fetch_all_pages(api_endpoint, page_size=100)

    raw_file = raw_dir / f"{resource_name}.json"
    raw_file.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    logger.info(f"RAW saved to {raw_file} ({len(rows)} records)")
    return raw_file


def run_full_ingestion() -> str:
    """Điều phối thu thập toàn bộ các bảng."""
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"=== BẮT ĐẦU QUY TRÌNH INGESTION (Run ID: {run_id}) ===")

    resources = ["customers", "products", "orders", "order_items", "payments"]
    for res in resources:
        try:
            ingest_api_raw(res, run_id=run_id)
        except Exception as e:
            logger.error(f"Lỗi khi ingest resource {res}: {e}")

    logger.info(f"=== HOÀN THÀNH QUY TRÌNH INGESTION CHO RUN_ID: {run_id} ===")
    return run_id


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    run_full_ingestion()