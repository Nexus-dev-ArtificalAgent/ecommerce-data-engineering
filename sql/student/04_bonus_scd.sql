-- ==========================================
-- PHẦN 2.1: SCD TYPE 2 CHO dim_product
-- ==========================================

-- Tạo bảng dim_product_scd2 quản lý lịch sử thay đổi giá
create table if not exists dim_product_scd2 (
	product_key serial primary key, 
	product_id varchar(50) not null, 
	product_name varchar(255) not null, 
	category varchar(100),
	unit_price numeric(12,2) not null, 
	valid_from timestamp not null,  
	valid_to timestamp, 
	is_current boolean not null 
); 

-- 1. Insert dữ liệu ban đầu (ví dụ sản phẩm ID 'P001' giá cũ 100k)
insert into dim_product_scd2 (product_id, product_name, category, unit_price, valid_from, valid_to, is_current)
values ('P001', 'Áo thun Polo', 'Thời trang', 100000.00, '2026-01-01 00:00:00', NULL, TRUE);

-- 2. Kịch bản DEMO khi sản phẩm thay đổi giá lên 120k vào ngày '2026-06-01':
-- Bước A: Đóng phiên bản cũ (set is_current = FALSE và cập nhật valid_to)
UPDATE dim_product_scd2 
SET valid_to = '2026-06-01 00:00:00', 
    is_current = FALSE
WHERE product_id = 'P001' AND is_current = TRUE;

-- Bước B: Insert phiên bản mới với giá mới (is_current = TRUE)
INSERT INTO dim_product_scd2 (product_id, product_name, category, unit_price, valid_from, valid_to, is_current)
VALUES ('P001', 'Áo thun Polo', 'Thời trang', 120000.00, '2026-06-01 00:00:00', NULL, TRUE);

select * from dim_product_scd2; 