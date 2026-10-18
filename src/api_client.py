import time
import logging
import requests
from requests.exceptions import RequestException
from src.config import SETTINGS

# Cấu hình logging cơ bản
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def fetch_all_pages(
    resource: str,
    updated_after: str | None = None,
    page_size: int = 100,
    timeout: int = 10,
    max_retries: int = 3,
    backoff_seconds: float = 1.0,
) -> list[dict]:
    """
    Thu thập toàn bộ các trang dữ liệu từ một tài nguyên REST API với cơ chế
    Bounded Exponential Retry và tự động phân trang (Pagination Loop).
    """
    url = f"{SETTINGS.mock_api_url}/{resource}"
    headers = {
        "X-API-Key": SETTINGS.mock_api_key,
        "Accept": "application/json"
    }

    page = 1
    rows = []

    while True:
        params = {"page": page, "page_size": page_size}
        if updated_after:
            params["updated_after"] = updated_after

        payload = None

        # Vòng lặp retry cho từng trang (Bounded Retry & Exponential Backoff)
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"[Attempt {attempt}/{max_retries}] Đang gọi GET tới {url} (page={page}, page_size={page_size})...")
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
                response.raise_for_status()
                
                payload = response.json()
                break  # Thành công -> thoát vòng retry
            except (RequestException, ValueError) as exc:
                logger.warning(
                    f"[Attempt {attempt}/{max_retries}] Lỗi khi gọi API resource '{resource}' (page {page}): {exc}"
                )
                if attempt == max_retries:
                    logger.error(f"Đã vượt quá số lần retry tối đa ({max_retries}) cho page {page}.")
                    raise RuntimeError(
                        f"API failed after {max_retries} attempts: {resource} page {page}"
                    ) from exc
                
                sleep_time = backoff_seconds * (2 ** (attempt - 1))
                logger.info(f"Đang chờ {sleep_time} giây trước khi retry...")
                time.sleep(sleep_time)

        # Trích xuất dữ liệu trang hiện tại
        page_rows = payload.get("data", [])
        rows.extend(page_rows)
        
        # Log tiến độ chuẩn yêu cầu đề bài
        logger.info(
            f"resource={resource} page={page} rows={len(page_rows)} total_so_far={len(rows)}"
        )

        # Điều kiện dừng phân trang khi has_next = False
        if not payload.get("has_next", False):
            logger.info(f"Đã duyệt xong tất cả các trang của resource '{resource}'. Tổng số bản ghi: {len(rows)}")
            break

        page += 1

    return rows

if __name__ == "__main__":
    print("=== TEST PHÂN TRANG TOÀN BỘ (FETCH ALL PAGES) ===")
    try:
        all_orders = fetch_all_pages(resource="orders", page_size=100)
        print(f"Thành công! Tổng số orders thu thập được: {len(all_orders)}")
    except Exception as e:
        print(f"Lỗi ngoài cùng: {e}")