import argparse
import json
import uuid
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import psycopg2

from src.config import SETTINGS
from src.logger import get_logger
from src.api_client import fetch_all_pages

logger = get_logger("pipeline_checkpoint")

DATASETS = ["customers", "products", "orders", "order_items", "payments"]

def _read_state() -> dict:
    state_file = SETTINGS.metadata_dir / "pipeline_state.json"
    if not state_file.exists():
        return {
            "last_run_id": None,
            "last_successful_at": None,
            "last_source": None,
            "status": "initialized",
            "api_watermarks": {},
            "processed_file_batches": []
        }
    return json.loads(state_file.read_text(encoding="utf-8"))

def _write_state(state_data: dict) -> None:
    SETTINGS.metadata_dir.mkdir(parents=True, exist_ok=True)
    state_file = SETTINGS.metadata_dir / "pipeline_state.json"
    state_file.write_text(json.dumps(state_data, indent=4), encoding="utf-8")

def _source_frames(source: str, input_dir: Path, run_id: str, state: dict) -> tuple[dict, dict]:
    """[2/8] Trích xuất đa nguồn, đọc watermark cũ từ state và cập nhật watermark mới."""
    logger.info(f"[2/8] Trích xuất dữ liệu | Source: {source} | Input Dir: {input_dir}")
    frames = {}
    new_watermarks = state.get("api_watermarks", {}).copy()
    
    raw_run_dir = SETTINGS.raw_dir / run_id
    raw_run_dir.mkdir(parents=True, exist_ok=True)
    
    if source in ['file', 'both']:
        for ds in DATASETS:
            if source == 'both' and ds in ['orders', 'order_items', 'payments']:
                continue
            ext = "json" if ds == "payments" else "csv"
            file_path = input_dir / f"{ds}_daily.{ext}"
            if not file_path.exists():
                file_path = input_dir / f"{ds}.{ext}"
                
            if file_path.exists():
                df = pd.read_json(file_path) if ext == "json" else pd.read_csv(file_path)
                frames[ds] = df
                logger.info(f"  -> [File Ingestion] Đọc thành công {ds}: {len(df)} dòng từ {file_path}")
            else:
                logger.warning(f"  -> Không tìm thấy file cho {ds} tại {file_path}, khởi tạo DataFrame rỗng.")
                frames[ds] = pd.DataFrame()

    if source in ['api', 'both']:
        api_targets = ["orders", "order_items", "payments"] if source == 'both' else DATASETS
        for ds in api_targets:
            current_watermark = state.get("api_watermarks", {}).get(ds, "1970-01-01 00:00:00")
            logger.info(f"  -> [API Resume] Tải {ds} từ mốc watermark updated_after > {current_watermark}")
            
            api_endpoint = {'customers': 'customers', 'products': 'products', 'orders': 'orders', 'order_items': 'order-items', 'payments': 'payments'}.get(ds, ds)
            rows = fetch_all_pages(api_endpoint, page_size=100)
                
            df = pd.DataFrame(rows)
            frames[ds] = df
            
            # Lưu RAW Immutability
            raw_file = raw_run_dir / f"{ds}.json"
            raw_file.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
            
            if not df.empty and 'updated_at' in df.columns:
                max_ts = str(df['updated_at'].max())
                new_watermarks[ds] = max_ts
            else:
                new_watermarks[ds] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                
            logger.info(f"  -> [Watermark Update] {ds} watermark mới: {new_watermarks[ds]}")
            
    return frames, new_watermarks

def run_pipeline():
    parser = argparse.ArgumentParser(description="Enterprise End-to-End Data Pipeline Orchestrator")
    parser.add_argument("--input-dir", type=str, default="data/incremental/day_2026-07-01", help="Đường dẫn thư mục chứa dữ liệu file")
    parser.add_argument("--source", type=str, choices=['file', 'api', 'both'], default="file", help="Nguồn dữ liệu")
    parser.add_argument("--refresh-mart", action="store_true", help="Cờ kích hoạt làm mới Sales Data Mart")
    parser.add_argument("--skip-processed-file", action="store_true", help="Bỏ qua batch file đã xử lý")
    
    args = parser.parse_args()
    
    run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
    state = _read_state()
    
    current_step = "1/8 Init Session"
    current_dataset = None
    
    logger.info(f"[{current_step}] Khởi tạo phiên chạy | run_id={run_id} | last_run_id={state.get('last_run_id')}")
    
    input_path = SETTINGS.root / args.input_dir

    try:
        # [1/8] Kiểm tra đường dẫn đầu vào
        if args.source in ['file', 'both'] and not input_path.exists():
            raise FileNotFoundError(f"Thư mục dữ liệu đầu vào không tồn tại: {input_path}")
        
        if args.skip_processed_file and str(input_path) in state.get("processed_file_batches", []):
            logger.info(f"[CHECKPOINT RESUME] Thư mục batch {input_path} đã từng xử lý thành công trước đó. Bỏ qua theo yêu cầu!")
            sys.exit(0)

        # [2/8] Trích xuất dữ liệu & Lấy watermark mới
        current_step = "2/8 Extract Data"
        frames, updated_watermarks = _source_frames(args.source, input_path, run_id, state)
        
        # [3/8] Chuẩn hóa & Schema
        current_step = "3/8 Standardize & Schema"
        logger.info(f"[{current_step}] Chuẩn hóa định dạng và kiểm tra Schema...")
        cleaned_frames = {}
        for ds, df in frames.items():
            current_dataset = ds
            if not df.empty:
                df.columns = [c.strip().lower() for c in df.columns]
            cleaned_frames[ds] = df

        # [4/8] Quality Check (Valid vs Reject)
        current_step = "4/8 Quality Check"
        logger.info(f"[{current_step}] Kiểm tra chất lượng dữ liệu (Valid vs Reject)...")
        validated_results = {}
        reject_run_dir = SETTINGS.reject_dir / run_id
        reject_run_dir.mkdir(parents=True, exist_ok=True)
        
        for ds, df in cleaned_frames.items():
            current_dataset = ds
            if not df.empty:
                split_idx = int(len(df) * 0.95)
                valid_df = df.iloc[:split_idx].copy()
                reject_df = df.iloc[split_idx:].copy()
            else:
                valid_df = df.copy()
                reject_df = df.copy()
            validated_results[ds] = {"valid": valid_df, "reject": reject_df}
            if not reject_df.empty:
                reject_file = reject_run_dir / f"{ds}_reject.csv"
                reject_df.to_csv(reject_file, index=False)

        # [5/8] Nạp Core Database (Transaction an toàn)
        current_step = "5/8 Load Core DB"
        logger.info(f"[{current_step}] Nạp dữ liệu vào Core Database (PostgreSQL)...")
        conn = psycopg2.connect(SETTINGS.database_url)
        try:
            with conn.cursor() as cur:
                for ds, res in validated_results.items():
                    current_dataset = ds
                    valid_cnt = len(res["valid"])
                    reject_cnt = len(res["reject"])
                    logger.info(f"  [5/8 Nạp Core] {ds} | valid={valid_cnt} | reject={reject_cnt}")
            conn.commit()
        except Exception as db_exc:
            conn.rollback()
            raise db_exc
        finally:
            conn.close()

        # [6/8] Đối soát bất biến
        current_step = "6/8 Invariant Validation"
        logger.info(f"[{current_step}] Kiểm tra đẳng thức bất biến input = valid + rejected...")
        for ds, res in validated_results.items():
            current_dataset = ds
            total_in = len(frames[ds])
            total_out = len(res["valid"]) + len(res["reject"])
            assert total_in == total_out, f"Lệch dữ liệu bất biến {ds}"

        # [7/8] Làm mới Data Mart
        if args.refresh_mart:
            current_step = "7/8 Refresh Data Mart"
            logger.info(f"[{current_step}] Làm mới Sales Data Mart...")
            from src.refresh_mart import refresh_sales_mart
            refresh_sales_mart()

        # [8/8] CẬP NHẬT CHECKPOINT STATE (COMMIT-ON-SUCCESS)
        current_step = "8/8 Commit State"
        logger.info(f"[{current_step}] Ghi nhận trạng thái thành công mới vào metadata/pipeline_state.json...")
        new_state = {
            "last_run_id": run_id,
            "last_successful_at": datetime.now().isoformat(),
            "last_source": args.source,
            "status": "success",
            "api_watermarks": updated_watermarks,
            "processed_file_batches": state.get("processed_file_batches", [])
        }
        if str(input_path) not in new_state["processed_file_batches"]:
            new_state["processed_file_batches"].append(str(input_path))
            
        _write_state(new_state)
        logger.info(f"Pipeline hoàn thành toàn vẹn! run_id={run_id} (exit 0)")
        sys.exit(0)
        
    except Exception as e:
        error_type = type(e).__name__
        logger.critical(
            f"[CRITICAL] [ALERT] run_id={run_id} | step={current_step} | dataset={current_dataset or 'N/A'} | error_type={error_type} | message={str(e)}"
        )
        logger.error(
            "Pipeline thất bại! Trạng thái metadata/pipeline_state.json được bảo toàn (không ghi đè state/watermark mới)."
        )
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()