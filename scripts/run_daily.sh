#!/usr/bin/env bash
set -euo pipefail

# Tự động xác định đường dẫn thư mục gốc dự án theo vị trí script
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Đảm bảo thư mục logs tồn tại
mkdir -p "$ROOT/logs"

# Định nghĩa tên file log theo ngày (VD: logs/pipeline_20261024.log)
LOG_FILE="$ROOT/logs/pipeline_$(date +%Y%m%d).log"

echo "==================================================" >> "$LOG_FILE"
echo "=== Bắt đầu chạy pipeline tự động: $(date) ===" >> "$LOG_FILE"
echo "==================================================" >> "$LOG_FILE"

# Tự động tìm đúng đường dẫn Python trong thư mục ảo .venv (Hỗ trợ WSL, Git Bash, Windows, Linux/macOS)
if [ -f "$ROOT/.venv/Scripts/python.exe" ]; then
    PYTHON_CMD="$ROOT/.venv/Scripts/python.exe"
elif [ -f "$ROOT/.venv/Scripts/python" ]; then
    PYTHON_CMD="$ROOT/.venv/Scripts/python"
elif [ -f "$ROOT/.venv/bin/python" ]; then
    PYTHON_CMD="$ROOT/.venv/bin/python"
else
    PYTHON_CMD="python"
fi

echo "Sử dụng Python tại: $PYTHON_CMD" >> "$LOG_FILE"

# Thực thi lệnh pipeline bằng đúng Python của venv, ghi log đồng thời ra file và hiển thị ra màn hình
"$PYTHON_CMD" -m src.pipeline --source both --input-dir data/incremental/day_2026-07-01 --refresh-mart 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

echo "==================================================" >> "$LOG_FILE"
echo "=== Kết thúc chạy pipeline | Exit Code: $EXIT_CODE | Thời gian: $(date) ===" >> "$LOG_FILE"
echo "==================================================" >> "$LOG_FILE"

exit $EXIT_CODE