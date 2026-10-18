# Tài liệu Kỹ thuật REST API - Data Ingestion Module

## 1. Thông tin chung (General Information)
- **Base URL**: `http://localhost:8000`
- **Authentication**: Sử dụng API Key truyền qua Header `X-API-Key`.
- **Bảo mật Secret**: Biến môi trường quản lý là `MOCK_API_KEY` (mặc định: `training-key`). Tuyệt đối không hard-code hoặc in lộ giá trị thật trong log hay tài liệu (luôn mask thành `******`).

---

## 2. Tiêu chuẩn Headers & Mã lỗi chung

### Headers bắt buộc:
- `X-API-Key: ******`
- `Accept: application/json`[cite: 11]

### Các mã lỗi chuẩn (HTTP Status Codes):
- **`200 OK`**: Yêu cầu thành công, trả về dữ liệu JSON[cite: 13].
- **`400 Bad Request`**: Lỗi cú pháp hoặc tham số truyền vào không hợp lệ (Ví dụ: `updated_after` sai chuẩn ISO 8601 kèm message `{"detail": "updated_after must be ISO 8601"}`).
- **`401 Unauthorized`**: Thiếu hoặc sai `X-API-Key` kèm message `{"detail": "Invalid API key"}`.
- **`404 Not Found`**: Endpoint hoặc tài nguyên không tồn tại trên hệ thống[cite: 13].

---

## 3. Khảo sát 5 Endpoints Nghiệp vụ

Toàn bộ các endpoint dưới đây đều hỗ trợ cấu trúc phân trang (Pagination) và lọc gia tăng (Incremental Filtering).

### 3.1. Health Check
- **Endpoint**: `GET /health`
- **Authentication**: Không yêu cầu.
- **Response thành công (`200 OK`)**:
  ```json
  {
    "status": "ok"
  }

  