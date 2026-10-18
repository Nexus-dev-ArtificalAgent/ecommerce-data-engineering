# Báo cáo Kiểm thử Tính Bất biến (Idempotency Test Report)

## 1. Thông tin Kiểm thử
- **Đối tượng kiểm thử:** Bảng `core.orders` (600 bản ghi).
- **Mục tiêu:** Xác thực tính bất biến của dữ liệu khi thực thi nạp lặp lại nhiều lần, đảm bảo không sinh bản ghi trùng lặp (`count(*)` không đổi, `inserted = 0`, chuyển toàn bộ thành `updated`).

## 2. Kịch bản & Số liệu Nghiệm thu (Test Metrics)

| Lần chạy (Run) | Thao tác thực thi | Incoming | Inserted | Updated | SELECT COUNT(*) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Lần 1 (Cold Start)** | Nạp dữ liệu lần đầu tiên | 600 | 600[cite: 7] | 0[cite: 7] | 600 |
| **Lần 2 (Re-run)** | Nạp lại chính tập dữ liệu cũ | 600[cite: 7] | **0**[cite: 7] | **600**[cite: 7] | 600 |

## 3. Đối soát Tính toàn vẹn (Integrity Verification Queries)
Thực hiện các câu lệnh truy vấn SQL kiểm tra trên DBeaver[cite: 7]:

```sql
-- Kiểm tra tổng số dòng
SELECT COUNT(*) FROM core.orders; -- Kết quả: 600
-- Kiểm tra số khóa chính duy nhất
SELECT COUNT(DISTINCT order_id) FROM core.orders; -- Kết quả: 600

