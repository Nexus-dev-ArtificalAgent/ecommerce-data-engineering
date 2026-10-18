import pandas as pd
import json
from pathlib import Path
import logging

from src.validators.business_validator import split_valid_invalid
from src.validators.integrity_validator import split_cross_table_invalid

logger = logging.getLogger(__name__)

def generate_quality_report():
    dirty_dir = Path("data/dirty/day_2026-07-02")
    evidence_dir = Path("docs/evidence")
    reports_dir = Path("reports")
    
    evidence_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    dataset_file_mapping = {
        "categories": "categories_daily.csv",
        "customers": "customers_daily.csv",
        "products": "products_daily.csv",
        "orders": "orders_daily.csv",
        "order_items": "order_items_daily.csv",
        "payments": "payments_daily",
    }

    # 1. Load tất cả raw datasets
    raw_datasets = {}
    for ds_name, filename in dataset_file_mapping.items():
        file_path = dirty_dir / filename
        if not file_path.exists():
            matches = list(dirty_dir.glob(f"{ds_name}*"))
            if matches:
                file_path = matches[0]
            else:
                continue

        if file_path.suffix.lower() == ".csv":
            raw_datasets[ds_name] = pd.read_csv(file_path)
        else:
            try:
                raw_datasets[ds_name] = pd.read_json(file_path)
            except Exception:
                import json as js
                data = js.loads(file_path.read_text(encoding="utf-8"))
                raw_datasets[ds_name] = pd.DataFrame(data)

    if "categories" not in raw_datasets:
        raw_datasets["categories"] = pd.DataFrame({"category_id": ["CAT001", "CAT002", "CAT003"]})

    report_data = []
    invariant_logs = []

    # Danh sách các bảng cần tổng hợp DQ Report
    target_datasets = ["customers", "products", "orders", "order_items", "payments"]

    for ds_name in target_datasets:
        if ds_name not in raw_datasets:
            continue

        df_raw = raw_datasets[ds_name]
        input_count = len(df_raw)

        # Chạy Business Rules Validation
        v_biz, r_biz = split_valid_invalid(ds_name, df_raw)

        # Chạy Cross-Table Integrity & Chronology Validation trên dữ liệu đã qua lọc Business Rules
        v_final, r_integ, _ = split_cross_table_invalid(ds_name, v_biz, raw_datasets)

        valid_count = len(v_final)
        # Tổng số bị reject = Số bị reject ở Business Rules + Số bị reject ở Integrity Check
        rejected_count = len(r_biz) + len(r_integ)

        # 3. Kiểm tra nguyên tắc bất biến (Invariant Check: Input = Valid + Rejected)
        assert input_count == valid_count + rejected_count, (
            f"INVARIANT VIOLATED [{ds_name}]: Input ({input_count}) != Valid ({valid_count}) + Rejected ({rejected_count})"
        )

        log_msg = f"{ds_name}: {input_count} = {valid_count} + {rejected_count} OK"
        logger.info(f"  [INVARIANT CHECK] {log_msg}")
        invariant_logs.append(log_msg)

        report_data.append({
            "dataset": ds_name,
            "input": input_count,
            "valid": valid_count,
            "rejected": rejected_count
        })

    # 2. Xuất báo cáo ra CSV & JSON
    report_df = pd.DataFrame(report_data)
    csv_file = reports_dir / "data_quality_report.csv"
    report_df.to_csv(csv_file, index=False)
    logger.info(f"Đã xuất báo cáo CSV ra file: {csv_file}")

    json_file = reports_dir / "data_quality_summary.json"
    json_summary = {
        "summary": report_data,
        "total_datasets": len(report_data),
        "total_input": int(report_df["input"].sum()),
        "total_valid": int(report_df["valid"].sum()),
        "total_rejected": int(report_df["rejected"].sum())
    }
    json_file.write_text(json.dumps(json_summary, indent=2), encoding="utf-8")
    logger.info(f"Đã xuất báo cáo JSON ra file: {json_file}")

    # Xuất log minh chứng Invariant Reconciliation
    evidence_file = evidence_dir / "07-invariant.txt"
    evidence_file.write_text("\n".join(invariant_logs), encoding="utf-8")
    logger.info(f"Đã xuất log minh chứng Invariant ra file: {evidence_file}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger.info("Bắt đầu tổng hợp Data Quality Report & Kiểm tra Invariant...")
    generate_quality_report()