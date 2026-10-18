import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def split_cross_table_invalid(
    name: str,
    df: pd.DataFrame,
    reference_data: dict[str, pd.DataFrame]
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """
    Kiểm tra Toàn vẹn tham chiếu (Foreign Key Checks) và Tính tuần tự thời gian (Chronology Check).
    Tách DataFrame thành (valid_df, rejected_df, violation_logs).
    """
    # Reset lại index để tránh lỗi IndexError khi DataFrame đầu vào là subset đã qua filter
    df_copy = df.copy().reset_index(drop=True)
    
    valid_mask = [True] * len(df_copy)
    error_codes = [[] for _ in range(len(df_copy))]
    violation_logs = []

    # 1. Foreign Key Checks
    if name == "products":
        if "categories" in reference_data and "category_id" in df_copy.columns:
            valid_categories = set(reference_data["categories"]["category_id"].dropna().astype(str))
            for idx, row in df_copy.iterrows():
                cat_id = str(row["category_id"]) if pd.notna(row["category_id"]) else ""
                if cat_id not in valid_categories:
                    valid_mask[idx] = False
                    error_codes[idx].append("FK_CATEGORY_NOT_FOUND")
                    p_id = row.get("product_id", f"ROW_{idx}")
                    violation_logs.append(
                        f"products id={p_id} category_id={cat_id} NOT FOUND (FK_CATEGORY_NOT_FOUND)"
                    )

    elif name == "orders":
        if "customers" in reference_data and "customer_id" in df_copy.columns:
            valid_customers = set(reference_data["customers"]["customer_id"].dropna().astype(str))
            for idx, row in df_copy.iterrows():
                cus_id = str(row["customer_id"]) if pd.notna(row["customer_id"]) else ""
                if cus_id not in valid_customers:
                    valid_mask[idx] = False
                    error_codes[idx].append("FK_CUSTOMER_NOT_FOUND")
                    o_id = row.get("order_id", f"ROW_{idx}")
                    violation_logs.append(
                        f"orders id={o_id} customer_id={cus_id} NOT FOUND (FK_CUSTOMER_NOT_FOUND)"
                    )

    elif name == "order_items":
        valid_orders = (
            set(reference_data["orders"]["order_id"].dropna().astype(str))
            if "orders" in reference_data and "order_id" in reference_data["orders"].columns
            else set()
        )
        valid_products = (
            set(reference_data["products"]["product_id"].dropna().astype(str))
            if "products" in reference_data and "product_id" in reference_data["products"].columns
            else set()
        )

        for idx, row in df_copy.iterrows():
            item_id = row.get("order_item_id", f"ROW_{idx}")
            ord_id = str(row["order_id"]) if pd.notna(row.get("order_id")) else ""
            prod_id = str(row["product_id"]) if pd.notna(row.get("product_id")) else ""

            if valid_orders and ord_id not in valid_orders:
                valid_mask[idx] = False
                error_codes[idx].append("FK_ORDER_NOT_FOUND")
                violation_logs.append(
                    f"order_items id={item_id} order_id={ord_id} NOT FOUND (FK_ORDER_NOT_FOUND)"
                )

            if valid_products and prod_id not in valid_products:
                valid_mask[idx] = False
                error_codes[idx].append("FK_PRODUCT_NOT_FOUND")
                violation_logs.append(
                    f"order_items id={item_id} product_id={prod_id} NOT FOUND (FK_PRODUCT_NOT_FOUND)"
                )

    elif name == "payments":
        valid_orders_df = reference_data.get("orders")
        valid_orders = (
            set(valid_orders_df["order_id"].dropna().astype(str))
            if valid_orders_df is not None and "order_id" in valid_orders_df.columns
            else set()
        )

        order_date_map = {}
        if valid_orders_df is not None and "order_id" in valid_orders_df.columns and "order_date" in valid_orders_df.columns:
            for _, o_row in valid_orders_df.iterrows():
                if pd.notna(o_row["order_id"]) and pd.notna(o_row["order_date"]):
                    try:
                        parsed_date = pd.to_datetime(o_row["order_date"])
                        order_date_map[str(o_row["order_id"])] = parsed_date
                    except Exception:
                        continue

        for idx, row in df_copy.iterrows():
            pay_id = row.get("payment_id", f"ROW_{idx}")
            ord_id = str(row["order_id"]) if pd.notna(row.get("order_id")) else ""

            if valid_orders and ord_id not in valid_orders:
                valid_mask[idx] = False
                error_codes[idx].append("FK_ORDER_NOT_FOUND")
                violation_logs.append(
                    f"payments id={pay_id} order_id={ord_id} NOT FOUND (FK_ORDER_NOT_FOUND)"
                )

            if pd.notna(row.get("payment_date")) and ord_id in order_date_map:
                try:
                    pay_date = pd.to_datetime(row["payment_date"])
                    ord_date = order_date_map[ord_id]
                    if pay_date < ord_date:
                        valid_mask[idx] = False
                        error_codes[idx].append("PAYMENT_BEFORE_ORDER")
                        violation_logs.append(
                            f"payments id={pay_id} payment_date={pay_date} < order_date={ord_date} (PAYMENT_BEFORE_ORDER)"
                        )
                except Exception:
                    pass

    df_copy["error_code"] = ["|".join(errs) for errs in error_codes]
    valid_df = df_copy[valid_mask].drop(columns=["error_code"])
    rejected_df = df_copy[~pd.Series(valid_mask, index=df_copy.index)].copy()

    return valid_df, rejected_df, violation_logs


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    dirty_dir = Path("data/dirty/day_2026-07-02")
    evidence_dir = Path("docs/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    dataset_file_mapping = {
        "categories": "categories_daily.csv",
        "customers": "customers_daily.csv",
        "products": "products_daily.csv",
        "orders": "orders_daily.csv",
        "order_items": "order_items_daily.csv",
        "payments": "payments_daily",
    }

    datasets = {}
    for ds_name, filename in dataset_file_mapping.items():
        file_path = dirty_dir / filename
        if not file_path.exists():
            matches = list(dirty_dir.glob(f"{ds_name}*"))
            if matches:
                file_path = matches[0]
            else:
                continue

        if file_path.suffix.lower() == ".csv":
            datasets[ds_name] = pd.read_csv(file_path)
        else:
            try:
                datasets[ds_name] = pd.read_json(file_path)
            except Exception:
                import json
                data = json.loads(file_path.read_text(encoding="utf-8"))
                datasets[ds_name] = pd.DataFrame(data)

    if "categories" not in datasets:
        datasets["categories"] = pd.DataFrame({"category_id": ["CAT001", "CAT002", "CAT003"]})

    all_violations = []
    check_order = ["products", "orders", "order_items", "payments"]

    for dataset in check_order:
        if dataset in datasets:
            logger.info(f"Đang kiểm tra Cross-Table Integrity & Chronology cho bảng: {dataset}")
            valid_df, rejected_df, violations = split_cross_table_invalid(
                dataset, datasets[dataset], datasets
            )
            logger.info(
                f"  --> {dataset}: Valid={len(valid_df)}, Rejected={len(rejected_df)}, Violations={len(violations)}"
            )
            all_violations.extend(violations)

    evidence_file = evidence_dir / "07-integrity.txt"
    evidence_file.write_text("\n".join(all_violations), encoding="utf-8")
    logger.info(f"Đã xuất danh sách vi phạm Integrity ra file: {evidence_file}")