import psycopg2
import pandas as pd
from pathlib import Path
from src.config import SETTINGS
from src.logger import get_logger

logger = get_logger("refresh_mart")

KPI_QUERY = """
SELECT 
    COALESCE(SUM(net_amount), 0) AS total_revenue,
    COUNT(DISTINCT order_id) AS order_count,
    COUNT(DISTINCT CASE WHEN status = 'completed' THEN order_id END) AS completed_orders,
    COALESCE(SUM(quantity), 0) AS total_items_sold
FROM mart.fact_sales;
"""

def fetch_kpis(conn) -> dict:
    """Truy vấn 4 chỉ số KPI cốt lõi trên bảng mart.fact_sales (Xử lý an toàn khi bảng chưa tồn tại)."""
    try:
        with conn.cursor() as cur:
            cur.execute(KPI_QUERY)
            row = cur.fetchone()
            if row:
                return {
                    "total_revenue": float(row[0] or 0),
                    "order_count": int(row[1] or 0),
                    "completed_orders": int(row[2] or 0),
                    "total_items_sold": int(row[3] or 0)
                }
    except psycopg2.errors.UndefinedTable:
        conn.rollback()  # Bắt buộc rollback transaction bị lỗi trong PostgreSQL
        logger.info("Bảng mart.fact_sales chưa tồn tại (chạy lần đầu). Thiết lập KPI ban đầu bằng 0.")
    except Exception as e:
        conn.rollback()
        logger.warning(f"Lỗi khi truy vấn KPI: {e}")
        
    return {"total_revenue": 0.0, "order_count": 0, "completed_orders": 0, "total_items_sold": 0}

def refresh_sales_mart():
    logger.info("Bắt đầu quy trình làm mới Sales Data Mart...")
    conn = psycopg2.connect(SETTINGS.database_url)
    try:
        # 1. Đo lường KPI TRƯỚC khi làm mới (nếu chưa có bảng sẽ trả về 0)
        kpis_before = fetch_kpis(conn)
        logger.info(f"KPI trước khi làm mới: {kpis_before}")

        # 2. Đọc và thực thi kịch bản SQL nạp Data Mart từ thư mục sql/solutions/
        sql_file = SETTINGS.root / "sql" / "solutions" / "12_load_data_mart.sql"
        if not sql_file.exists():
            raise FileNotFoundError(f"Không tìm thấy kịch bản SQL tại đường dẫn: {sql_file}")
            
        sql_script = sql_file.read_text(encoding="utf-8")
        logger.info(f"Đang thực thi kịch bản SQL từ {sql_file}...")
        
        with conn.cursor() as cur:
            cur.execute(sql_script)
        conn.commit()
        logger.info("Thực thi script SQL làm mới Data Mart thành công!")

        # 3. Đo lường KPI SAU khi làm mới
        kpis_after = fetch_kpis(conn)
        logger.info(f"KPI sau khi làm mới: {kpis_after}")

        # 4. Tính toán chênh lệch (diff) và xuất bảng đối chiếu ra file CSV chuẩn yêu cầu
        comparison_data = []
        for kpi_name in ["total_revenue", "order_count", "completed_orders", "total_items_sold"]:
            b_val = kpis_before[kpi_name]
            a_val = kpis_after[kpi_name]
            diff_val = a_val - b_val
            comparison_data.append({
                "kpi": kpi_name,
                "before": b_val,
                "after": a_val,
                "diff": diff_val
            })

        df_comp = pd.DataFrame(comparison_data)
        
        # Đảm bảo thư mục docs tồn tại
        docs_dir = SETTINGS.root / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        csv_path = docs_dir / "kpi_comparison.csv"
        
        df_comp.to_csv(csv_path, index=False)
        logger.info(f"Đã xuất bảng đối chiếu KPI thành công tại: {csv_path}")
        
        # In trực tiếp ra console để tiện theo dõi
        print("\n=== BẢNG ĐỐI CHIẾU KPI (BEFORE vs AFTER) ===")
        print(df_comp.to_string(index=False))
        print("===========================================\n")

    except Exception as e:
        conn.rollback()
        logger.exception(f"[CRITICAL ERROR] Lỗi khi làm mới Data Mart: {e}")
        raise e
    finally:
        conn.close()
        logger.info("Đã đóng kết nối cơ sở dữ liệu an toàn.")

if __name__ == "__main__":
    refresh_sales_mart()