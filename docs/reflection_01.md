**BÁO CÁO**

1. # **Khó khăn khi cài Docker/DBeaver và cách bạn xử lý?**

- Khó khăn duy nhất là không nhớ câu lệnh để setup trong Terminal, cách xử lý là sử dụng Gemini để giải quyết


2. # **Vì sao chọn data type như vậy cho tiền tệ / thời gian / ID? Cho 1 ví dụ cụ thể.**

Lý do chọn Data Type chuẩn trong thiết kế CSDL OLTP E-commerce:

* **Tiền tệ (NUMERIC / DECIMAL)**:  
  * *Lý do*:Tránh lỗi sai số làm tròn khi tính toán số thực của FLOAT/DOUBLE. Đảm bảo độ chính xác tuyệt đối cho báo cáo tài chính.  
  * *Ví dụ*: price NUMERIC(12, 2\) lưu giá tiền tối đa 999.999.999.999 với đúng 2 chữ số thập phân (VD: 150.00).  
* **Thời gian (TIMESTAMPTZ / TIMESTAMP WITH TIME ZONE)**:  
  * *Lý do*: Tự động chuyển đổi và lưu trữ mốc thời gian chuẩn UTC. Đảm bảo tính nhất quán khi người dùng, tài xế hoặc hệ thống ở các múi giờ khác nhau.  
  * *Ví dụ*: created\_at TIMESTAMP DEFAULT CURRENT\_TIMESTAMP lưu chính xác thời điểm đơn hàng khởi tạo.  
* **ID (BIGINT / UUID)**:  
  * *Lý do*: BIGINT dùng cho khóa chính tự tăng (Auto\_increment) giúp tối ưu hiệu năng ghi/đánh index và tiết kiệm dung lượng. UUID dùng khi cần định danh phân tán, bảo mật, tránh bị dò quét ID đơn hàng/người dùng.  
  * *Ví dụ*: customer\_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY cho bảng khách hàng.

3. # **Hiểu thế nào về quan hệ 1:N giữa customers và orders? Vẽ/kể ví dụ 1 customer có N orders.**

Hiểu về quan hệ 1:N (Customers \- Orders):

* **Một khách hàng (customers)** có thể thực hiện **nhiều đơn hàng (orders)** theo thời gian.  
* **Một đơn hàng (orders)** chỉ thuộc về **duy nhất một khách hàng**.  
* **Cách thể hiện:** Khóa chính customer\_id của bảng customers được đem sang làm **Khóa ngoại (Foreign Key)** tại bảng orders để liên kết.

Bảng customers (Khách hàng) 

| customer\_id | full\_name | email |
| :---- | :---- | :---- |
| 101 | Nguyễn Trọng Khôi | Nguyentrongkhoi0405@gmail.com |

Bảng orders (Đơn hàng của khách 101\) 

| order\_id | customer\_id (fk) | order\_date | total\_amount |
| :---- | :---- | :---- | :---- |
| ORD001 | 101 | 2026-03-01  | 250.00  |
| ORD002 | 101 | 2026-03-15 | 1,200.00  |
| ORD003 | 101 | 2026-04-02 | 450.00  |

4. # **Nếu schema cần sửa sau này (thêm cột, đổi FK), bạn sẽ xử lý thế nào (ALTER vs tạo lại)?**

**Sử dụng ALTER TABLE (Production / Đã có dữ liệu)**:

* **Lý do**: Bảo toàn dữ liệu hiện có, không làm gián đoạn dịch vụ và tuân thủ quy trình Migration (DDC/Schema Migration tools như Flyway, Liquibase, Alembic).

**Tạo lại DROP / CREATE TABLE (Local Development / Mới khởi tạo)**:

* **Lý do**: Nhanh gọn khi xây dựng bản dựng ban đầu (Dev/POC) và dữ liệu mẫu không quan trọng.  
* **Cách làm**: Chỉnh sửa trực tiếp file DDL gốc (01\_create\_oltp.sql), chạy docker compose down \-v để xóa volume cũ và tạo lại database sạch từ đầu.

