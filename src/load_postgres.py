import json
import logging
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)

PK = {
    'customers': 'customer_id',
    'products': 'product_id',
    'orders': 'order_id',
    'order_items': 'order_item_id',
    'payments': 'payment_id',
}

def _python_value(value):
    if value is None:
        return None
    try:
        if str(value) in {'NaT', 'nan', '<NA>'}:
            return None
    except Exception:
        pass
    if hasattr(value, 'to_pydatetime'):
        return value.to_pydatetime()
    if hasattr(value, 'item'):
        try:
            return value.item()
        except Exception:
            pass
    return value

def upsert_dataframe(name: str, df: pd.DataFrame) -> dict:
    if df.empty:
        return {'inserted': 0, 'updated': 0, 'inserted_or_updated': 0}

    pk = PK[name]
    cols = [c for c in df.columns if c != 'error_code']
    incoming_ids = set(df[pk].astype(str))

    with engine.connect() as conn:
        existing_ids = set(
            map(str, conn.execute(text(f"SELECT {pk} FROM core.{name}")).scalars().all())
        )

    inserted = len(incoming_ids - existing_ids)
    updated = len(incoming_ids & existing_ids)

    logger.info(f"[UPSERT] table=core.{name} incoming={len(incoming_ids)} inserted={inserted} updated={updated}")

    placeholders = ', '.join(':' + c for c in cols)
    updates = ', '.join(f"{c}=EXCLUDED.{c}" for c in cols if c != pk)
    sql = text(
        f"INSERT INTO core.{name} ({','.join(cols)}) VALUES ({placeholders}) "
        f"ON CONFLICT ({pk}) DO UPDATE SET {updates}"
    )

    records = [
        {k: _python_value(v) for k, v in row.items()}
        for row in df[cols].to_dict('records')
    ]

    with engine.begin() as conn:
        conn.execute(sql, records)

    return {'inserted': inserted, 'updated': updated, 'inserted_or_updated': len(records)}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    
    raw_dirs = sorted(Path("data/raw").glob("run_*"))
    if raw_dirs:
        latest_dir = raw_dirs[-1]
        print(f"--- Đang nạp dữ liệu từ phiên: {latest_dir.name} ---")

        # 1. Nạp customers trước để thỏa mãn khóa ngoại
        cust_file = latest_dir / "customers.json"
        if cust_file.exists():
            df_cust = pd.DataFrame(json.loads(cust_file.read_text(encoding="utf-8")))
            print("Kết quả UPSERT Customers:", upsert_dataframe("customers", df_cust))

        # 2. Nạp products
        prod_file = latest_dir / "products.json"
        if prod_file.exists():
            df_prod = pd.DataFrame(json.loads(prod_file.read_text(encoding="utf-8")))
            print("Kết quả UPSERT Products:", upsert_dataframe("products", df_prod))

        # 3. Sau đó mới nạp orders
        orders_file = latest_dir / "orders.json"
        if orders_file.exists():
            df_orders = pd.DataFrame(json.loads(orders_file.read_text(encoding="utf-8")))
            print("Kết quả UPSERT Orders:", upsert_dataframe("orders", df_orders))
    else:
        print("Không tìm thấy thư mục raw nào!")