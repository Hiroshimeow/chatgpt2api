# Triển khai

## Docker

```bash
docker compose up -d
```

Xem log:

```bash
docker compose logs -f app
```

Dừng dịch vụ:

```bash
docker compose down
```

## Cấu hình

Các cấu hình quan trọng gồm khóa truy cập API, backend lưu trữ, URL database nếu dùng PostgreSQL, thông tin Git storage nếu dùng backend Git, và base URL public nếu cần tạo link ảnh hoặc callback.

## Dữ liệu runtime

Dữ liệu runtime nằm dưới `data/`. Không commit thư mục này.

## Cập nhật

1. Kiểm tra `git status`.
2. Kiểm tra upstream có commit mới không.
3. Đánh giá conflict với file local.
4. Pull/merge chỉ khi cần.
5. Chạy test tối thiểu trước khi deploy.
