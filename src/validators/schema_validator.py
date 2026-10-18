import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Định nghĩa Data Contract (Cột cấu trúc bắt buộc & Trường giá trị bắt buộc) cho 5 bảng
SCHEMA_CONTRACT = {
    "customers": {
        "required_columns": ["customer_id", "full_name", "email", "status"],
        "required_values": ["customer_id", "full_name", "email"]
    },
    "products": {
        "required_columns": ["product_id", "product_name", "price", "category_id"],
        "required_values": ["product_id", "product_name", "price"]
    },
    "orders": {
        "required_columns": ["order_id", "customer_id", "order_date", "status", "order_total"],
        "required_values": ["order_id", "customer_id", "order_date"]
    },
    "order_items": {
        "required_columns": ["order_item_id", "order_id", "product_id", "quantity", "unit_price"],
        "required_values": ["order_item_id", "order_id", "product_id", "quantity"]
    },
    "payments": {
        "required_columns": ["payment_id", "order_id", "amount", "payment_date", "payment_status"],
        "required_values": ["payment_id", "order_id", "amount", "payment_date"]
    }
}

def validate_schema(dataset_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    1. Kiểm tra danh sách cột bắt buộc (REQUIRED). Thiếu cấu trúc -> raise ValueError.
    2. Kiểm tra missing value (NULL, NaN, hoặc chuỗi rỗng/khoảng trắng) ở REQUIRED_VALUES.
    3. Tính điểm chất lượng từng dòng (row scoring): Tỷ lệ các trường hợp lệ (0-100%).
    """
    if dataset_name not in SCHEMA_CONTRACT:
        raise ValueError(f"Unknown dataset: {dataset_name}")
        
    contract = SCHEMA_CONTRACT[dataset_name]
    required_cols = contract["required_columns"]
    required_vals = contract["required_values"]
    
    # Yêu cầu 1: Kiểm tra cột cấu trúc (Schema Mismatch)
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"SCHEMA MISMATCH [{dataset_name}]: Thiếu các cột bắt buộc: {missing_cols}")
        
    df_checked = df.copy()
    scores = []
    error_lists = []
    
    # Yêu cầu 2 & 3: Kiểm tra completeness và chấm điểm row scoring
    for idx, row in df_checked.iterrows():
        row_errors = []
        valid_count = 0
        for col in required_vals:
            val = row.get(col)
            is_missing = False
            
            # Xử lý các dạng thiếu: None, NaN, hoặc chuỗi chỉ chứa khoảng trắng
            if pd.isna(val):
                is_missing = True
            elif isinstance(val, str) and val.strip() == "":
                is_missing = True
            
            if is_missing:
                row_errors.append("MISSING_REQUIRED")
            else:
                valid_count += 1
        
        # Tính tỷ lệ hợp lệ (0 - 100%)
        score = round((valid_count / len(required_vals)) * 100, 2) if len(required_vals) > 0 else 100.0
        scores.append(score)
        error_lists.append(row_errors if row_errors else ["OK"])
        
    df_checked["quality_score"] = scores
    df_checked["schema_errors"] = error_lists
    return df_checked


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    
    dirty_dir = Path("data/dirty/day_2026-07-02")
    evidence_dir = Path("docs/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    # Map tên dataset chuẩn với tên file thực tế có hậu tố _daily
    dataset_file_mapping = {
        "customers": "customers_daily.csv",
        "products": "products_daily.csv",
        "orders": "orders_daily.csv",
        "order_items": "order_items_daily.csv",
        "payments": "payments_daily"
    }
    
    output_lines = []
    
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
            
        logger.info(f"Đang kiểm tra Schema & Completeness cho bảng: {dataset} từ file {file_path.name} ({len(df)} dòng)")
        
        output_lines.append(f"=== DATASET: {dataset} ===")
        try:
            validated_df = validate_schema(dataset, df)
            id_col = SCHEMA_CONTRACT[dataset]["required_columns"][0]
            
            for i in range(min(10, len(validated_df))):
                row_id = validated_df.iloc[i].get(id_col, f"ROW_{i}")
                score = validated_df.iloc[i]["quality_score"]
                errors = validated_df.iloc[i]["schema_errors"]
                line = f"row_id={row_id} score={score} errors={errors}"
                output_lines.append(line)
        except ValueError as e:
            logger.error(str(e))
            output_lines.append(f"ERROR: {str(e)}")
        output_lines.append("")
        
    evidence_file = evidence_dir / "07-schema.txt"
    evidence_file.write_text("\n".join(output_lines), encoding="utf-8")
    logger.info(f"Đã xuất log minh chứng ra file: {evidence_file}")