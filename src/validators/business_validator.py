import pandas as pd
import re
from pathlib import Path
import logging
from collections import Counter

logger = logging.getLogger(__name__)

# Danh sách Enum chuẩn cho các cột
ALLOWED_ENUMS = {
    "status": ["active", "inactive", "pending", "completed", "cancelled"],
    "channel": ["web", "mobile", "store", "partner"],
    "payment_method": ["credit_card", "e_wallet", "bank_transfer", "cod"],
    "payment_status": ["pending", "completed", "failed", "refunded"]
}

EMAIL_REGEX = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'

def validate_row_business_rules(name: str, row: pd.Series) -> list:
    """
    Kiểm tra các Business Rules cấp dòng cho từng dataset. Trả về danh sách các mã lỗi.
    """
    errors = []

    # 1. Email check (cho bảng customers)
    if "email" in row and pd.notna(row["email"]):
        email_str = str(row["email"]).strip()
        if not re.match(EMAIL_REGEX, email_str):
            errors.append("INVALID_EMAIL")

    # 2. Enum check (status, channel, payment_method, payment_status)
    for col, allowed_vals in ALLOWED_ENUMS.items():
        if col in row and pd.notna(row[col]):
            val_str = str(row[col]).strip().lower()
            if val_str not in allowed_vals:
                errors.append(f"INVALID_{col.upper()}")

    # 3. Range check
    # unit_price >= 0
    if "unit_price" in row and pd.notna(row["unit_price"]):
        try:
            if float(row["unit_price"]) < 0:
                errors.append("NEGATIVE_PRICE")
        except ValueError:
            errors.append("INVALID_PRICE_TYPE")

    # quantity > 0
    if "quantity" in row and pd.notna(row["quantity"]):
        try:
            if float(row["quantity"]) <= 0:
                errors.append("INVALID_QUANTITY")
        except ValueError:
            errors.append("INVALID_QUANTITY_TYPE")

    # order_total >= 0
    if "order_total" in row and pd.notna(row["order_total"]):
        try:
            if float(row["order_total"]) < 0:
                errors.append("NEGATIVE_ORDER_TOTAL")
        except ValueError:
            errors.append("INVALID_ORDER_TOTAL_TYPE")

    # amount >= 0
    if "amount" in row and pd.notna(row["amount"]):
        try:
            if float(row["amount"]) < 0:
                errors.append("NEGATIVE_AMOUNT")
        except ValueError:
            errors.append("INVALID_AMOUNT_TYPE")

    # discount_amount >= 0
    if "discount_amount" in row and pd.notna(row["discount_amount"]):
        try:
            if float(row["discount_amount"]) < 0:
                errors.append("NEGATIVE_DISCOUNT")
        except ValueError:
            errors.append("INVALID_DISCOUNT_TYPE")

    # 4. Consistency check: discount_amount <= quantity * unit_price
    if "discount_amount" in row and "quantity" in row and "unit_price" in row:
        if (
            pd.notna(row["discount_amount"])
            and pd.notna(row["quantity"])
            and pd.notna(row["unit_price"])
        ):
            try:
                disc = float(row["discount_amount"])
                qty = float(row["quantity"])
                u_price = float(row["unit_price"])
                gross = qty * u_price
                if disc > gross:
                    errors.append("DISCOUNT_EXCEEDS_GROSS")
            except ValueError:
                pass

    return errors


def split_valid_invalid(name: str, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Kiểm tra các quy tắc cấp dòng (row-level rules), tách DataFrame thành (valid_df, rejected_df).
    Bảng rejected_df có thêm cột error_code (nối bằng dấu '|' nếu có nhiều lỗi).
    """
    df_copy = df.copy()
    valid_mask = []
    error_codes = []

    for _, row in df_copy.iterrows():
        row_errors = validate_row_business_rules(name, row)
        if len(row_errors) == 0:
            valid_mask.append(True)
            error_codes.append("")
        else:
            valid_mask.append(False)
            error_codes.append("|".join(row_errors))

    df_copy["error_code"] = error_codes

    valid_df = df_copy[valid_mask].drop(columns=["error_code"])
    rejected_df = df_copy[~pd.Series(valid_mask, index=df_copy.index)].copy()

    return valid_df, rejected_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    dirty_dir = Path("data/dirty/day_2026-07-02")
    evidence_dir = Path("docs/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    dataset_file_mapping = {
        "customers": "customers_daily.csv",
        "products": "products_daily.csv",
        "orders": "orders_daily.csv",
        "order_items": "order_items_daily.csv",
        "payments": "payments_daily",
    }

    global_error_counter = Counter()

    for dataset, filename in dataset_file_mapping.items():
        file_path = dirty_dir / filename

        if not file_path.exists():
            matches = list(dirty_dir.glob(f"{dataset}*"))
            if matches:
                file_path = matches[0]
            else:
                logger.warning(f"Không tìm thấy file dữ liệu cho dataset: {dataset}")
                continue

        df = None
        if file_path.suffix.lower() == ".csv":
            df = pd.read_csv(file_path)
        else:
            try:
                df = pd.read_json(file_path)
            except Exception:
                import json
                data = json.loads(file_path.read_text(encoding="utf-8"))
                df = pd.DataFrame(data)

        logger.info(f"Đang kiểm tra Business Rules cho bảng: {dataset} ({len(df)} dòng)")

        try:
            valid_df, rejected_df = split_valid_invalid(dataset, df)
            logger.info(
                f"  --> {dataset}: Valid={len(valid_df)}, Rejected={len(rejected_df)}"
            )

            # Thống kê số lượng vi phạm từng lỗi
            for err_string in rejected_df["error_code"]:
                individual_errors = err_string.split("|")
                for err in individual_errors:
                    if err:
                        global_error_counter[err] += 1

        except Exception as e:
            logger.error(f"Lỗi khi xử lý dataset {dataset}: {str(e)}")

    # Xuất minh chứng dạng per-rule count vào docs/evidence/07-business.txt
    evidence_lines = []
    for err_code, count in global_error_counter.most_common():
        evidence_lines.append(f"{err_code}: {count}")

    evidence_file = evidence_dir / "07-business.txt"
    evidence_file.write_text(", ".join(evidence_lines), encoding="utf-8")
    logger.info(f"Đã xuất minh chứng per-rule ra file: {evidence_file}")